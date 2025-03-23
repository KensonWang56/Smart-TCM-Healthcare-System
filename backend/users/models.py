from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import os
import re

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('用户名不能为空')
        if not email:
            raise ValueError('邮箱不能为空')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """自定义用户模型"""
    uid = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30, unique=True, verbose_name='用户名')
    email = models.EmailField(unique=True, verbose_name='邮箱')
    create_time = models.DateField(auto_now_add=True, verbose_name='创建时间')
    last_login_time = models.DateTimeField(null=True, blank=True, verbose_name='最后登录时间')
    has_face = models.BooleanField(default=False, verbose_name='是否设置人脸登录')
    face_image = models.CharField(max_length=255, null=True, blank=True, verbose_name='人脸图片路径')
    avatar = models.CharField(max_length=255, null=True, blank=True, verbose_name='头像路径')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    need_change_password = models.BooleanField(default=False, verbose_name='是否需要修改密码')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        return self.username
    
    def check_password_strength(self, password):
        """检查密码强度"""
        if len(password) < 6 or len(password) > 20:
            return False, '密码长度应为6-20个字符'
        
        if not re.match(r'^[a-zA-Z0-9]+$', password):
            return False, '密码只能包含英文字母和数字'
        
        return True, '密码符合要求'
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login_time = timezone.now()
        self.save(update_fields=['last_login_time']) 