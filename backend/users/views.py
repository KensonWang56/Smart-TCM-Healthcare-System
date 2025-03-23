from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.utils import timezone
import os
import time
import base64
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import torch
import pickle
import logging
import random
import string

# 设置日志
logger = logging.getLogger(__name__)

# 导入人脸识别模型（假设模型文件放在backend/face_recognition目录下）
try:
    from face_recognition.model import FaceRecognitionModel
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning("警告：人脸识别模型未找到，相关功能将被禁用")

from .serializers import (
    UserSerializer, 
    UserRegisterSerializer, 
    PasswordChangeSerializer,
    UserUpdateSerializer
)

User = get_user_model()

# 初始化人脸识别模型
face_model = None
if FACE_RECOGNITION_AVAILABLE:
    try:
        DB_CONFIG = {
            'host': 'localhost',
            'user': settings.DATABASES['default']['USER'],
            'password': settings.DATABASES['default']['PASSWORD'],
            'database': settings.DATABASES['default']['NAME']
        }
        face_model = FaceRecognitionModel(DB_CONFIG)
        print("人脸识别模型初始化成功")
    except Exception as e:
        print(f"人脸识别模型初始化失败: {str(e)}")

# 人脸识别函数
def recognize_face(face_image):
    """
    对上传的人脸图像进行识别，返回匹配的用户列表和相似度
    
    Args:
        face_image: 上传的人脸图像文件
        
    Returns:
        列表[tuple]: 包含(用户名,相似度)的列表，如果未检测到人脸则返回None
    """
    if not FACE_RECOGNITION_AVAILABLE or face_model is None:
        logger.error("人脸识别模型不可用")
        return None
    
    try:
        # 读取图像
        image = Image.open(face_image)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 进行人脸识别
        results = face_model.recognize_face(image)
        
        if not results:
            logger.warning("未检测到人脸")
            return None
        
        # 处理识别结果
        recognized_users = []
        for name, similarity in results:
            if name != "未知":
                # 转换为百分比并保留两位小数
                similarity_percent = round(similarity * 100, 2)
                recognized_users.append((name, similarity_percent))
        
        return recognized_users
        
    except Exception as e:
        logger.error(f"人脸识别处理错误: {str(e)}")
        return None

class RegisterView(APIView):
    """用户注册视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # 创建Token
            refresh = RefreshToken.for_user(user)
            response_data = {
                'code': 200,
                'message': '注册成功',
                'data': {
                    'token': str(refresh.access_token),
                    'refresh': str(refresh),
                    'username': user.username
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response({'code': 400, 'message': '注册失败', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """用户登录视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'code': 400, 'message': '用户名和密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # 更新最后登录时间
            user.update_last_login()
            
            # 创建Token
            refresh = RefreshToken.for_user(user)
            response_data = {
                'code': 200,
                'message': '登录成功',
                'data': {
                    'token': str(refresh.access_token),
                    'refresh': str(refresh),
                    'username': user.username
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'code': 401, 'message': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)

class FaceLoginView(APIView):
    """人脸登录视图"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            # 获取上传的人脸图片
            face_image = request.FILES.get('face_image')
            if not face_image:
                return Response({
                    'code': 400,
                    'message': '未上传人脸图片'
                })

            # 人脸识别
            recognize_result = recognize_face(face_image)
            if recognize_result is None:
                return Response({
                    'code': 404,
                    'message': '未检测到人脸，请确保光线充足并正对摄像头'
                })

            # 根据识别结果查找用户
            recognized_users = []
            for name, similarity in recognize_result:
                try:
                    user = User.objects.get(username=name)
                    # 为每个匹配的用户生成token
                    refresh = RefreshToken.for_user(user)
                    token = str(refresh.access_token)
                    recognized_users.append({
                        'username': user.username, # 使用数据库中的当前用户名
                        'similarity': similarity,
                        'token': token
                    })
                except User.DoesNotExist:
                    logger.warning(f"找到匹配的人脸，但用户名{name}在系统中不存在")
                    pass

            if len(recognized_users) == 0:
                return Response({
                    'code': 404,
                    'message': '未找到匹配的用户，请先注册或使用用户名密码登录'
                })

            # 返回所有匹配到的用户信息
            return Response({
                'code': 300,
                'message': '找到多个匹配的用户',
                'data': {
                    'users': recognized_users
                }
            })

        except Exception as e:
            logger.error(f"人脸登录错误: {str(e)}")
            return Response({
                'code': 500,
                'message': '人脸识别服务暂时不可用，请稍后再试或使用其他登录方式'
            })

class UserInfoView(APIView):
    """获取和更新用户信息"""
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({
            'code': 200,
            'message': '获取用户信息成功',
            'data': serializer.data
        })
    
    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'message': '更新用户信息成功',
                'data': UserSerializer(request.user).data
            })
        return Response({'code': 400, 'message': '更新用户信息失败', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    """修改密码"""
    
    def put(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            # 验证旧密码
            if not request.user.check_password(serializer.validated_data['old_password']):
                return Response({'code': 400, 'message': '当前密码错误'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 设置新密码
            request.user.set_password(serializer.validated_data['new_password'])
            # 如果用户之前需要修改密码，修改该标志
            if request.user.need_change_password:
                request.user.need_change_password = False
            request.user.save()
            
            return Response({'code': 200, 'message': '密码修改成功'})
        return Response({'code': 400, 'message': '密码修改失败', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class AvatarUploadView(APIView):
    """上传用户头像"""
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        avatar = request.FILES.get('file')
        
        if not avatar:
            return Response({'code': 400, 'message': '未提供头像图片'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 生成唯一文件名
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        filename = f"{random_str}.jpg"
        avatar_path = os.path.join(settings.AVATAR_DIR, filename)
        
        # 保存头像
        try:
            with open(avatar_path, 'wb+') as destination:
                for chunk in avatar.chunks():
                    destination.write(chunk)
            
            # 更新用户头像路径
            request.user.avatar = f"/media/avatars/{filename}"
            request.user.save()
            
            return Response({
                'code': 200,
                'message': '头像上传成功',
                'data': {
                    'avatarUrl': request.user.avatar
                }
            })
        except Exception as e:
            return Response({'code': 500, 'message': f'头像上传失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FaceUploadView(APIView):
    """上传人脸图片"""
    parser_classes = [MultiPartParser, FormParser]
    
    def put(self, request):
        if not FACE_RECOGNITION_AVAILABLE or face_model is None:
            return Response({'code': 500, 'message': '人脸识别服务不可用'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        face_image = request.FILES.get('file')
        
        if not face_image:
            # 处理base64编码的图片数据
            face_data = request.data.get('image')
            if face_data and isinstance(face_data, str) and face_data.startswith('data:image'):
                # 解析base64
                format, imgstr = face_data.split(';base64,')
                ext = format.split('/')[-1]
                face_image = BytesIO(base64.b64decode(imgstr))
            else:
                return Response({'code': 400, 'message': '未提供人脸图片'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 生成唯一文件名（使用时间戳）
        timestamp = int(time.time())
        filename = f"{request.user.username}_{timestamp}.jpg"
        face_path = os.path.join(settings.FACE_DIR, filename)
        
        # 保存人脸图片
        try:
            # 首先检查用户是否已有人脸数据
            has_face_before = request.user.has_face
            old_face_path = None
            
            if has_face_before and request.user.face_image:
                # 记录旧的人脸图片路径，之后会删除
                old_face_path = os.path.join(settings.MEDIA_ROOT, request.user.face_image.lstrip('/media/'))
            
            # 保存新上传的人脸图片
            if isinstance(face_image, BytesIO):
                # 处理base64解码的图片
                img = Image.open(face_image)
                img.save(face_path, 'JPEG')
            else:
                # 处理上传的文件
                with open(face_path, 'wb+') as destination:
                    for chunk in face_image.chunks():
                        destination.write(chunk)
            
            # 将人脸添加到人脸识别模型（内部已处理更新操作）
            success = face_model.add_face(face_path, request.user.username)
            
            if not success:
                # 如果添加失败，删除刚刚保存的新照片
                if os.path.exists(face_path):
                    os.remove(face_path)
                return Response({'code': 400, 'message': '人脸图片中未检测到有效人脸'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 成功添加到模型后，删除旧的照片文件（如果有）
            if old_face_path and os.path.exists(old_face_path):
                try:
                    os.remove(old_face_path)
                    logger.info(f"删除旧人脸图片: {old_face_path}")
                except Exception as e:
                    logger.warning(f"删除旧人脸图片失败: {old_face_path}, 错误: {str(e)}")
            
            # 更新用户人脸图片路径和标志
            request.user.face_image = f"/media/faces/{filename}"
            request.user.has_face = True
            request.user.save()
            
            return Response({
                'code': 200,
                'message': '人脸图片上传成功',
                'data': {
                    'faceImage': request.user.face_image
                }
            })
        except Exception as e:
            logger.error(f"人脸图片上传失败: {str(e)}")
            # 清理临时文件
            if os.path.exists(face_path):
                try:
                    os.remove(face_path)
                except:
                    pass
            return Response({'code': 500, 'message': f'人脸图片上传失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        """删除人脸图片"""
        if request.user.face_image:
            try:
                # 获取文件路径
                face_path = os.path.join(settings.MEDIA_ROOT, request.user.face_image.lstrip('/media/'))
                
                # 如果文件存在则删除
                if os.path.exists(face_path):
                    os.remove(face_path)
                
                # 从人脸识别模型中移除用户人脸数据
                if FACE_RECOGNITION_AVAILABLE and face_model is not None:
                    try:
                        success = face_model.remove_face(request.user.username)
                        if not success:
                            logger.warning(f"从人脸识别模型中移除用户 {request.user.username} 的人脸数据失败")
                    except Exception as e:
                        logger.error(f"移除用户人脸数据时出错: {str(e)}")
                
                # 更新用户信息
                request.user.face_image = None
                request.user.has_face = False
                request.user.save()
                
                return Response({'code': 200, 'message': '人脸图片删除成功'})
            except Exception as e:
                logger.error(f"删除用户人脸图片失败: {str(e)}")
                return Response({'code': 500, 'message': f'人脸图片删除失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'code': 400, 'message': '用户未设置人脸图片'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """用户退出登录视图"""
    
    def post(self, request):
        # 对于JWT令牌系统，服务器端不需要额外操作，客户端负责删除本地令牌
        # 但可以添加一些日志记录或其他逻辑
        return Response({
            'code': 200,
            'message': '退出登录成功'
        }, status=status.HTTP_200_OK) 