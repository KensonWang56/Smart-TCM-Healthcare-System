import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tcm_platform.settings')
django.setup()

import mysql.connector
from django.conf import settings

def fix_face_tables():
    try:
        # 数据库配置
        db_config = {
            'host': 'localhost',
            'user': settings.DATABASES['default']['USER'],
            'password': settings.DATABASES['default']['PASSWORD'],
            'database': settings.DATABASES['default']['NAME']
        }
        
        # 连接MySQL数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        try:
            # 1. 检查face_recognition文件的load_data方法是否尝试使用uuid
            face_recognition_file = 'face_recognition/model.py'
            if os.path.exists(face_recognition_file):
                print(f"找到文件: {face_recognition_file}")
                
                # 备份原文件
                import shutil
                backup_file = f"{face_recognition_file}.bak"
                shutil.copy2(face_recognition_file, backup_file)
                print(f"已创建备份: {backup_file}")
                
                # 读取文件内容
                with open(face_recognition_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 修改load_data方法
                if 'SELECT u.id, u.name, u.uuid, fp.face_encoding' in content:
                    content = content.replace(
                        'SELECT u.id, u.name, u.uuid, fp.face_encoding', 
                        'SELECT u.id, u.name, fp.face_encoding'
                    )
                    
                    # 移除所有关于uuid的引用
                    content = content.replace('self.known_face_uuids = []', '')
                    content = content.replace('self.known_face_uuids.append(uuid)', '')
                    
                    # 写回文件
                    with open(face_recognition_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print("已修复load_data方法")
            
            # 2. 修复face_users表
            cursor.execute("SHOW TABLES LIKE 'face_users'")
            if cursor.fetchone():
                print("找到face_users表，尝试修复...")
                
                # 检查是否存在uuid列
                cursor.execute("SHOW COLUMNS FROM face_users LIKE 'uuid'")
                if cursor.fetchone():
                    # 删除uuid列
                    cursor.execute("ALTER TABLE face_users DROP COLUMN uuid")
                    conn.commit()
                    print("已删除uuid列")
                else:
                    print("face_users表中没有uuid列，无需处理")
            else:
                print("face_users表不存在，无需处理")
            
            # 3. 修复用户视图模块(views.py)中的uuid相关代码
            views_file = 'users/views.py'
            if os.path.exists(views_file):
                print(f"找到文件: {views_file}")
                
                # 备份原文件
                backup_file = f"{views_file}.bak"
                shutil.copy2(views_file, backup_file)
                print(f"已创建备份: {backup_file}")
                
                # 读取文件内容
                with open(views_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 修改recognize_face方法
                if '包含(用户名,用户uuid,相似度)的列表' in content:
                    content = content.replace(
                        '包含(用户名,用户uuid,相似度)的列表', 
                        '包含(用户名,相似度)的列表'
                    )
                
                # 修改返回结果处理
                if 'for name, uuid, similarity in results:' in content:
                    content = content.replace(
                        'for name, uuid, similarity in results:',
                        'for name, similarity in results:'
                    )
                    content = content.replace(
                        'recognized_users.append((name, uuid, similarity_percent))',
                        'recognized_users.append((name, similarity_percent))'
                    )
                
                # 修改FaceLoginView视图
                if 'for name, user_uuid, similarity in recognize_result:' in content:
                    content = content.replace(
                        'for name, user_uuid, similarity in recognize_result:',
                        'for name, similarity in recognize_result:'
                    )
                    content = content.replace(
                        'user = User.objects.get(uuid=user_uuid)',
                        'user = User.objects.get(username=name)'
                    )
                    
                    # 移除uuid回退查询部分
                    start_idx = content.find('except User.DoesNotExist:')
                    if start_idx != -1:
                        # 找到下一个try-except块的开始
                        next_try = content.find('try:', start_idx + 20)
                        if next_try != -1:
                            # 删除整个回退查询块
                            content = content[:start_idx] + content[next_try:]
                
                # 修改FaceUploadView的put方法
                if 'user_uuid = str(request.user.uuid)' in content:
                    content = content.replace(
                        'user_uuid = str(request.user.uuid)',
                        '# user_uuid removed'
                    )
                    content = content.replace(
                        'success = face_model.add_face(face_path, request.user.username, user_uuid)',
                        'success = face_model.add_face(face_path, request.user.username)'
                    )
                
                # 修改FaceUploadView的delete方法
                if 'user_uuid = str(request.user.uuid)' in content:
                    content = content.replace(
                        'user_uuid = str(request.user.uuid)',
                        '# user_uuid removed'
                    )
                    content = content.replace(
                        'success = face_model.remove_face(user_uuid)',
                        'success = face_model.remove_face(request.user.username)'
                    )
                    content = content.replace(
                        f'logger.warning(f"从人脸识别模型中移除用户 {request.user.username} (UUID: {user_uuid}) 的人脸数据失败")',
                        f'logger.warning(f"从人脸识别模型中移除用户 {request.user.username} 的人脸数据失败")'
                    )
                
                # 写回文件
                with open(views_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("已修复views.py文件")
                
            # 4. 修复face_recognition模型类
            model_file = 'face_recognition/model.py'
            if os.path.exists(model_file):
                print(f"找到文件: {model_file}")
                
                # 已经有备份，直接读取
                with open(model_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 修改add_face方法
                if 'def add_face(self, image_path: str, name: str, user_uuid: str,' in content:
                    content = content.replace(
                        'def add_face(self, image_path: str, name: str, user_uuid: str,',
                        'def add_face(self, image_path: str, name: str,'
                    )
                
                # 修改add_face方法中的查询参数
                if '"SELECT id FROM face_users WHERE uuid = %s"' in content:
                    content = content.replace(
                        '"SELECT id FROM face_users WHERE uuid = %s"',
                        '"SELECT id FROM face_users WHERE name = %s"'
                    )
                    content = content.replace(
                        '(user_uuid,)',
                        '(name,)'
                    )
                
                # 修改add_face方法中的日志
                if 'print(f"找到现有用户: {name} (UUID: {user_uuid}, ID: {user_id}")' in content:
                    content = content.replace(
                        'print(f"找到现有用户: {name} (UUID: {user_uuid}, ID: {user_id}")',
                        'print(f"找到现有用户: {name} (ID: {user_id}")'
                    )
                
                # 修改add_face方法中的用户创建
                if '"INSERT INTO face_users (name, uuid) VALUES (%s, %s)"' in content:
                    content = content.replace(
                        '"INSERT INTO face_users (name, uuid) VALUES (%s, %s)"',
                        '"INSERT INTO face_users (name) VALUES (%s)"'
                    )
                    content = content.replace(
                        '(name, user_uuid)',
                        '(name,)'
                    )
                
                # 修改添加成功日志
                if 'print(f"成功添加人脸数据: {name} (UUID: {user_uuid}")' in content:
                    content = content.replace(
                        'print(f"成功添加人脸数据: {name} (UUID: {user_uuid}")',
                        'print(f"成功添加人脸数据: {name}")'
                    )
                
                # 修改remove_face方法
                if 'def remove_face(self, user_uuid: str)' in content:
                    content = content.replace(
                        'def remove_face(self, user_uuid: str)',
                        'def remove_face(self, name: str)'
                    )
                
                # 修改remove_face中的查询
                if '"SELECT id, name FROM face_users WHERE uuid = %s"' in content:
                    content = content.replace(
                        '"SELECT id, name FROM face_users WHERE uuid = %s"',
                        '"SELECT id FROM face_users WHERE name = %s"'
                    )
                    content = content.replace(
                        '(user_uuid,)',
                        '(name,)'
                    )
                
                # 修改recognize_face返回类型
                if 'def recognize_face(self, image, threshold=0.75) -> List[Tuple[str, str, float]]:' in content:
                    content = content.replace(
                        'def recognize_face(self, image, threshold=0.75) -> List[Tuple[str, str, float]]:',
                        'def recognize_face(self, image, threshold=0.75) -> List[Tuple[str, float]]:'
                    )
                
                # 修改recognize_face方法中的返回值描述
                if 'List[Tuple[str, str, float]]: 识别结果列表，每个元素为(用户名, 用户UUID, 相似度)' in content:
                    content = content.replace(
                        'List[Tuple[str, str, float]]: 识别结果列表，每个元素为(用户名, 用户UUID, 相似度)',
                        'List[Tuple[str, float]]: 识别结果列表，每个元素为(用户名, 相似度)'
                    )
                
                # 修改未知用户的返回
                if 'return [("未知", "", 0.0)]' in content:
                    content = content.replace(
                        'return [("未知", "", 0.0)]',
                        'return [("未知", 0.0)]'
                    )
                
                # 修改匹配项
                if 'matches.append((self.known_face_names[i], self.known_face_uuids[i], float(similarity)))' in content:
                    content = content.replace(
                        'matches.append((self.known_face_names[i], self.known_face_uuids[i], float(similarity)))',
                        'matches.append((self.known_face_names[i], float(similarity)))'
                    )
                
                # 修改排序键
                if 'matches.sort(key=lambda x: x[2], reverse=True)' in content:
                    content = content.replace(
                        'matches.sort(key=lambda x: x[2], reverse=True)',
                        'matches.sort(key=lambda x: x[1], reverse=True)'
                    )
                
                # 写回文件
                with open(model_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("已修复model.py文件")
                
            # 5. 修复数据库中的face_users表创建
            cursor.execute("SHOW CREATE TABLE face_users")
            create_table = cursor.fetchone()
            
            if create_table and 'uuid' in create_table[1]:
                # 重新创建表，不包含uuid列
                cursor.execute("DROP TABLE face_users")
                cursor.execute("""
                    CREATE TABLE face_users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 需要重建face_photos表吗？
                cursor.execute("SHOW TABLES LIKE 'face_photos'")
                if cursor.fetchone():
                    # 获取照片数据
                    cursor.execute("SELECT user_id, photo_path, face_encoding, is_primary FROM face_photos")
                    photos = cursor.fetchall()
                    
                    cursor.execute("DROP TABLE face_photos")
                    cursor.execute("""
                        CREATE TABLE face_photos (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            user_id INT NOT NULL,
                            photo_path VARCHAR(255) NOT NULL,
                            face_encoding BLOB NOT NULL,
                            is_primary BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # 重新插入照片数据
                    for user_id, photo_path, face_encoding, is_primary in photos:
                        cursor.execute("""
                            INSERT INTO face_photos (user_id, photo_path, face_encoding, is_primary)
                            VALUES (%s, %s, %s, %s)
                        """, (user_id, photo_path, face_encoding, is_primary))
                
                conn.commit()
                print("已修复数据库表结构")
            
        except Exception as e:
            print(f"处理过程中出错: {str(e)}")
            conn.rollback()
        
        print("处理完成！")
        
    except Exception as e:
        print(f"整体处理过程中出错: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_face_tables()