import os
import torch
import requests
from tqdm import tqdm
from pathlib import Path
from facenet_pytorch import MTCNN, InceptionResnetV1

def get_model_dir():
    """获取模型存储目录"""
    cache_dir = os.path.expanduser('~/.cache/torch/checkpoints')
    if os.name == 'nt':  # Windows系统
        cache_dir = os.path.expandvars('%USERPROFILE%/.cache/torch/checkpoints')
    return cache_dir

def download_file(url, filename):
    """下载文件并显示进度条"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    print(f"开始下载 {filename}...")
    with open(filename, 'wb') as f, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            pbar.update(size)
    print(f"{filename} 下载完成！")

def download_models():
    """下载并验证人脸识别模型"""
    # 创建模型目录
    model_dir = get_model_dir()
    os.makedirs(model_dir, exist_ok=True)
    print(f"模型将保存在: {model_dir}")
    
    # InceptionResnetV1 模型下载链接
    resnet_url = "https://drive.google.com/uc?export=download&id=1Sy3QkBZlSbhrpW0lLPeY5HBe-rVlTv8X"
    resnet_path = os.path.join(model_dir, "20180402-114759-vggface2.pt")
    
    # 检查是否已存在模型文件
    if not os.path.exists(resnet_path):
        print("未找到预训练模型文件，开始下载...")
        download_file(resnet_url, resnet_path)
    else:
        print("预训练模型文件已存在，跳过下载。")
    
    # 验证模型
    print("\n正在验证模型...")
    try:
        # 设置设备
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"使用设备: {device}")
        
        # 加载并验证 MTCNN
        print("正在加载 MTCNN 模型...")
        mtcnn = MTCNN(
            keep_all=True,
            device=device,
            selection_method='probability'
        )
        print("MTCNN 模型加载成功！")
        
        # 加载并验证 InceptionResnetV1
        print("正在加载 InceptionResnetV1 模型...")
        resnet = InceptionResnetV1(
            pretrained='vggface2'
        ).to(device).eval()
        print("InceptionResnetV1 模型加载成功！")
        
        print("\n所有模型验证完成！")
        print("模型文件位置：")
        print(f"- InceptionResnetV1: {resnet_path}")
        print(f"- MTCNN: 已自动下载到 {model_dir}")
        
    except Exception as e:
        print(f"\n模型验证过程中出现错误: {str(e)}")
        print("请检查网络连接或尝试手动下载模型文件。")

if __name__ == "__main__":
    print("=== 人脸识别模型下载工具 ===")
    print("本工具将帮助您下载和验证人脸识别所需的预训练模型。")
    print("如果模型已存在，将跳过下载步骤。")
    print("=" * 40)
    
    download_models() 
    