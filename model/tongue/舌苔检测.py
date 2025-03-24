#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/3/24 10:00
# @Author  : fangjianxin
# @File    : 舌苔检测.py
# @Software: PyCharm

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms, datasets
import os
from tqdm import tqdm
from PIL import Image

# 数据集根目录
data_dir = r'D:\人工智能大实训\1ad8a-main\Tongue coating classification'
# 图像转换操作
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

# 加载数据集（假设没有划分训练集和测试集）
dataset = datasets.ImageFolder(root=data_dir, transform=transform)

# 划分训练集和测试集，这里按照 80% 训练集，20% 测试集的比例划分
train_size = int(0.8 * len(dataset))
test_size = len(dataset) - train_size
train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=4, shuffle=False)


# 定义模型
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)

        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)

        self.fc1 = nn.Linear(32 * 56 * 56, 128)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(128, 7)

    def forward(self, x):
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = x.view(-1, 32 * 56 * 56)
        x = self.relu3(self.fc1(x))
        x = self.fc2(x)
        return x


# 已训练模型的文件路径
model_path = 'trained_model_weights_new.pth'

# 初始化模型
model = SimpleCNN()
if os.path.exists(model_path):
    # 加载已训练的模型权重
    model.load_state_dict(torch.load(model_path))
    print("已加载训练好的模型")
    model.eval()
else:
    # 初始化损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

    # 训练模型
    num_epochs = 100
    for epoch in range(num_epochs):
        running_loss = 0.0
        # 使用 tqdm 显示训练进度
        progress_bar = tqdm(enumerate(train_loader), total=len(train_loader), desc=f'Epoch {epoch + 1}/{num_epochs}')
        for i, data in progress_bar:
            inputs, labels = data
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            if i % 100 == 99:
                avg_loss = running_loss / 100
                progress_bar.set_postfix({'loss': avg_loss})
                running_loss = 0.0

    print('Finished Training')
    # 保存训练好的模型权重
    torch.save(model.state_dict(), model_path)

# 进行预测
with torch.no_grad():
    correct = 0
    total = 0
    for images, labels in test_loader:
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    print(f'Accuracy of the network on the test images: {100 * correct / total}%')


# 新增部分：让用户输入图片进行预测
def predict_single_image(image_path, model, transform):
    try:
        # 打开图片
        image = Image.open(image_path)
        # 预处理图片
        image = transform(image).unsqueeze(0)
        # 进行预测
        with torch.no_grad():
            output = model(image)
            _, predicted = torch.max(output.data, 1)
        # 获取类别名称
        class_names = dataset.classes
        predicted_class = class_names[predicted.item()]
        return predicted_class
    except Exception as e:
        print(f"预测出错: {e}")
        return None


# 让用户输入图片路径
image_path = input("请输入要预测的图片路径: ")
result = predict_single_image(image_path, model, transform)
if result:
    print(f"预测结果: {result}")
