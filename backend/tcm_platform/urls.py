from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import index

# 添加调试信息
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")

urlpatterns = [
    path('', index, name='index'),  # 添加首页视图
    path('admin/', admin.site.urls),
    # 注意：我们使用新的users应用替代原有的auth应用，保持API路径不变
    path('api/auth/', include('users.urls')),
    # 用户相关API
    path('api/user/', include('users.urls')),
    path('api/herbs/', include('herbs.urls')),
    path('api/tongue/', include('tongue.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/knowledge/', include('knowledge.urls')),
]

# 确保在开发环境中正确提供媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # 生产环境也添加静态文件服务
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 