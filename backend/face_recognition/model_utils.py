import torch
import warnings
from facenet_pytorch import MTCNN, InceptionResnetV1

def load_face_models(device):
    """
    加载人脸检测和识别模型
    
    Args:
        device: torch.device 对象，指定运行设备
        
    Returns:
        tuple: (MTCNN模型, InceptionResnetV1模型)
    """
    # 临时禁用警告
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        
        # 初始化MTCNN
        mtcnn = MTCNN(
            keep_all=True,
            device=device,
            selection_method='probability'
        )
        
        # 初始化InceptionResnetV1
        resnet = InceptionResnetV1(
            pretrained='vggface2'
        ).to(device).eval()
        
    return mtcnn, resnet 