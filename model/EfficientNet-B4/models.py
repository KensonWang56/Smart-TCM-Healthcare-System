# models.py
import torch
import torch.nn as nn
import torchvision.models as models
import torch.nn.functional as F

class EfficientNetB4(nn.Module):
    def __init__(self, num_classes=5):
        super(EfficientNetB4, self).__init__()
        # 加载 EfficientNet-B4 预训练模型
        self.model = models.efficientnet_b4(pretrained=True)  # Use pre-trained EfficientNet-B4
        # 修改最后的全连接层以适应五分类任务
        self.model.classifier[1] = nn.Linear(self.model.classifier[1].in_features, num_classes)

    def forward(self, x):
        return self.model(x)


# 1. 定义 MBConv 模块（Mobile Inverted Residual Block）
class MBConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels, expansion_factor, stride, kernel_size):
        super(MBConvBlock, self).__init__()

        self.stride = stride
        self.out_channels = out_channels

        # 1x1 扩展卷积（扩展通道数）
        self.expand_conv = nn.Conv2d(in_channels, in_channels * expansion_factor, kernel_size=1, padding=0)
        self.bn1 = nn.BatchNorm2d(in_channels * expansion_factor)

        # Depthwise 可分离卷积
        self.depthwise_conv = nn.Conv2d(in_channels * expansion_factor, in_channels * expansion_factor,
                                        kernel_size=kernel_size, stride=stride, padding=kernel_size // 2,
                                        groups=in_channels * expansion_factor)
        self.bn2 = nn.BatchNorm2d(in_channels * expansion_factor)

        # 1x1 压缩卷积（压缩通道数）
        self.project_conv = nn.Conv2d(in_channels * expansion_factor, out_channels, kernel_size=1, padding=0)
        self.bn3 = nn.BatchNorm2d(out_channels)

        # 残差连接（仅在 stride=1 时启用）
        self.use_residual = (in_channels == out_channels and stride == 1)

    def forward(self, x):
        residual = x

        x = F.relu(self.bn1(self.expand_conv(x)))  # 扩展卷积
        x = F.relu(self.bn2(self.depthwise_conv(x)))  # 深度可分离卷积
        x = self.bn3(self.project_conv(x))  # 压缩卷积

        if self.use_residual:
            x += residual  # 残差连接

        return x


# 2. 定义 EfficientNet-B4 模型架构
class EfficientNetB4Model(nn.Module):
    def __init__(self, num_classes):
        super(EfficientNetB4, self).__init__()

        # 第一层卷积
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1)
        self.bn1 = nn.BatchNorm2d(32)

        # 定义 MBConv 层
        self.mbconv1 = MBConvBlock(32, 64, expansion_factor=1, stride=1, kernel_size=3)
        self.mbconv2 = MBConvBlock(64, 128, expansion_factor=6, stride=2, kernel_size=3)
        self.mbconv3 = MBConvBlock(128, 256, expansion_factor=6, stride=2, kernel_size=3)
        self.mbconv4 = MBConvBlock(256, 512, expansion_factor=6, stride=2, kernel_size=3)

        # 最后的分类头（全连接层）
        self.fc = nn.Linear(512, num_classes)

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))  # 第一层卷积

        x = self.mbconv1(x)  # 第一层 MBConv
        x = self.mbconv2(x)  # 第二层 MBConv
        x = self.mbconv3(x)  # 第三层 MBConv
        x = self.mbconv4(x)  # 第四层 MBConv

        x = torch.mean(x, dim=[2, 3])  # 全局平均池化
        x = self.fc(x)  # 分类层

        return x