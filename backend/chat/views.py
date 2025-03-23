from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sparkai.llm.llm import ChatSparkLLM
from sparkai.core.messages import BaseMessage, ChatMessage
import json
import re

class ChatView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 中医助手身份prompt
        self.system_prompt = """你是一个专业的中医智能助手，由讯飞星火大模型驱动。你的主要职责是：
1. 帮助用户解答中医相关问题，包括中医理论、诊断方法、常见症状分析等
2. 基于中医理论为用户提供健康建议，如饮食调理、生活习惯改善、穴位按摩等自我保健方法
3. 对常见疾病提供中医视角的分析和建议
4. 解释中药材的功效与作用，以及常见中药方剂的组成和适用情况
5. 向用户普及中医养生知识

请注意：
- 保持专业、耐心的态度。
"""
        # 星火大模型配置
        self.spark = ChatSparkLLM(
            spark_api_url='wss://spark-api.xf-yun.com/chat/max-32k',
            spark_app_id='bf620b6f',
            spark_api_key='e306e8f60327283c6f44e6dd871f66dc',
            spark_api_secret='NDkwYmRlZDFlNDZmNTJlN2I2ZDk5YjJh',
            spark_llm_domain='max-32k',
            streaming=False,
        )

    def format_response(self, text):

        text = re.sub(r'\s+$', '', text, flags=re.MULTILINE) 
        
        pattern = r'^([^\n#:：]{2,})[:：]\s*\n(.*?)(?=\n\s*\n|\n[^\n:：]{2,}[:：]|$)'
        
        def format_title_content(match):
            title = match.group(1).strip()
            content = match.group(2).strip()
            # 将标题转换为Markdown的h3格式
            return f"### {title}\n\n{content}"

        text = re.sub(pattern, format_title_content, text, flags=re.MULTILINE | re.DOTALL)

        text = re.sub(r'^\s*[:：]\s*\n', '', text, flags=re.MULTILINE)

        text = re.sub(r'^([^\n#:：]{2,})[:：]\s*$', r'### \1', text, flags=re.MULTILINE)

        text = re.sub(r'^\s*-\s+(.+?)$', r'- \1', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*(\d+)\.\s+\*\*([^*]+?)\*\*:?', r'\1. \2', text, flags=re.MULTILINE)

        text = re.sub(r'\*\*([^*\n]+?)\*\*:?', r'**\1**', text)

        text = re.sub(r'(\n- [^\n]+)(\n- )', r'\1\n\2', text)

        text = re.sub(r'\n{3,}', '\n\n', text)

        text = re.sub(r'(### [^\n]+)\n([^\n])', r'\1\n\n\2', text)

        text = re.sub(r'([^\n])\n([^\n#\-])', r'\1\n\n\2', text)
        
        return text
    def post(self, request):
        try:
            message = request.data.get('message')
            if not message:
                return Response({'error': '消息不能为空'}, status=status.HTTP_400_BAD_REQUEST)

            messages: list[BaseMessage] = [
                ChatMessage(
                    role="system",
                    content=self.system_prompt
                ),
                ChatMessage(
                    role="user",
                    content=message
                )
            ]
            
            # 发送请求到星火API
            result = self.spark.generate([messages])
            
            # 提取响应内容并格式化
            response = result.generations[0][0].text
            formatted_response = self.format_response(response)
            
            return Response({'response': formatted_response}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
