# dataset.py
import os
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from cfgs import INPUT_SIZE, MEAN, STD, NUM_WORKERS, DATASET_DIR


class ChineseMedicineDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.class_names = os.listdir(data_dir)  # 子文件夹名称就是类别名
        self.image_paths = []
        self.labels = []

        # 遍历每个类别文件夹，收集图片路径和标签
        for label, class_name in enumerate(self.class_names):
            class_folder = os.path.join(data_dir, class_name)
            for filename in os.listdir(class_folder):
                if filename.endswith('.jpg') or filename.endswith('.png'):
                    self.image_paths.append(os.path.join(class_folder, filename))
                    self.labels.append(label)

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]

        # 加载图片
        img = Image.open(img_path).convert("RGB")

        if self.transform:
            img = self.transform(img)

        return img, label


# 数据增强和预处理
transform = transforms.Compose([
    transforms.Resize((INPUT_SIZE, INPUT_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=MEAN, std=STD),
])


def get_dataloader(batch_size=32, num_workers=4):
    # 划分训练集和验证集
    dataset = ChineseMedicineDataset(DATASET_DIR, transform=transform)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    return train_loader, val_loader
