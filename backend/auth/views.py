from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random
import string
from PIL import Image, ImageDraw, ImageFont
import io

# 默认用户凭证
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin123'

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        # 检查是否匹配默认用户
        if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            return Response({
                'token': token,
                'username': username
            })
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        return Response(status=status.HTTP_200_OK)

class CaptchaView(APIView):
    def get(self, request):
        # 生成随机验证码
        chars = string.ascii_letters + string.digits
        captcha_text = ''.join(random.choices(chars, k=4))
        
        # 创建图片
        width = 120
        height = 40
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # 添加干扰线
        for i in range(5):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill='#666')
        
        # 添加验证码文字
        for i, char in enumerate(captcha_text):
            x = 20 + i * 20
            y = random.randint(5, 15)
            draw.text((x, y), char, fill='#333')
        
        # 保存验证码到缓存
        if not request.session.session_key:
            request.session.create()
        cache.set(f'captcha_{request.session.session_key}', captcha_text, timeout=300)
        
        # 返回图片
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return Response(buffer.getvalue(), content_type='image/png') 