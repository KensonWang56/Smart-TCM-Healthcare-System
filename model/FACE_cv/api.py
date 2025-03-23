from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from PIL import Image
import io
import os
from model import FaceRecognitionModel
from config import DB_CONFIG, STORAGE_CONFIG
from typing import List
import mysql.connector

app = FastAPI(
    title="人脸识别系统",
    description="基于深度学习的人脸识别系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/face_photos", StaticFiles(directory=STORAGE_CONFIG['photo_dir']), name="face_photos")

# 初始化模型
model = FaceRecognitionModel(DB_CONFIG)

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    返回主页
    """
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"无法加载主页: {str(e)}")

@app.get("/favicon.ico")
async def favicon():
    """
    返回网站图标
    """
    return FileResponse("static/favicon.ico")

@app.post("/register")
async def register_face(
    name: str = Form(...),
    photo: UploadFile = File(...),
    make_primary: bool = Form(True)
):
    """
    注册新的人脸
    """
    try:
        # 读取上传的图片
        contents = await photo.read()
        image = Image.open(io.BytesIO(contents))
        
        # 保存临时文件
        temp_path = f"temp_{photo.filename}"
        image.save(temp_path)
        
        # 添加人脸
        success = model.add_face(temp_path, name, make_primary)
        
        # 删除临时文件
        os.remove(temp_path)
        
        if success:
            return {"status": "success", "message": f"成功注册用户 {name} 的人脸"}
        else:
            raise HTTPException(status_code=400, detail="未能检测到有效的人脸")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/photos")
async def get_user_photos(user_id: int):
    """
    获取用户的所有照片
    """
    try:
        photos = model.get_user_photos(user_id)
        return {"status": "success", "photos": photos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/photos/{photo_id}/set-primary")
async def set_primary_photo(photo_id: int):
    """
    设置主要照片
    """
    try:
        success = model.set_primary_photo(photo_id)
        if success:
            return {"status": "success", "message": "已成功设置主要照片"}
        else:
            raise HTTPException(status_code=404, detail="未找到指定的照片")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify")
async def verify_face(photo: UploadFile = File(...)):
    """
    验证人脸
    
    Returns:
        dict: {
            "status": "success",
            "matches": [
                {
                    "name": str,  # 匹配到的用户名
                    "confidence": float  # 相似度（0-1）
                }
            ]
        }
    """
    try:
        # 读取上传的图片
        contents = await photo.read()
        image = Image.open(io.BytesIO(contents))
        
        # 保存临时文件
        temp_path = f"temp_{photo.filename}"
        image.save(temp_path)
        
        # 识别人脸
        results = model.recognize_face(image, threshold=0.6)  # 设置阈值为0.6
        
        # 删除临时文件
        os.remove(temp_path)
        
        if results:
            # 返回识别结果
            return {
                "status": "success",
                "matches": [
                    {
                        "name": name,
                        "confidence": float(confidence),
                        "verified": float(confidence) >= 0.6  # 添加验证结果
                    }
                    for name, confidence in results
                ]
            }
        else:
            raise HTTPException(status_code=400, detail="未能检测到有效的人脸或无匹配结果")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/photos/{name}")
async def get_user_photos_by_name(name: str):
    """
    通过用户名获取照片
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 先获取用户ID
        cursor.execute(
            "SELECT id FROM users WHERE name = %s",
            (name,)
        )
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="未找到该用户")
            
        # 获取用户的所有照片
        cursor.execute("""
            SELECT fp.id, fp.photo_path, fp.is_primary, fp.created_at 
            FROM face_photos fp
            WHERE fp.user_id = %s 
            ORDER BY fp.created_at DESC
        """, (user['id'],))
        
        photos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"status": "success", "photos": photos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # 确保必要的目录存在
    os.makedirs("static", exist_ok=True)
    os.makedirs(STORAGE_CONFIG['photo_dir'], exist_ok=True)
    
    # 创建默认的favicon.ico
    if not os.path.exists("static/favicon.ico"):
        # 创建一个1x1像素的透明图片作为默认图标
        img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        img.save("static/favicon.ico", format="ICO")
    
    # 启动服务器
    uvicorn.run(
        "api:app",  # 使用字符串形式指定应用
        host="127.0.0.1",
        port=8000,
        reload=True,  # 启用自动重载
        reload_dirs=["./"],  # 监视当前目录的文件变化
        workers=1  # 开发模式使用单个工作进程
    )