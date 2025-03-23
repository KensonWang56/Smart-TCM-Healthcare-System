import torch
import numpy as np
import cv2
from PIL import Image
import pickle
import mysql.connector
from typing import List, Tuple, Optional
import os
import time
from datetime import datetime
from .config import DB_CONFIG, STORAGE_CONFIG
from .model_utils import load_face_models

class FaceRecognitionModel:
    def __init__(self, db_config: dict):
        """
        初始化人脸识别模型
        
        Args:
            db_config: MySQL数据库配置
        """
        self.db_config = db_config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"使用设备: {self.device}")
        
        # 初始化模型
        self.mtcnn, self.resnet = load_face_models(self.device)
        
        # 创建照片存储目录
        os.makedirs(STORAGE_CONFIG['photo_dir'], exist_ok=True)
        
        # 初始化数据
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        self.init_database()
        self.load_data()
    
    def init_database(self):
        """初始化数据库表"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS face_users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建人脸照片表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS face_photos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    photo_path VARCHAR(255) NOT NULL,
                    face_encoding BLOB NOT NULL,
                    is_primary BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("数据库初始化成功")
        except Exception as e:
            print(f"数据库初始化失败: {str(e)}")
    
    def load_data(self):
        """从数据库加载人脸数据"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 加载所有用户的主要人脸照片
            cursor.execute("""
                SELECT u.id, u.name, fp.face_encoding 
                FROM face_users u 
                JOIN face_photos fp ON u.id = fp.user_id 
                WHERE fp.is_primary = TRUE
            """)
            results = cursor.fetchall()
            
            self.known_face_ids = []
            self.known_face_names = []
            self.known_face_encodings = []
            
            for user_id, name, face_encoding_blob in results:
                face_encoding = pickle.loads(face_encoding_blob)
                self.known_face_ids.append(user_id)
                self.known_face_names.append(name)
                self.known_face_encodings.append(face_encoding)
            
            print(f"已从数据库加载 {len(self.known_face_names)} 个用户的人脸数据")
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"从数据库加载数据时出错: {str(e)}")
    
    def save_photo(self, image: Image.Image, user_id: int) -> str:
        """
        保存人脸照片
        
        Args:
            image: PIL图像对象
            user_id: 用户ID
            
        Returns:
            str: 保存的文件路径
        """
        try:
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = STORAGE_CONFIG['naming_pattern'].format(
                user_id=user_id,
                timestamp=timestamp,
                ext=STORAGE_CONFIG['photo_format'].lower()
            )
            
            # 构建完整路径
            photo_path = os.path.join(STORAGE_CONFIG['photo_dir'], filename)
            
            # 确保图片是RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 保存图片
            image.save(
                photo_path,
                format='JPEG',
                quality=STORAGE_CONFIG['photo_quality']
            )
            
            print(f"照片已保存到: {photo_path}")
            return photo_path
            
        except Exception as e:
            print(f"保存照片时出错: {str(e)}")
            raise
    
    def extract_face_encoding(self, image) -> Optional[np.ndarray]:
        """
        提取人脸特征向量
        
        Args:
            image: 图片数据（PIL.Image或numpy数组）
            
        Returns:
            np.ndarray: 人脸特征向量，如果未检测到人脸则返回None
        """
        try:
            # 转换为PIL Image
            if isinstance(image, np.ndarray):
                image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # 检测人脸
            faces = self.mtcnn(image)
            if faces is None:
                print("未检测到人脸")
                return None
            
            # 确保人脸张量在正确的设备上
            faces = faces.to(self.device)
            
            # 提取特征
            with torch.no_grad():
                face_embedding = self.resnet(faces[0].unsqueeze(0))
            
            return face_embedding.cpu().numpy()[0]
            
        except Exception as e:
            print(f"提取人脸特征时出错: {str(e)}")
            return None
    
    def add_face(self, image_path: str, name: str, make_primary: bool = True) -> bool:
        """
        添加人脸到数据库
        
        Args:
            image_path: 图片路径
            name: 用户名
            make_primary: 是否设为主要人脸照片
            
        Returns:
            bool: 是否成功添加
        """
        try:
            print(f"正在处理图片: {image_path}")
            
            # 读取图片
            try:
                image = Image.open(image_path)
                # 确保图片是RGB模式
                if image.mode != 'RGB':
                    image = image.convert('RGB')
            except Exception as e:
                print(f"读取图片失败: {str(e)}")
                return False
            
            # 提取人脸特征
            face_encoding = self.extract_face_encoding(image)
            if face_encoding is None:
                print(f"未在图片中检测到人脸: {image_path}")
                return False
            
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 开启事务
            conn.start_transaction()
            
            try:
                # 先检查是否存在该用户的数据，如果存在则先删除
                cursor.execute(
                    "SELECT id FROM face_users WHERE name = %s",
                    (name,)
                )
                result = cursor.fetchone()
                
                if result:
                    user_id = result[0]
                    print(f"找到现有用户: {name} (ID: {user_id})")
                    
                    # 获取所有照片路径以便删除
                    cursor.execute(
                        "SELECT photo_path FROM face_photos WHERE user_id = %s",
                        (user_id,)
                    )
                    photo_paths = [row[0] for row in cursor.fetchall()]
                    
                    # 删除物理文件
                    for photo_path in photo_paths:
                        if os.path.exists(photo_path):
                            try:
                                os.remove(photo_path)
                                print(f"删除旧照片: {photo_path}")
                            except Exception as e:
                                print(f"删除旧照片失败: {photo_path}, 错误: {str(e)}")
                    
                    # 删除数据库中的照片记录
                    cursor.execute(
                        "DELETE FROM face_photos WHERE user_id = %s",
                        (user_id,)
                    )
                    
                    # 更新用户名（以防用户更改了用户名）
                    cursor.execute(
                        "UPDATE face_users SET name = %s WHERE id = %s",
                        (name, user_id)
                    )
                    
                    # 从内存中移除旧的人脸数据
                    indices = []
                    for i, id_val in enumerate(self.known_face_ids):
                        if id_val == user_id:
                            indices.append(i)
                    
                    for index in sorted(indices, reverse=True):
                        del self.known_face_ids[index]
                        del self.known_face_names[index]
                        del self.known_face_encodings[index]
                else:
                    # 创建新用户
                    cursor.execute(
                        "INSERT INTO face_users (name) VALUES (%s)",
                        (name,)
                    )
                    user_id = cursor.lastrowid
                    print(f"创建新用户: {name} (ID: {user_id})")
                
                # 保存照片文件
                try:
                    photo_path = self.save_photo(image, user_id)
                except Exception as e:
                    print(f"保存照片失败: {str(e)}")
                    raise
                
                # 将特征向量转换为二进制
                face_encoding_blob = pickle.dumps(face_encoding)
                
                # 保存到数据库
                cursor.execute(
                    """
                    INSERT INTO face_photos 
                    (user_id, photo_path, face_encoding, is_primary) 
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, photo_path, face_encoding_blob, make_primary)
                )
                
                # 提交事务
                conn.commit()
                
                # 更新内存中的数据
                self.known_face_ids.append(user_id)
                self.known_face_names.append(name)
                self.known_face_encodings.append(face_encoding)
                
                print(f"成功添加人脸数据: {name}")
                return True
                
            except Exception as e:
                # 回滚事务
                conn.rollback()
                print(f"数据库操作失败: {str(e)}")
                raise
                
        except Exception as e:
            print(f"添加人脸时出错: {str(e)}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def get_user_photos(self, user_id: int) -> List[dict]:
        """
        获取用户的所有照片
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[dict]: 照片信息列表
        """
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute(
                """
                SELECT id, photo_path, is_primary, created_at 
                FROM face_photos 
                WHERE user_id = %s 
                ORDER BY created_at DESC
                """,
                (user_id,)
            )
            
            photos = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return photos
            
        except Exception as e:
            print(f"获取用户照片时出错: {str(e)}")
            return []
    
    def set_primary_photo(self, photo_id: int) -> bool:
        """
        设置主要照片
        
        Args:
            photo_id: 照片ID
            
        Returns:
            bool: 是否成功设置
        """
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 开启事务
            conn.start_transaction()
            
            try:
                # 获取照片信息
                cursor.execute(
                    """
                    SELECT user_id, face_encoding 
                    FROM face_photos 
                    WHERE id = %s
                    """,
                    (photo_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    return False
                    
                user_id, face_encoding_blob = result
                
                # 取消当前主要照片
                cursor.execute(
                    "UPDATE face_photos SET is_primary = FALSE WHERE user_id = %s",
                    (user_id,)
                )
                
                # 设置新的主要照片
                cursor.execute(
                    "UPDATE face_photos SET is_primary = TRUE WHERE id = %s",
                    (photo_id,)
                )
                
                # 获取用户名
                cursor.execute(
                    "SELECT name FROM face_users WHERE id = %s",
                    (user_id,)
                )
                name = cursor.fetchone()[0]
                
                # 提交事务
                conn.commit()
                
                # 更新内存中的数据
                if user_id in self.known_face_ids:
                    idx = self.known_face_ids.index(user_id)
                    self.known_face_encodings[idx] = pickle.loads(face_encoding_blob)
                else:
                    self.known_face_ids.append(user_id)
                    self.known_face_names.append(name)
                    self.known_face_encodings.append(pickle.loads(face_encoding_blob))
                
                return True
                
            except Exception as e:
                conn.rollback()
                raise e
                
        except Exception as e:
            print(f"设置主要照片时出错: {str(e)}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def recognize_face(self, image, threshold=0.75) -> List[Tuple[str, float]]:
        """
        识别图片中的人脸
        
        Args:
            image: 图片数据（PIL.Image或numpy数组）
            threshold: 相似度阈值
            
        Returns:
            List[Tuple[str, float]]: 识别结果列表，每个元素为(用户名, 相似度)
        """
        try:
            # 提取人脸特征
            face_encoding = self.extract_face_encoding(image)
            if face_encoding is None:
                return []
            
            if not self.known_face_encodings:
                return [("未知", 0.0)]
            
            # 计算与所有已知人脸的相似度
            face_encoding = torch.from_numpy(face_encoding).to(self.device)
            known_encodings = torch.from_numpy(np.array(self.known_face_encodings)).to(self.device)
            
            # 计算余弦相似度
            with torch.no_grad():
                similarities = torch.nn.functional.cosine_similarity(
                    face_encoding.unsqueeze(0),
                    known_encodings
                )
            
            # 将相似度转为CPU张量并转为numpy数组
            similarities = similarities.cpu().numpy()
            
            # 找出所有超过阈值的匹配项
            matches = []
            for i, similarity in enumerate(similarities):
                if similarity >= threshold:
                    matches.append((self.known_face_names[i], float(similarity)))
            
            # 按相似度降序排序
            matches.sort(key=lambda x: x[1], reverse=True)
            
            if matches:
                return matches
            else:
                return [("未知", 0.0)]
                
        except Exception as e:
            print(f"识别人脸时出错: {str(e)}")
            return []
    
    def get_all_names(self) -> List[str]:
        """获取所有已知人脸的名字"""
        return self.known_face_names.copy()
    
    def remove_face(self, name: str) -> bool:
        """
        删除指定用户的所有人脸数据
        
        Args:
            name: 用户名
            
        Returns:
            bool: 操作是否成功
        """
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 开启事务
            conn.start_transaction()
            
            try:
                # 查找用户ID
                cursor.execute(
                    "SELECT id, name FROM face_users WHERE name = %s",
                    (name,)
                )
                result = cursor.fetchone()
                
                if not result:
                    print(f"用户不存在: {name}")
                    return False
                    
                user_id, user_name = result
                
                # 查询用户的所有照片路径
                cursor.execute(
                    "SELECT photo_path FROM face_photos WHERE user_id = %s",
                    (user_id,)
                )
                photo_paths = [row[0] for row in cursor.fetchall()]
                
                # 删除物理文件
                for photo_path in photo_paths:
                    if os.path.exists(photo_path):
                        try:
                            os.remove(photo_path)
                            print(f"删除物理文件: {photo_path}")
                        except Exception as e:
                            print(f"删除物理文件失败: {photo_path}, 错误: {str(e)}")
                
                # 删除数据库中的照片记录
                cursor.execute(
                    "DELETE FROM face_photos WHERE user_id = %s",
                    (user_id,)
                )
                
                # 从内存中移除该用户的人脸数据
                indices = []
                for i, id_val in enumerate(self.known_face_ids):
                    if id_val == user_id:
                        indices.append(i)
                
                for index in sorted(indices, reverse=True):
                    del self.known_face_ids[index]
                    del self.known_face_names[index]
                    del self.known_face_encodings[index]
                
                # 提交事务
                conn.commit()
                print(f"成功删除用户人脸数据: {user_name}")
                return True
                
            except Exception as e:
                conn.rollback()
                print(f"删除用户人脸数据时出错: {str(e)}")
                raise e
                
        except Exception as e:
            print(f"删除用户人脸数据时出错: {str(e)}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close() 