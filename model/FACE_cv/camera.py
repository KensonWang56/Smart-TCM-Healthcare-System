import cv2
import numpy as np
import torch
from model import FaceRecognitionModel
from config import DB_CONFIG
import time
from PIL import Image

class FaceDetectionCamera:
    def __init__(self, camera_id=0):
        """
        初始化摄像头检测类
        
        Args:
            camera_id: 摄像头ID，默认为0（通常是笔记本内置摄像头）
        """
        self.camera_id = camera_id
        self.model = FaceRecognitionModel(DB_CONFIG)
        self.cap = None
        
    def start(self):
        """启动摄像头"""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise Exception("无法打开摄像头")
    
    def stop(self):
        """停止摄像头"""
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()
    
    def get_frame(self):
        """获取一帧图像"""
        if not self.cap:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        return frame
    
    def process_frame(self, frame, threshold=0.6):
        """
        处理单帧图像
        
        Args:
            frame: 图像帧
            threshold: 相似度阈值
            
        Returns:
            processed_frame: 处理后的图像
            face_results: 识别结果列表，每个元素为(名字, 相似度)
        """
        # 识别人脸
        results = self.model.recognize_face(frame, threshold)
        
        # 获取人脸位置
        faces = self.model.mtcnn.detect(frame)
        if faces[0] is not None:
            boxes = faces[0]
            
            # 在图像上绘制结果
            for (box, (name, similarity)) in zip(boxes, results):
                x1, y1, x2, y2 = [int(b) for b in box]
                
                # 绘制边框
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # 绘制文本
                text = f"{name} ({similarity:.2f})"
                cv2.putText(
                    frame,
                    text,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )
        
        return frame, results
    
    def verify_face(self, target_name, min_similarity=0.5, timeout=10):
        """
        验证特定人脸
        
        Args:
            target_name: 目标人名
            min_similarity: 最小相似度要求
            timeout: 超时时间（秒）
            
        Returns:
            bool: 是否验证成功
            float: 最高相似度
        """
        start_time = time.time()
        max_similarity = 0.0
        
        while time.time() - start_time < timeout:
            frame = self.get_frame()
            if frame is None:
                continue
                
            _, face_results = self.process_frame(frame)
            
            for name, similarity in face_results:
                if name == target_name:
                    max_similarity = max(max_similarity, similarity)
                    if similarity >= min_similarity:
                        return True, similarity
        
        return False, max_similarity 