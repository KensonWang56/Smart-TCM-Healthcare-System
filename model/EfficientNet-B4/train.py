# train.py
import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
from models import EfficientNetB4
from dataset import get_dataloader
from cfgs import WEIGHTS_DIR, LEARNING_RATE, EPOCHS, DEVICE, BATCH_SIZE, NUM_CLASSES


def train(model, train_loader, val_loader, device, epochs=5, learning_rate=0.001):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    model.to(device)

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct_preds = 0
        total_preds = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()

            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            correct_preds += (predicted == labels).sum().item()
            total_preds += labels.size(0)

        epoch_loss = running_loss / len(train_loader)
        epoch_acc = correct_preds / total_preds * 100

        print(f"Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss:.4f}, Accuracy: {epoch_acc:.2f}%")

        # 每个epoch结束后验证一下
        validate(model, val_loader, device)

    # 保存模型权重
    torch.save(model.state_dict(), WEIGHTS_DIR)


def validate(model, val_loader, device):
    model.eval()
    correct_preds = 0
    total_preds = 0
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            correct_preds += (predicted == labels).sum().item()
            total_preds += labels.size(0)

    accuracy = correct_preds / total_preds * 100
    print(f"Validation Accuracy: {accuracy:.2f}%")


if __name__ == "__main__":
    # 加载数据
    train_loader, val_loader = get_dataloader(batch_size=BATCH_SIZE)

    # 加载模型
    model = EfficientNetB4(num_classes=NUM_CLASSES)

    # 训练模型
    train(model, train_loader, val_loader, DEVICE, epochs=EPOCHS, learning_rate=LEARNING_RATE)
