from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import numpy as np
from PIL import Image
import io
import os
import torch
import sys
import torch.nn as nn
import torchvision.models as models

# 添加模型目录到系统路径
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'model/EfficientNet-B4'))

# 直接在views.py中定义EfficientNetB4模型类，避免导入问题
class EfficientNetB4(nn.Module):
    def __init__(self, num_classes=5):
        super(EfficientNetB4, self).__init__()
        # 加载 EfficientNet-B4 预训练模型
        self.model = models.efficientnet_b4(pretrained=True)
        # 修改最后的全连接层以适应五分类任务
        self.model.classifier[1] = nn.Linear(self.model.classifier[1].in_features, num_classes)

    def forward(self, x):
        return self.model(x)

class HerbIdentificationView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 模型路径
        self.model_path = "D:/code/sixweek/Code/front/model/EfficientNet-B4.pth"
        # 设备配置
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # 类别标签
        self.class_labels = ["百合", "党参", "枸杞", "槐花", "金银花"]
        # 加载模型
        self.model = self.load_model()
        
    def load_model(self):
        """加载预训练模型"""
        try:
            model = EfficientNetB4(num_classes=len(self.class_labels))
            model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            model.to(self.device)
            model.eval()  # 设置为评估模式
            return model
        except Exception as e:
            print(f"模型加载失败: {str(e)}")
            return None
    
    def preprocess_image(self, image):
        """对图像进行预处理"""
        from torchvision import transforms
        transform = transforms.Compose([
            transforms.Resize((320, 320)),  # 调整图像尺寸
            transforms.ToTensor(),         # 转换为张量
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # 标准化
        ])
        return transform(image).unsqueeze(0)  # 增加 batch 维度
    
    def predict(self, image):
        """使用模型预测图像类别"""
        if self.model is None:
            return None
            
        try:
            # 预处理图像
            image_tensor = self.preprocess_image(image).to(self.device)
            
            # 进行预测
            with torch.no_grad():
                outputs = self.model(image_tensor)
                _, predicted = torch.max(outputs, 1)
                
            # 获取预测的类别名称
            predicted_class = self.class_labels[predicted.item()]
            return predicted_class
        except Exception as e:
            print(f"预测失败: {str(e)}")
            return None
    
    def get_herb_info(self, herb_name):
        """根据药材名称获取详细信息"""
        herb_database = {
            '党参': {
                'name': '党参',
                'effects': '补中益气，健脾养胃，生津润肺',
                'properties': '甘、平',
                'meridians': '脾、肺经',
                'usage': '可煎服，或熬制成汤剂，也可研末服用。一般用量6-15克。',
                'precautions': '脾胃有热、阴虚火旺者慎用。',
            },
            '枸杞': {
                'name': '枸杞',
                'effects': '滋补肝肾，明目，润肺',
                'properties': '甘、平',
                'meridians': '肝、肾经',
                'usage': '煎服，或熬制成汤剂，也可研末服用。一般用量6-15克。',
                'precautions': '脾胃有热、阴虚火旺者慎用。',
            },
            '百合': {
                'name': '百合',
                'effects': '养阴润肺，清心安神',
                'properties': '甘、微寒',
                'meridians': '肺、心经',
                'usage': '煎服，或熬制成汤剂，也可研末服用。一般用量6-15克。',
                'precautions': '脾胃有热、阴虚火旺者慎用。',
            },
            '槐花': {
                'name': '槐花',
                'effects': '凉血止血，清肝泻火',
                'properties': '苦、寒',
                'meridians': '肝、大肠经',
                'usage': '煎服，或熬制成汤剂，也可研末服用。一般用量6-15克。',
                'precautions': '脾胃有热、阴虚火旺者慎用。',
            },
            '金银花': {
                'name': '金银花',
                'effects': '清热解毒，凉散风热',
                'properties': '甘、寒',
                'meridians': '肺、心经',
                'usage': '煎服，或熬制成汤剂，也可研末服用。一般用量6-15克。',
                'precautions': '脾胃有热、阴虚火旺者慎用。',
            }
        }
        
        return herb_database.get(herb_name, None)
            
    def post(self, request):
        try:
            # 获取上传的图片
            image_file = request.FILES.get('image')
            if not image_file:
                return Response({'error': '未找到上传的图片'}, status=status.HTTP_400_BAD_REQUEST)

            # 读取图片
            image = Image.open(io.BytesIO(image_file.read())).convert("RGB")
            
            # 使用模型预测图片类别
            predicted_herb = self.predict(image)
            
            if predicted_herb is None:
                return Response({'error': '模型预测失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            # 获取药材详细信息
            herb_info = self.get_herb_info(predicted_herb)
            
            if herb_info is None:
                return Response({'error': f'未找到药材 {predicted_herb} 的信息'}, status=status.HTTP_404_NOT_FOUND)

            return Response(herb_info, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 