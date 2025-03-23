# 中医系统安装与运行说明文档

## 系统要求

- Python 3.x (推荐使用 Anaconda)
- MySQL 数据库
- Node.js 和 npm
- GPU支持（可选，用于加速人脸识别）

## 后端安装与配置

### 1. 配置 MySQL 数据库

1. 安装 MySQL（如未安装）
2. 打开MySQL并创建数据库：
   ```sql
   CREATE DATABASE tcm_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. 确保数据库用户名和密码与设置文件匹配（默认用户名: `root`，密码: `123456`）
4. 如果有数据库连接问题，请检查 `backend/tcm_platform/settings.py` 中的数据库配置是否正确

### 2. 配置 Python 环境

1. 打开 Anaconda Prompt
2. 创建新的虚拟环境：
   ```
   conda create -n tcm_env python=3.9
   ```
3. 激活环境：
   ```
   conda activate tcm_env
   ```

### 3. 安装后端依赖

1. 切换到后端目录：

   ```
   cd 路径/到项目/backend
   ```
2. 安装基本依赖包：

   ```
   pip install -r requirements.txt
   ```
3. 安装人脸识别相关库：

   ```
   # 安装PyTorch（GPU版本，如果有NVIDIA GPU）
   conda install pytorch torchvision cudatoolkit=11.3 -c pytorch

   # 或安装PyTorch（CPU版本，如果没有GPU）
   conda install pytorch torchvision cpuonly -c pytorch

   # 安装人脸识别必要的库
   pip install facenet-pytorch>=2.5.2
   pip install opencv-python-headless>=4.5.0
   pip install pillow>=8.0.0
   pip install numpy>=1.19.0
   ```

### 4. 数据库迁移

1. 在激活的虚拟环境中，运行以下命令创建数据库表：
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

### 5. 启动后端服务器

在激活的虚拟环境中：

```
python manage.py runserver
```

后端服务器将在 http://127.0.0.1:8000/ 运行。

## 前端安装与配置

### 1. 安装依赖

1. 打开命令提示符 (CMD)
2. 切换到前端目录：
   ```
   cd 路径/到项目/frontend
   ```
3. 安装依赖：
   ```
   npm install
   ```

### 2. 启动前端开发服务器

```
npm run dev
```

前端将在 http://localhost:5173/ 运行（具体端口可能会有所不同，请查看终端输出）。

## 注意事项

1. 确保后端服务器在前端运行之前已启动
2. 如果有数据库连接问题，请检查 `backend/tcm_platform/settings.py` 中的数据库配置是否正确
3. 系统使用了人脸识别功能，请确保安装了相关的依赖（参考安装人脸识别相关库的步骤）
4. 媒体文件存储在 `backend/media/` 目录中，请确保此目录有写入权限
5. 人脸识别使用了MTCNN和InceptionResnetV1模型，首次运行时会自动下载预训练模型

## 人脸识别模块说明

系统使用了以下模型进行人脸识别：

1. MTCNN - 用于人脸检测和对齐
2. InceptionResnetV1 (预训练模型: vggface2) - 用于生成人脸特征向量

人脸识别数据存储在以下两个数据库表中：

- `face_users` - 存储用户信息
- `face_photos` - 存储用户照片和人脸特征向量

## 常见问题排查

1. 数据库连接错误：

   - 检查 MySQL 服务是否运行
   - 验证用户名和密码是否正确
   - 确认数据库 `tcm_platform` 是否已创建
2. 依赖安装问题：

   - 对于 PyTorch 安装，请根据您的GPU情况选择正确的安装命令
   - 如果遇到 CUDA 相关错误，请确保安装了兼容的 CUDA 版本或使用 CPU 版本
   - facenet-pytorch 安装失败时，可以尝试：
     ```
     pip install facenet-pytorch --no-deps
     pip install Pillow numpy torch torchvision
     ```
3. 人脸识别问题：

   - 确保照片中有清晰的人脸
   - 检查 `backend/media/` 目录是否存在并有写入权限
   - 检查预训练模型是否正确下载（通常在用户目录的`.cache/torch/checkpoints/`）
4. 前端接口连接问题：

   - 确保后端 API 地址配置正确
   - 检查 CORS 设置
5. 权限问题：

   - Windows 下可能需要以管理员身份运行命令提示符

## 完成安装

完成上述步骤后，您应该能够通过浏览器访问系统：

- 后端 API：http://127.0.0.1:8000/
- 前端界面：http://localhost:5173/ (或终端显示的其他端口)
