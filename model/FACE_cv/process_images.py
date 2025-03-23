import os
import shutil
from model import FaceRecognitionModel
from config import DB_CONFIG

def process_folder(folder_path: str):
    """
    处理指定文件夹中的所有图片
    
    Args:
        folder_path: 图片文件夹路径
    """
    # 初始化人脸识别模型
    print("初始化人脸识别模型...")
    model = FaceRecognitionModel(DB_CONFIG)
    
    # 确保文件夹存在
    if not os.path.exists(folder_path):
        print(f"文件夹 {folder_path} 不存在")
        return
    
    # 支持的图片格式
    image_extensions = ('.jpg', '.jpeg', '.png')
    
    # 创建处理后的文件夹
    processed_folder = os.path.join(folder_path, 'processed')
    if not os.path.exists(processed_folder):
        os.makedirs(processed_folder)
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(image_extensions):
            image_path = os.path.join(folder_path, filename)
            name = os.path.splitext(filename)[0]  # 使用文件名作为人名
            
            print(f"\n处理图片: {filename}")
            
            # 添加人脸到数据库
            if model.add_face(image_path, name):
                print(f"成功添加人脸: {name}")
                # 移动已处理的图片到processed文件夹
                shutil.move(image_path, os.path.join(processed_folder, filename))
                print(f"已移动图片到: {processed_folder}")
            else:
                print(f"添加人脸失败: {name}")
    
    # 显示数据库中的所有记录
    print("\n当前数据库中的所有记录:")
    names = model.get_all_names()
    if names:
        for name in names:
            print(f"- {name}")
    else:
        print("数据库为空")

def main():
    """主函数"""
    # 获取当前目录
    current_dir = os.getcwd()
    
    # 创建images文件夹（如果不存在）
    images_folder = os.path.join(current_dir, 'images')
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
        print(f"已创建图片文件夹: {images_folder}")
        print("请将要处理的人脸图片放入该文件夹，然后重新运行此脚本")
        return
    
    # 处理图片
    print(f"开始处理文件夹: {images_folder}")
    process_folder(images_folder)

if __name__ == "__main__":
    main() 