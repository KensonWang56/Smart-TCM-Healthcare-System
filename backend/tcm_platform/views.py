from django.shortcuts import render, redirect
from django.http import JsonResponse

def index(request):
    """首页视图"""
    return JsonResponse({
        'status': 'success',
        'message': '中医药综合服务平台API服务正常运行',
        'endpoints': {
            'admin': '/admin/',
            'api': {
                'auth': '/api/auth/',
                'user': '/api/user/',
                'herbs': '/api/herbs/',
                'tongue': '/api/tongue/',
                'chat': '/api/chat/',
                'knowledge': '/api/knowledge/',
            }
        }
    }) 