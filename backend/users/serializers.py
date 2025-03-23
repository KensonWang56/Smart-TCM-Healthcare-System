from rest_framework import serializers
from django.contrib.auth import get_user_model
import re

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    class Meta:
        model = User
        fields = ['uid', 'username', 'email', 'create_time', 'last_login_time', 'has_face', 'avatar', 'need_change_password']
        read_only_fields = ['uid', 'create_time', 'last_login_time', 'has_face']

class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate_username(self, value):
        """验证用户名"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        if not 3 <= len(value) <= 20:
            raise serializers.ValidationError("用户名长度应在3到20个字符之间")
        return value
    
    def validate_password(self, value):
        """验证密码"""
        if not 6 <= len(value) <= 20:
            raise serializers.ValidationError("密码长度应为6-20个字符")
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise serializers.ValidationError("密码只能包含英文字母和数字")
        return value
    
    def validate(self, data):
        """验证密码一致性"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "两次输入的密码不一致"})
        return data
    
    def create(self, validated_data):
        """创建用户"""
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

class PasswordChangeSerializer(serializers.Serializer):
    """密码修改序列化器"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    
    def validate_new_password(self, value):
        """验证新密码"""
        if not 6 <= len(value) <= 20:
            raise serializers.ValidationError("密码长度应为6-20个字符")
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise serializers.ValidationError("密码只能包含英文字母和数字")
        return value
    
    def validate(self, data):
        """验证新密码与确认密码一致"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "两次输入的密码不一致"})
        return data

class UserUpdateSerializer(serializers.ModelSerializer):
    """用户信息更新序列化器"""
    class Meta:
        model = User
        fields = ['username', 'email']
    
    def validate_username(self, value):
        """验证用户名"""
        user = self.context['request'].user
        if User.objects.filter(username=value).exclude(uid=user.uid).exists():
            raise serializers.ValidationError("用户名已存在")
        if not 3 <= len(value) <= 20:
            raise serializers.ValidationError("用户名长度应在3到20个字符之间")
        return value 