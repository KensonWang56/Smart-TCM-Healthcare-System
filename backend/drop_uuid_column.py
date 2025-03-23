import mysql.connector
import traceback

def drop_uuid_column():
    try:
        print("开始执行脚本...")
        # 数据库配置
        db_config = {
            'host': 'localhost',
            'user': 'root',  # 修改为您的MySQL用户名
            'password': '123456',  # 修改为您的MySQL密码
            'database': 'tcm_platform'  # 修改为您的数据库名
        }
        
        print("连接到数据库...")
        # 连接MySQL数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        try:
            # 检查users_user表中是否存在uuid列
            print("检查users_user表结构...")
            cursor.execute("DESCRIBE users_user")
            columns = cursor.fetchall()
            
            print(f"表结构: {columns}")
            
            # 检查是否存在uuid列
            has_uuid = False
            for column in columns:
                if column[0] == 'uuid':
                    has_uuid = True
                    break
            
            if has_uuid:
                print("检测到uuid列，正在从users_user表中移除...")
                
                # 删除uuid列
                cursor.execute("ALTER TABLE users_user DROP COLUMN uuid")
                
                print("已成功移除users_user表中的uuid列")
            else:
                print("users_user表中没有uuid列，无需处理")
            
            # 提交事务
            conn.commit()
            print("处理完成！")
            
        except Exception as e:
            conn.rollback()
            print(f"处理过程中出错: {str(e)}")
            traceback.print_exc()
        
    except Exception as e:
        print(f"连接数据库出错: {str(e)}")
        traceback.print_exc()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    drop_uuid_column() 