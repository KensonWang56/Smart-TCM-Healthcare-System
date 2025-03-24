from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
import io
import logging
from sparkai.llm.llm import ChatSparkLLM
from sparkai.core.messages import BaseMessage, ChatMessage
import torch
import torchvision.transforms as transforms
import torchvision.models as models
import sys
import os
from torchvision import datasets

# 添加模型路径到系统路径
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'model'))

logger = logging.getLogger(__name__)

class TongueAnalysisView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            # 初始化星火大模型
            self.spark = ChatSparkLLM(
                spark_api_url='wss://spark-api.xf-yun.com/chat/max-32k',
                spark_app_id='bf620b6f',
                spark_api_key='e306e8f60327283c6f44e6dd871f66dc',
                spark_api_secret='NDkwYmRlZDFlNDZmNTJlN2I2ZDk5YjJh',
                spark_llm_domain='max-32k',
                streaming=False,
            )
            
            # 加载数据集以获取正确的类别顺序
            data_dir = r"D:\code\sixweek\data\Tongue coating classification"
            dataset = datasets.ImageFolder(root=data_dir)
            self.class_names = dataset.classes
            
            # 初始化舌苔检测模型
            self.model_path = 'D:/code/sixweek/Code/front/model/tongue/trained_model_weights_new.pth'
            logger.info(f"尝试加载模型: {self.model_path}")
            
            # 使用ResNet50模型，保持与训练时相同的初始化方式
            self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            num_ftrs = self.model.fc.in_features
            self.model.fc = torch.nn.Linear(num_ftrs, 7)
            
            if os.path.exists(self.model_path):
                try:
                    self.model.load_state_dict(torch.load(self.model_path, map_location=torch.device('cpu')))
                    self.model.eval()
                    logger.info("舌苔检测模型加载成功")
                except Exception as e:
                    logger.error(f"模型加载失败: {str(e)}")
                    raise
            else:
                logger.error(f"模型文件不存在: {self.model_path}")
                raise FileNotFoundError(f"模型文件不存在: {self.model_path}")
            
            # 定义图像转换，与训练时保持一致
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
            ])
            
            # 英文到中文的映射
            self.en_to_cn = {
                "black tongue coating": "黑苔",
                "brown tongue coating": "褐苔",
                "map tongue coating": "地图舌",
                "purple tongue coating": "紫苔",
                "red tongue yellow fur thick greasy fur": "红舌黄苔厚腻苔",
                "The red tongue is thick and greasy": "红舌厚腻苔",
                "The white tongue is thick and greasy": "白舌厚腻苔"
            }
            
        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            raise

    def predict_tongue(self, image):
        """使用模型预测舌苔类型"""
        try:
            # 预处理图片
            image_tensor = self.transform(image).unsqueeze(0)
            
            # 进行预测
            with torch.no_grad():
                output = self.model(image_tensor)
                _, predicted = torch.max(output.data, 1)
            
            # 获取预测结果
            predicted_class_idx = predicted.item()
            predicted_class_en = self.class_names[predicted_class_idx]
            predicted_class_cn = self.en_to_cn[predicted_class_en]
            
            logger.info(f"舌苔预测结果: {predicted_class_en} -> {predicted_class_cn}")
            
            return predicted_class_en, predicted_class_cn
        except Exception as e:
            logger.error(f"舌苔预测失败: {str(e)}")
            return None, "预测失败"

    def get_ai_suggestions(self, tongue_type_cn):
        try:
            prompt = f"""
            基于以下舌诊结果给出建议：
            舌苔性状：{tongue_type_cn}

            请给出3条简短建议（每条15字以内）和7味推荐中药（只需要药名）。
            回复格式：
            建议：
            1. [建议1]
            2. [建议2]
            3. [建议3]
            
            推荐中药：
            [药名1]、[药名2]、[药名3]、[药名4]、[药名5]、[药名6]、[药名7]
            给出的建议和药名不要带[]。
            """
            
            messages = [ChatMessage(
                role="user",
                content=prompt
            )]
            
            result = self.spark.generate([messages])
            return result.generations[0][0].text
        except Exception as e:
            logger.error(f"获取AI建议失败: {str(e)}")
            return "AI建议获取失败，请稍后重试"

    def post(self, request):
        try:
            # 获取上传的舌苔图片
            image_file = request.FILES.get('image')
            if not image_file:
                logger.error("未找到上传的图片")
                return Response({'error': '未找到上传的图片'}, status=status.HTTP_400_BAD_REQUEST)

            # 打印接收到的文件信息
            logger.info(f"接收到文件: {image_file.name}, 大小: {image_file.size}")

            try:
                # 读取图片
                image_data = io.BytesIO(image_file.read())
                logger.info(f"成功读取图片数据，大小: {len(image_data.getvalue())} 字节")
                
                image = Image.open(image_data)
                logger.info(f"成功打开图片，尺寸: {image.size}，格式: {image.format}")
                
                # 使用模型预测舌苔类型
                logger.info("开始预测舌苔类型...")
                tongue_type_en, tongue_type_cn = self.predict_tongue(image)
                
                # 记录预测结果
                logger.info(f"舌苔预测完成: {tongue_type_en} -> {tongue_type_cn}")
                
                if not tongue_type_cn or tongue_type_cn == "预测失败":
                    logger.error("舌苔类型预测失败")
                    return Response({'error': '舌苔类型预测失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                # 构建分析结果（只包含舌苔性状）
                analysis_result = {
                    'tongueCoating': tongue_type_cn
                }
                logger.info(f"分析结果初步构建: {analysis_result}")

                # 调用星火大模型获取建议
                logger.info(f"正在获取AI建议，舌苔类型: {tongue_type_cn}")
                ai_suggestions = self.get_ai_suggestions(tongue_type_cn)
                analysis_result['aiSuggestions'] = ai_suggestions
                
                # 记录返回的结果
                logger.info(f"完整分析结果构建完成，准备返回: {analysis_result}")

                response = Response(analysis_result, status=status.HTTP_200_OK)
                logger.info(f"返回响应对象: {response}")
                return response
                
            except IOError as e:
                logger.error(f"图片处理错误: {str(e)}")
                return Response({'error': f'图片处理错误: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"舌诊分析失败: {str(e)}")
            return Response(
                {'error': f'服务器处理错误: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 