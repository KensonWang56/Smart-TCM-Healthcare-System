import os
from model import FaceRecognitionModel
from config import DB_CONFIG, FACE_RECOGNITION_CONFIG, IMAGE_PATHS

def setup_directories():
    """创建必要的目录"""
    for dir_path in IMAGE_PATHS.values():
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"创建目录: {dir_path}")

def add_known_faces(model):
    """添加已知人脸到数据库"""
    known_faces_dir = IMAGE_PATHS['known_faces_dir']
    
    # 遍历已知人脸目录
    for filename in os.listdir(known_faces_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(known_faces_dir, filename)
            name = os.path.splitext(filename)[0]  # 使用文件名作为人名
            
            print(f"\n正在添加人脸: {name}")
            if model.add_face(image_path, name):
                print(f"成功添加人脸: {name}")
            else:
                print(f"添加人脸失败: {name}")

def test_face_recognition(model):
    """测试人脸识别"""
    test_faces_dir = IMAGE_PATHS['test_faces_dir']
    
    # 遍历测试图片目录
    for filename in os.listdir(test_faces_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(test_faces_dir, filename)
            print(f"\n正在识别图片: {filename}")
            
            # 识别人脸
            results = model.recognize_face(
                image_path, 
                tolerance=FACE_RECOGNITION_CONFIG['tolerance']
            )
            
            # 输出识别结果
            if results:
                for name, similarity in results:
                    print(f"识别结果: {name}, 相似度: {similarity:.2f}")
            else:
                print("未检测到人脸")

def main():
    """主函数"""
    # 创建必要的目录
    setup_directories()
    
    # 初始化人脸识别模型
    print("初始化人脸识别模型...")
    model = FaceRecognitionModel(DB_CONFIG)
    
    # 显示所有已存储的人脸
    print("\n当前数据库中的人脸:")
    names = model.get_all_names()
    if names:
        for name in names:
            print(f"- {name}")
    else:
        print("数据库为空")
    
    # 添加已知人脸
    print("\n开始添加已知人脸...")
    add_known_faces(model)
    
    # 测试人脸识别
    print("\n开始测试人脸识别...")
    test_face_recognition(model)

if __name__ == "__main__":
    main() 