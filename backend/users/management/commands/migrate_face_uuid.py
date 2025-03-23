from django.core.management.base import BaseCommand
import mysql.connector
from django.conf import settings
from django.contrib.auth import get_user_model
import logging

# 获取用户模型
User = get_user_model()

class Command(BaseCommand):
    help = '将现有的人脸数据迁移到使用UUID关联用户'

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        
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
            
            # 检查face_users表是否存在uuid列
            try:
                cursor.execute("SHOW COLUMNS FROM face_users LIKE 'uuid'")
                uuid_column_exists = cursor.fetchone() is not None
                
                if not uuid_column_exists:
                    self.stdout.write(self.style.WARNING('face_users表中不存在uuid列，添加该列...'))
                    cursor.execute("""
                        ALTER TABLE face_users
                        ADD COLUMN uuid VARCHAR(36) NOT NULL UNIQUE AFTER name
                    """)
                    conn.commit()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'检查uuid列出错: {str(e)}'))
                return
            
            # 获取所有现有的用户记录
            cursor.execute("SELECT id, name FROM face_users")
            face_users = cursor.fetchall()
            
            updated_count = 0
            for face_user_id, face_user_name in face_users:
                try:
                    # 从Django用户模型中查找对应的用户
                    django_user = User.objects.get(username=face_user_name)
                    
                    # 更新人脸用户的UUID字段
                    user_uuid = str(django_user.uuid)
                    cursor.execute(
                        "UPDATE face_users SET uuid = %s WHERE id = %s",
                        (user_uuid, face_user_id)
                    )
                    updated_count += 1
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'已更新用户 {face_user_name} (ID: {face_user_id}) 的UUID为 {user_uuid}'
                    ))
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f'用户 {face_user_name} 在Django用户表中不存在，无法更新UUID'
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'更新用户 {face_user_name} 的UUID时出错: {str(e)}'
                    ))
            
            conn.commit()
            self.stdout.write(self.style.SUCCESS(f'已完成迁移，更新了 {updated_count} 个用户的UUID'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'迁移过程中出错: {str(e)}'))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close() 