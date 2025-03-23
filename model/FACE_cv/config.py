# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # 替换为您的MySQL用户名
    'password': '123456',  # 替换为您的MySQL密码
    'database': 'face_recognition_db'
}

# 人脸识别配置
FACE_RECOGNITION_CONFIG = {
    'tolerance': 0.6,  # 人脸匹配阈值，越小越严格
    'model': 'hog'  # 人脸检测模型：'hog' 或 'cnn'
}

# 照片存储配置
STORAGE_CONFIG = {
    'photo_dir': 'face_photos',  # 照片存储根目录
    'photo_format': 'jpg',       # 照片格式
    'photo_quality': 95,         # JPEG质量（1-100）
    'min_face_size': 160,        # 最小人脸尺寸
    'naming_pattern': '{user_id}_{timestamp}.{ext}'  # 照片命名模式
}

# 图片路径配置
IMAGE_PATHS = {
    'known_faces_dir': 'known_faces',  # 已知人脸图片目录
    'test_faces_dir': 'test_faces',    # 测试人脸图片目录
} 