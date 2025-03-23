from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class KnowledgeView(APIView):
    def get(self, request, category=None):
        try:
            # 模拟知识库数据
            knowledge_data = {
                'yin-yang': {
                    'title': '阴阳五行理论',
                    'content': """
                    <h3>阴阳理论概述</h3>
                    <p>阴阳学说是中医学的理论基础之一，它认为世界上的一切事物和现象都可以分为阴阳两个对立的方面。阴阳既对立又统一，相互依存、相互制约、相互转化。</p>
                    
                    <h3>五行理论基础</h3>
                    <p>五行学说是中医学的另一个重要理论基础，它以金、木、水、火、土五种物质的特性和相互关系来解释自然界和人体的生理、病理变化规律。</p>
                    
                    <h3>在中医诊断中的应用</h3>
                    <p>阴阳五行理论在中医诊断中具有重要的指导意义：</p>
                    <ul>
                        <li>通过阴阳理论分析疾病的性质</li>
                        <li>运用五行理论判断脏腑功能的相互关系</li>
                        <li>指导临床辨证施治</li>
                    </ul>""",
                    'references': [
                        '《黄帝内经》',
                        '《中医基础理论》',
                        '《中医诊断学》'
                    ],
                    'related': [
                        {
                            'id': 'zang-fu',
                            'title': '脏腑理论',
                            'description': '了解人体五脏六腑的功能与关系',
                            'icon': 'Stethoscope'
                        },
                        {
                            'id': 'meridians',
                            'title': '经络学说',
                            'description': '探索人体经络系统的分布规律',
                            'icon': 'Connection'
                        }
                    ]
                },
                'zang-fu': {
                    'title': '脏腑理论',
                    'content': """
                    <h3>五脏的生理功能</h3>
                    <p>五脏包括心、肝、脾、肺、肾，各有其特定的生理功能：</p>
                    <ul>
                        <li>心：主血脉，藏神</li>
                        <li>肝：主疏泄，藏血</li>
                        <li>脾：主运化，藏意</li>
                        <li>肺：主气，朝百脉</li>
                        <li>肾：主水，藏精</li>
                    </ul>
                    
                    <h3>六腑的功能特点</h3>
                    <p>六腑包括胆、胃、小肠、大肠、膀胱、三焦，主要功能是传化物质。</p>""",
                    'references': [
                        '《中医基础理论》',
                        '《脏腑学说》'
                    ],
                    'related': [
                        {
                            'id': 'meridians',
                            'title': '经络学说',
                            'description': '了解经络与脏腑的关系',
                            'icon': 'Connection'
                        }
                    ]
                }
            }

            if category and category in knowledge_data:
                return Response(knowledge_data[category], status=status.HTTP_200_OK)
            elif not category:
                return Response(list(knowledge_data.keys()), status=status.HTTP_200_OK)
            else:
                return Response({'error': '未找到相关知识'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 