import torch

# 数据集路径
DATASET_DIR = "./data/Chinese Medicine"

# DataLoader 多线程加载数据
NUM_WORKERS = 4

#图片输入大小
INPUT_SIZE = 224

# 模型保存路径
WEIGHTS_DIR = "weights/EfficientNet-B4.pth"  # 权重存储路径

# 加载完整模型路径
MODEL_PATH = "weights/EfficientNet-B4.pth"

# 模型训练配置
BATCH_SIZE = 32
EPOCHS = 4
LEARNING_RATE = 0.001
NUM_CLASSES = 5

# 图像预处理
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]

# 定义类别标签
CLASS_LABELS = [
    "百合","党参","枸杞","槐花","金银花"
]

# 设备配置
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"