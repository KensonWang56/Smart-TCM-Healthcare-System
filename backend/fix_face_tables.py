import mysql.connector

def fix_face_tables():
    try:
        # 数据库配置
        db_config = {
            'host': 'localhost',
            'user': 'root',  # 修改为您的MySQL用户名
            'password': '123456',  # 修改为您的MySQL密码
            'database': 'tcm_platform'  # 修改为您的数据库名
        }
        
        # 连接MySQL数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        try:
            # 检查face_users表是否存在
            cursor.execute("SHOW TABLES LIKE 'face_users'")
            if cursor.fetchone():
                print("找到face_users表，正在检查结构...")
                
                # 获取表结构
                cursor.execute("DESCRIBE face_users")
                columns = cursor.fetchall()
                
                # 检查是否存在uuid列
                has_uuid = False
                for column in columns:
                    if column[0] == 'uuid':
                        has_uuid = True
                        break
                
                if has_uuid:
                    print("检测到uuid列，正在移除...")
                    
                    # 重建face_users表，不包含uuid列
                    cursor.execute("""
                        CREATE TABLE face_users_new (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            name VARCHAR(100) NOT NULL UNIQUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # 复制数据
                    cursor.execute("""
                        INSERT INTO face_users_new (id, name, created_at)
                        SELECT id, name, created_at FROM face_users
                    """)
                    
                    # 删除旧表
                    cursor.execute("DROP TABLE face_users")
                    
                    # 重命名新表
                    cursor.execute("RENAME TABLE face_users_new TO face_users")
                    
                    print("已重建face_users表，移除了uuid列")
                else:
                    print("face_users表中没有uuid列，无需处理")
            else:
                print("face_users表不存在，将会在应用启动时自动创建")
            
            # 提交事务
            conn.commit()
            print("处理完成！")
            
        except Exception as e:
            conn.rollback()
            print(f"处理过程中出错: {str(e)}")
        
    except Exception as e:
        print(f"连接数据库出错: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_face_tables() 