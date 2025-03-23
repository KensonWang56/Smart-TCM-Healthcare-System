import torch
from PIL import Image
from torchvision import transforms
from models import EfficientNetB4
from cfgs import MODEL_PATH, DEVICE, NUM_CLASSES, CLASS_LABELS
import warnings


def preprocess_image(image):
    """
    对图像进行预处理
    :param image: PIL 图像对象
    :return: 预处理后的图像张量
    """
    transform = transforms.Compose([
        transforms.Resize((320, 320)),  # 调整图像尺寸
        transforms.ToTensor(),         # 转换为张量
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # 标准化
    ])
    if not isinstance(image, Image.Image):
        raise ValueError("Input image must be a PIL.Image.Image object.")
    return transform(image).unsqueeze(0)  # 增加 batch 维度


def load_model(model_path, num_classes):
    """
    加载训练好的模型权重
    :param model_path: 模型权重路径
    :param num_classes: 类别数量
    :return: 加载好权重的模型
    """
    model = EfficientNetB4(num_classes=NUM_CLASSES)
    model.load_state_dict(torch.load(model_path, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()  # 设置为评估模式
    return model


def predict_image(image_path, model):
    """
    使用模型对单张图片进行推理
    :param image_path: 图片路径
    :param model: 加载好的模型
    :return: 预测结果 (类别名称)
    """
    try:
        image = Image.open(image_path).convert("RGB")  # 确保图像为 RGB 格式
    except Exception as e:
        raise ValueError(f"Error loading image {image_path}: {e}")

    image_tensor = preprocess_image(image).to(DEVICE)

    with torch.no_grad():
        outputs = model(image_tensor)
        _, predicted = torch.max(outputs, 1)
    return CLASS_LABELS[predicted.item()]


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=UserWarning)

    # 加载模型
    model = load_model(MODEL_PATH, NUM_CLASSES)

    # 单张图片推理示例
    single_image_path = r"D:\code\sixweek\EfficientNet-B4_data\1742118727809.jpg"  # 测试图片路径
    if single_image_path and torch.cuda.is_available():
        try:
            prediction = predict_image(single_image_path, model)
        finally:
            print(f"Single Image Prediction:\nImage: {single_image_path}\nPredicted Class: {prediction}")

