from models import EfficientNetB4
from cfgs import *
from dataset import get_dataloader
from predict import load_model

def test():
    test_loader, class_to_idx = get_dataloader()

    # 加载模型
    model = EfficientNetB4(num_classes=len(class_to_idx)).to(DEVICE)
    model = load_model(MODEL_PATH, DEVICE)
    model.eval()

    # 测试模型
    correct_per_class = {i: 0 for i in range(NUM_CLASSES)}  # 初始化每个类别的正确计数
    total_per_class = {i: 0 for i in range(NUM_CLASSES)}  # 初始化每个类别的总计数
    total_correct = 0
    total_samples = 0

    model.eval()  # 设置模型为评估模式
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)

            # 前向传播
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)

            # 统计每个类别的准确率
            for label, prediction in zip(labels, predicted):
                total_per_class[label.item()] += 1
                if label == prediction:
                    correct_per_class[label.item()] += 1

            # 统计总体准确率
            total_samples += labels.size(0)
            total_correct += (predicted == labels).sum().item()

    # 计算每个类别的准确率

    class_accuracies = {
        CLASS_LABELS[i]: correct_per_class.get(i, 0) / total_per_class[i] if total_per_class[i] > 0 else 0.0
        for i in range(NUM_CLASSES)
    }
    total_accuracy = total_correct / total_samples

    # 打印每个类别的准确率
    print("Class-wise Accuracies:")
    for class_name, accuracy in class_accuracies.items():
        print(f"{class_name}: {accuracy:.4f}")

    # 打印总准确率
    print(f"Overall Validation Accuracy: {total_accuracy:.4f}")

if __name__ == "__main__":
    test()