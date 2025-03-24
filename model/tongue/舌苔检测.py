import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms, datasets, models
import os
from tqdm import tqdm
from PIL import Image

# 数据集根目录
data_dir = r"D:\code\sixweek\data\Tongue coating classification"

# 训练集的图像转换操作，包含更多数据增强
train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.RandomRotation(30),
    transforms.ColorJitter(brightness=0.5, contrast=0.5, saturation=0.5, hue=0.2),
    transforms.GaussianBlur(kernel_size=3),
    transforms.RandomAffine(degrees=30, translate=(0.2, 0.2), scale=(0.7, 1.3)),
    transforms.RandomErasing(p=0.8),
    transforms.RandomPerspective(distortion_scale=0.3, p=0.6),
    transforms.AutoAugment(transforms.AutoAugmentPolicy.IMAGENET),
    transforms.ToTensor(),
    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
])

# 测试集的图像转换操作，不包含数据增强
test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
])

# 加载数据集（假设没有划分训练集和测试集）
dataset = datasets.ImageFolder(root=data_dir)

# 划分训练集和测试集，这里按照 80% 训练集，20% 测试集的比例划分
train_size = int(0.8 * len(dataset))
test_size = len(dataset) - train_size
train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

# 对训练集和测试集分别应用不同的转换
train_dataset.dataset.transform = train_transform
test_dataset.dataset.transform = test_transform

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

# 使用更复杂的预训练模型，这里选择ResNet50
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
num_ftrs = model.fc.in_features
# 添加额外的全连接层
model.fc = nn.Sequential(
    nn.Linear(num_ftrs, 512),
    nn.ReLU(),
    nn.Dropout(0.5),
    nn.Linear(512, 7)
)

# 已训练模型的文件路径
model_path = 'trained_model_weights_new2.pth'

# 初始化模型
if os.path.exists(model_path):
    # 加载已训练的模型权重
    model.load_state_dict(torch.load(model_path))
    print("已加载训练好的模型")
    model.eval()
else:
    # 初始化损失函数和优化器，调整学习率，添加L2正则化
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.001)
    # 学习率调度器
    scheduler = CosineAnnealingWarmRestarts(optimizer, T_0=10, T_mult=2)

    # 早停机制参数
    best_val_acc = 0
    patience = 20
    counter = 0

    # 冻结模型的部分层
    for param in model.parameters():
        param.requires_grad = False
    for param in model.fc.parameters():
        param.requires_grad = True
    for param in model.layer4.parameters():
        param.requires_grad = True

    # 训练模型
    num_epochs = 300
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

        # 验证集评估
        with torch.no_grad():
            correct = 0
            total = 0
            for images, labels in test_loader:
                outputs = model(images)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
            val_acc = 100 * correct / total

        # 更新学习率
        scheduler.step()

        # 早停机制
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), model_path)
            counter = 0
        else:
            counter += 1
            if counter >= patience:
                print(f'Early stopping at epoch {epoch + 1}')
                break

    print('Finished Training')

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
result = predict_single_image(image_path, model, test_transform)
if result:
    print(f"预测结果: {result}")