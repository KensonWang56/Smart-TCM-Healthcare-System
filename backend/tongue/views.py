from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
import io
import logging
from sparkai.llm.llm import ChatSparkLLM  # 直接从正确的路径导入
from sparkai.core.messages import BaseMessage, ChatMessage  # 添加必要的导入

logger = logging.getLogger(__name__)

class TongueAnalysisView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            # 初始化星火大模型
            self.spark = ChatSparkLLM(
                spark_api_url='wss://spark-api.xf-yun.com/chat/max-32k',
                spark_app_id='bf620b6f',
                spark_api_key='e306e8f60327283c6f44e6dd871f66dc',
                spark_api_secret='NDkwYmRlZDFlNDZmNTJlN2I2ZDk5YjJh',
                spark_llm_domain='max-32k',
                streaming=False,
            )
        except Exception as e:
            logger.error(f"初始化星火大模型失败: {str(e)}")
            raise

    def get_ai_suggestions(self, diagnosis_result):
        try:
            prompt = f"""
            基于以下舌诊结果给出建议：
            舌质：{diagnosis_result['tongueBody']}
            舌苔：{diagnosis_result['tongueCoating']}
            舌色：{diagnosis_result['tongueColor']}
            主要症候：{diagnosis_result['mainSymptoms']}
            
            请给出3条简短建议（每条15字以内）和7味推荐中药（只需要药名）。
            回复格式：
            建议：
            1. [建议1]
            2. [建议2]
            3. [建议3]
            
            推荐中药：
            [药名1]、[药名2]、[药名3]、[药名4]、[药名5]、[药名6]、[药名7]
            给出的建议和药名不要带[]。
            """
            
            messages = [ChatMessage(  # 使用正确的消息格式
                role="user",
                content=prompt
            )]
            
            result = self.spark.generate([messages])
            return result.generations[0][0].text
        except Exception as e:
            logger.error(f"获取AI建议失败: {str(e)}")
            return "AI建议获取失败，请稍后重试"

    def post(self, request):
        try:
            # 获取上传的舌苔图片
            image_file = request.FILES.get('image')
            if not image_file:
                return Response({'error': '未找到上传的图片'}, status=status.HTTP_400_BAD_REQUEST)

            # 打印接收到的文件信息
            logger.info(f"接收到文件: {image_file.name}, 大小: {image_file.size}")

            # 读取和预处理图片
            image = Image.open(io.BytesIO(image_file.read()))
            # TODO: 实现实际的舌诊分析逻辑

            # 模拟分析结果
            analysis_result = {
                'tongueBody': '舌质淡红，略胖大',
                'tongueCoating': '薄白苔',
                'tongueColor': '淡红色',
                'mainSymptoms': '脾胃虚弱，气血不足'
            }

            # 调用星火大模型获取建议
            ai_suggestions = self.get_ai_suggestions(analysis_result)
            analysis_result['aiSuggestions'] = ai_suggestions

            return Response(analysis_result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"舌诊分析失败: {str(e)}")
            return Response(
                {'error': f'服务器处理错误: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 