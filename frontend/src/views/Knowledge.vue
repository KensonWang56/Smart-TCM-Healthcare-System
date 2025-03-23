<template>
  <div class="knowledge-base">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="category-card">
          <template #header>
            <div class="card-header">
              <h3>知识分类</h3>
            </div>
          </template>
          <el-menu
            :default-active="activeCategory"
            class="category-menu"
            @select="handleCategorySelect">
            <el-sub-menu index="theory">
              <template #title>
                <el-icon><Document /></el-icon>
                <span>中医理论</span>
              </template>
              <el-menu-item index="yin-yang">阴阳五行</el-menu-item>
              <el-menu-item index="zang-fu">脏腑理论</el-menu-item>
              <el-menu-item index="meridians">经络学说</el-menu-item>
            </el-sub-menu>
            <el-sub-menu index="diagnosis">
              <template #title>
                <el-icon><Stethoscope /></el-icon>
                <span>诊断方法</span>
              </template>
              <el-menu-item index="look">望诊</el-menu-item>
              <el-menu-item index="listen-smell">闻诊</el-menu-item>
              <el-menu-item index="ask">问诊</el-menu-item>
              <el-menu-item index="pulse">切诊</el-menu-item>
            </el-sub-menu>
            <el-sub-menu index="herbs">
              <template #title>
                <el-icon><Monitor /></el-icon>
                <span>中药学</span>
              </template>
              <el-menu-item index="herb-nature">药性理论</el-menu-item>
              <el-menu-item index="common-herbs">常用中药</el-menu-item>
              <el-menu-item index="formulas">方剂学</el-menu-item>
            </el-sub-menu>
          </el-menu>
        </el-card>
      </el-col>
      <el-col :span="18">
        <el-card class="content-card">
          <template #header>
            <div class="content-header">
              <h2>{{ currentContent.title }}</h2>
            </div>
          </template>
          <div class="content-body" v-loading="loading">
            <div class="article-content" v-html="currentContent.content"></div>
            <div v-if="currentContent.references" class="references">
              <h3>参考资料</h3>
              <ul>
                <li v-for="(ref, index) in currentContent.references" :key="index">
                  {{ ref }}
                </li>
              </ul>
            </div>
            <div class="related-content">
              <h3>相关内容</h3>
              <el-row :gutter="20">
                <el-col :span="8" v-for="item in currentContent.related" :key="item.id">
                  <el-card class="related-card" shadow="hover" @click="loadContent(item.id)">
                    <div class="related-card-content">
                      <el-icon :size="24" class="related-icon">
                        <component :is="item.icon" />
                      </el-icon>
                      <h4>{{ item.title }}</h4>
                      <p>{{ item.description }}</p>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  Document,
  Monitor,
  Share,
  Download,
  FirstAidKit as Stethoscope
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getKnowledgeDetail } from '@/api/knowledge'

// 先定义 getRelatedContent 函数
const getRelatedContent = (currentId) => {
  const relatedMap = {
    'yin-yang': [
      {
        id: 'zang-fu',
        title: '脏腑理论',
        description: '五脏六腑的功能与关系',
        icon: 'FirstAidKit'
      },
      {
        id: 'meridians',
        title: '经络学说',
        description: '十二经脉与奇经八脉',
        icon: 'Document'
      },
      {
        id: 'herb-nature',
        title: '药性理论',
        description: '中药四性五味',
        icon: 'Monitor'
      }
    ],
    'zang-fu': [
      {
        id: 'yin-yang',
        title: '阴阳五行',
        description: '中医基础理论',
        icon: 'Document'
      },
      {
        id: 'meridians',
        title: '经络学说',
        description: '十二经脉与奇经八脉',
        icon: 'Monitor'
      },
      {
        id: 'herb-nature',
        title: '药性理论',
        description: '中药四性五味',
        icon: 'FirstAidKit'
      }
    ],
    'look': [
      {
        id: 'listen-smell',
        title: '闻诊',
        description: '听声音、嗅气味的诊断方法',
        icon: 'FirstAidKit'
      },
      {
        id: 'ask',
        title: '问诊',
        description: '通过询问了解病情',
        icon: 'Document'
      },
      {
        id: 'pulse',
        title: '切诊',
        description: '脉诊与按诊',
        icon: 'Monitor'
      }
    ],
    'listen-smell': [
      {
        id: 'look',
        title: '望诊',
        description: '观察神色、舌象等',
        icon: 'Document'
      },
      {
        id: 'ask',
        title: '问诊',
        description: '通过询问了解病情',
        icon: 'FirstAidKit'
      },
      {
        id: 'pulse',
        title: '切诊',
        description: '脉诊与按诊',
        icon: 'Monitor'
      }
    ],
    'ask': [
      {
        id: 'look',
        title: '望诊',
        description: '观察神色、舌象等',
        icon: 'Document'
      },
      {
        id: 'listen-smell',
        title: '闻诊',
        description: '听声音、嗅气味的诊断方法',
        icon: 'FirstAidKit'
      },
      {
        id: 'pulse',
        title: '切诊',
        description: '脉诊与按诊',
        icon: 'Monitor'
      }
    ],
    'pulse': [
      {
        id: 'look',
        title: '望诊',
        description: '观察神色、舌象等',
        icon: 'Document'
      },
      {
        id: 'listen-smell',
        title: '闻诊',
        description: '听声音、嗅气味的诊断方法',
        icon: 'FirstAidKit'
      },
      {
        id: 'ask',
        title: '问诊',
        description: '通过询问了解病情',
        icon: 'Monitor'
      }
    ],
    'herb-nature': [
      {
        id: 'common-herbs',
        title: '常用中药',
        description: '中药的分类与应用',
        icon: 'Document'
      },
      {
        id: 'formulas',
        title: '方剂学',
        description: '中药方剂的组成与应用',
        icon: 'Monitor'
      },
      {
        id: 'zang-fu',
        title: '脏腑理论',
        description: '五脏六腑的功能与关系',
        icon: 'FirstAidKit'
      }
    ],
    'common-herbs': [
      {
        id: 'herb-nature',
        title: '药性理论',
        description: '中药四气五味',
        icon: 'Document'
      },
      {
        id: 'formulas',
        title: '方剂学',
        description: '中药方剂的组成与应用',
        icon: 'Monitor'
      },
      {
        id: 'meridians',
        title: '经络学说',
        description: '十二经脉与归经',
        icon: 'FirstAidKit'
      }
    ],
    'formulas': [
      {
        id: 'herb-nature',
        title: '药性理论',
        description: '中药四气五味',
        icon: 'Document'
      },
      {
        id: 'common-herbs',
        title: '常用中药',
        description: '中药的分类与应用',
        icon: 'Monitor'
      },
      {
        id: 'zang-fu',
        title: '脏腑理论',
        description: '五脏六腑的功能与关系',
        icon: 'FirstAidKit'
      }
    ],
    'meridians': [
      {
        id: 'yin-yang',
        title: '阴阳五行',
        description: '中医基础理论',
        icon: 'Document'
      },
      {
        id: 'zang-fu',
        title: '脏腑理论',
        description: '五脏六腑的功能与关系',
        icon: 'FirstAidKit'
      },
      {
        id: 'common-herbs',
        title: '常用中药',
        description: '中药的应用与分类',
        icon: 'Monitor'
      }
    ]
  }
  return relatedMap[currentId] || []
}

// 然后定义 knowledgeContent
const knowledgeContent = {
  'yin-yang': {
    title: '阴阳五行理论',
    content: `
    <h3>阴阳理论概述</h3>
    <p>阴阳学说是中医学的理论基础之一，它认为世界上的一切事物和现象都可以分为阴阳两个对立的方面。阴阳既对立又统一，相互依存、相互制约、相互转化。</p>
    
    <h3>五行理论基础</h3>
    <p>五行学说是中医学的另一个重要理论基础，它以金、木、水、火、土五种物质的特性和相互关系来解释自然界和人体的生理、病理变化规律。</p>
    
    <h3>五行的特性与关系</h3>
    <ul>
      <li>木：生发、升发，主疏泄</li>
      <li>火：温热、上炎，主温煦</li>
      <li>土：生化、承载，主运化</li>
      <li>金：肃降、收敛，主清肃</li>
      <li>水：寒凉、润下，主滋润</li>
    </ul>

    <h3>五行的生克关系</h3>
    <p>相生关系：木生火、火生土、土生金、金生水、水生木</p>
    <p>相克关系：木克土、土克水、水克火、火克金、金克木</p>
    
    <h3>在中医诊断中的应用</h3>
    <p>阴阳五行理论在中医诊断中具有重要的指导意义：</p>
    <ul>
      <li>通过阴阳理论分析疾病性质</li>
      <li>运用五行理论判断脏腑功能的相互关系</li>
      <li>指导临床辨证施治</li>
    </ul>

    <h3>临床应用举例</h3>
    <p>例如：肝属木，心属火。当肝气郁结时，可能会导致"木火刑金"，出现肺系症状。治疗时可以通过疏肝理气来改善症状。</p>
    `,
    references: [
      '《黄帝内经》',
      '《中医基础理论》',
      '《中医诊断学》',
      '《伤寒论》',
      '《温病条辨》'
    ]
  },
  'zang-fu': {
    title: '脏腑理论',
    content: `
      <h3>五脏的生理功能</h3>
      <ul>
        <li>心：主血脉、藏神</li>
        <li>肝：主疏泄、藏血</li>
        <li>脾：主运化、统血</li>
        <li>肺：主气、司呼吸</li>
        <li>肾：主水、藏精</li>
      </ul>

      <h3>六腑的功能特点</h3>
      <ul>
        <li>胆：主决断、贮存胆汁</li>
        <li>胃：受纳腐熟水谷</li>
        <li>小肠：分清别浊</li>
        <li>大肠：传导糟粕</li>
        <li>膀胱：贮存排泄尿液</li>
        <li>三焦：决渎通调水道</li>
      </ul>
    `,
    references: ['《内经》', '《难经》', '《中医基础理论》'],
  },
  'meridians': {
    title: '经络学说',
    content: `
      <h3>十二正经</h3>
      <p>手三阴经：手太阴肺经、手少阴心经、手厥阴心包经</p>
      <p>手三阳经：手阳明大肠经、手太阳小肠经、手少阳三焦经</p>
      <p>足三阴经：足太阴脾经、足少阴肾经、足厥阴肝经</p>
      <p>足三阳经：足阳明胃经、足太阳膀胱经、足少阳胆经</p>

      <h3>奇经八脉</h3>
      <ul>
        <li>督脉：阳脉之海</li>
        <li>任脉：阴脉之海</li>
        <li>冲脉：十二经脉之海</li>
        <li>带脉：约束诸经</li>
        <li>阴维脉：总统阴经</li>
        <li>阳维脉：总统阳经</li>
        <li>阴跷脉：会于足少阴</li>
        <li>阳跷脉：会于足太阳</li>
      </ul>
    `,
    references: ['《灵枢》', '《针灸学》'],
  },
  'look': {
    title: '望诊',
    content: `
      <h3>望诊概述</h3>
      <p>望诊是中医四诊之一，是通过医者的视觉观察患者的神色、形态、舌象等来判断疾病的诊断方法。</p>

      <h3>望神</h3>
      <ul>
        <li>得神：精神充沛，病情轻浅或康复</li>
        <li>失神：精神萎靡，病情严重</li>
        <li>假神：危重病人暂时出现的假性好转</li>
      </ul>

      <h3>望面色</h3>
      <ul>
        <li>青色：主肝病或疼痛</li>
        <li>红色：主热证</li>
        <li>黄色：主脾胃病或湿证</li>
        <li>白色：主气血两虚或寒证</li>
        <li>黑色：主肾病或水气病</li>
      </ul>

      <h3>望舌象</h3>
      <p>舌诊包括观察舌质和舌苔两个方面：</p>
      <h4>舌质</h4>
      <ul>
        <li>淡红舌：正常舌色</li>
        <li>淡白舌：气血两虚</li>
        <li>红舌：热证</li>
        <li>绛舌：热重血瘀</li>
        <li>青紫舌：血瘀或寒凝</li>
      </ul>
      <h4>舌苔</h4>
      <ul>
        <li>薄白苔：正常</li>
        <li>厚腻苔：湿浊</li>
        <li>黄苔：热证</li>
        <li>黑苔：重症或寒证</li>
      </ul>

      <h3>望形态</h3>
      <p>观察病人的体型、姿态、动作、皮肤等外在表现：</p>
      <ul>
        <li>形体强壮：正气充足</li>
        <li>形体消瘦：气血亏虚</li>
        <li>浮肿：水液代谢障碍</li>
        <li>畸形：筋骨损伤或发育异常</li>
      </ul>
    `,
    references: [
      '《望诊》',
      '《中医诊断学》',
      '《舌诊图谱》',
      '《四诊心法要诀》'
    ]
  },
  'listen-smell': {
    title: '闻诊',
    content: `
      <h3>闻诊概述</h3>
      <p>闻诊包括听声音和嗅气味两个方面，是中医四诊之一。通过病人的声音、呼吸和各种异常气味来诊断疾病。</p>

      <h3>听声音</h3>
      <h4>言语声音</h4>
      <ul>
        <li>声高气粗：阳证、实证</li>
        <li>声低气怯：阴证、虚证</li>
        <li>声哑：肺气亏虚或热伤声音</li>
        <li>懒言：气虚或神疲</li>
      </ul>

      <h4>呼吸声音</h4>
      <ul>
        <li>喘促：气道阻塞或肺气不足</li>
        <li>气短：气虚或血虚</li>
        <li>哮鸣：痰阻气道</li>
        <li>鼾声：痰浊阻塞</li>
      </ul>

      <h3>嗅气味</h3>
      <h4>口气</h4>
      <ul>
        <li>腥臭：胃热</li>
        <li>酸臭：食积</li>
        <li>甜腻：痰湿</li>
      </ul>

      <h4>体味</h4>
      <ul>
        <li>特殊腥臭：癌症</li>
        <li>尿臭：尿毒症</li>
        <li>酸臭：湿热</li>
      </ul>

      <h3>临床意义</h3>
      <p>闻诊在某些疾病的诊断中具有重要价值：</p>
      <ul>
        <li>糖尿病患者常有特殊的水果味</li>
        <li>肝病患者可能有特殊的肝臭味</li>
        <li>某些传染病有特征性气味</li>
      </ul>
    `,
    references: [
      '《中医诊断学》',
      '《四诊心法要诀》',
      '《金匮要略》',
      '《诊法入门》'
    ]
  },
  'ask': {
    title: '问诊',
    content: `
      <h3>问诊概述</h3>
      <p>问诊是中医四诊之一，通过询问患者的症状、病史等信息来了解疾病的发生、发展过程及现状，是中医诊断的重要方法。</p>

      <h3>问诊内容</h3>
      <h4>主诉</h4>
      <ul>
        <li>发病时间</li>
        <li>主要症状</li>
        <li>发病诱因</li>
        <li>病情演变</li>
      </ul>

      <h4>十问要点</h4>
      <ul>
        <li>寒热：感受寒热、畏寒发热等</li>
        <li>汗：自汗、盗汗、无汗等</li>
        <li>头身：头痛、眩晕、身痛等</li>
        <li>胸腹：胸闷、腹痛、腹胀等</li>
        <li>二便：大小便异常情况</li>
        <li>饮食：食欲、口味、饮水等</li>
        <li>睡眠：失眠、多梦、嗜睡等</li>
        <li>耳目：视听异常、目赤等</li>
        <li>男女：月经、带下、性功能等</li>
        <li>病史：既往病史、家族病史等</li>
      </ul>

      <h3>问诊方法</h3>
      <ul>
        <li>以虚心和蔼的态度询问</li>
        <li>注意询问的逻辑性和系统性</li>
        <li>针对不同患者采用适当的语言方式</li>
        <li>注意观察患者的表情和反应</li>
      </ul>

      <h3>注意事项</h3>
      <ul>
        <li>避免诱导性提问</li>
        <li>注意保护患者隐私</li>
        <li>对特殊人群要采取适当方式</li>
        <li>重视细节信息的收集</li>
      </ul>
    `,
    references: [
      '《中医诊断学》',
      '《四诊心法要诀》',
      '《临床问诊要点》',
      '《黄帝内经·诊法》'
    ]
  },
  'pulse': {
    title: '切诊',
    content: `
      <h3>切诊概述</h3>
      <p>切诊是中医四诊之一，主要包括脉诊和按诊两大部分，通过医者手指的触摸来了解患者的病情。</p>

      <h3>脉诊</h3>
      <h4>寸口脉的位置</h4>
      <ul>
        <li>寸：食指所按处，主心肺</li>
        <li>关：中指所按处，主脾胃</li>
        <li>尺：无名指所按处，主肾命</li>
      </ul>

      <h4>二十八脉象</h4>
      <ul>
        <li>浮脉：如物浮水面</li>
        <li>沉脉：沉伏于筋骨之间</li>
        <li>迟脉：一息不足四至</li>
        <li>数脉：一息六至以上</li>
        <li>虚脉：来势软弱无力</li>
        <li>实脉：来势充实有力</li>
      </ul>

      <h3>按诊</h3>
      <h4>腹部按诊</h4>
      <ul>
        <li>腹部柔软度</li>
        <li>压痛部位</li>
        <li>腹部温度</li>
        <li>腹部包块</li>
      </ul>

      <h4>经络按诊</h4>
      <ul>
        <li>压痛点</li>
        <li>结节</li>
        <li>硬结</li>
        <li>温度变化</li>
      </ul>

      <h3>切诊注意事项</h3>
      <ul>
        <li>保持手指温度适中</li>
        <li>注意按压力度</li>
        <li>选择合适的诊断时间</li>
        <li>考虑患者的特殊情况</li>
      </ul>
    `,
    references: [
      '《脉经》',
      '《中医诊断学》',
      '《切诊要诀》',
      '《伤寒论》'
    ]
  },
  'herb-nature': {
    title: '药性理论',
    content: `
      <h3>药性理论概述</h3>
      <p>中药药性理论是研究中药性质、功效及其临床应用规律的理论体系，主要包括四气、五味、升降浮沉、归经等内容。</p>

      <h3>四气</h3>
      <ul>
        <li>寒：清热泻火，凉血解毒</li>
        <li>热：温阳散寒，助阳回阳</li>
        <li>温：温中散寒，补火助阳</li>
        <li>凉：清热泻火，凉血止血</li>
      </ul>

      <h3>五味</h3>
      <ul>
        <li>酸味：收敛、涩滞，多入肝经</li>
        <li>苦味：泻火、燥湿，多入心经</li>
        <li>甘味：补益、和中，多入脾经</li>
        <li>辛味：发散、行气，多入肺经</li>
        <li>咸味：软坚、下气，多入肾经</li>
      </ul>

      <h3>升降浮沉</h3>
      <ul>
        <li>升：向上升发，如葱白、薄荷</li>
        <li>降：向下沉降，如枳实、大黄</li>
        <li>浮：发散表邪，如桂枝、防风</li>
        <li>沉：沉降下行，如熟地、牡蛎</li>
      </ul>

      <h3>归经</h3>
      <p>中药归经是指药物作用于人体的特定脏腑经络：</p>
      <ul>
        <li>心经药物：丹参、麦冬</li>
        <li>肝经药物：柴胡、当归</li>
        <li>脾经药物：白术、山药</li>
        <li>肺经药物：麻黄、杏仁</li>
        <li>肾经药物：熟地、山茱萸</li>
      </ul>

      <h3>毒性</h3>
      <ul>
        <li>有毒：如雄黄、砒霜</li>
        <li>大毒：如附子、乌头</li>
        <li>小毒：如半夏、天南星</li>
        <li>无毒：如人参、甘草</li>
      </ul>
    `,
    references: [
      '《神农本草经》',
      '《本草纲目》',
      '《中药学》',
      '《中医药学概论》'
    ]
  },
  'common-herbs': {
    title: '常用中药',
    content: `
      <h3>补益类</h3>
      <h4>补气药</h4>
      <ul>
        <li>人参：大补元气，复脉固脱</li>
        <li>黄芪：补气升阳，固表止汗</li>
        <li>白术：健脾益气，燥湿利水</li>
        <li>甘草：补脾益气，调和诸药</li>
      </ul>

      <h4>补血药</h4>
      <ul>
        <li>当归：补血活血，调经止痛</li>
        <li>熟地：补血养阴，滋肾填精</li>
        <li>白芍：养血柔肝，缓急止痛</li>
        <li>阿胶：补血止血，滋阴润燥</li>
      </ul>

      <h3>清热类</h3>
      <ul>
        <li>金银花：清热解毒，疏散风热</li>
        <li>黄连：清热燥湿，泻火解毒</li>
        <li>板蓝根：清热解毒，凉血利咽</li>
        <li>栀子：清热泻火，凉血降压</li>
      </ul>

      <h3>活血化瘀类</h3>
      <ul>
        <li>丹参：活血化瘀，养心安神</li>
        <li>川芎：活血行气，祛风止痛</li>
        <li>红花：活血通经，散瘀止痛</li>
        <li>桃仁：活血祛瘀，润肠通便</li>
      </ul>

      <h3>理气类</h3>
      <ul>
        <li>陈皮：理气健脾，燥湿化痰</li>
        <li>木香：行气止痛，健脾消导</li>
        <li>香附：理气解郁，调经止痛</li>
        <li>枳实：破气消积，化痰散结</li>
      </ul>

      <h3>安神类</h3>
      <ul>
        <li>酸枣仁：养心安神，敛汗生津</li>
        <li>远志：安神益智，祛痰开窍</li>
        <li>柏子仁：养心安神，润肠通便</li>
        <li>龙骨：镇惊安神，收敛固涩</li>
      </ul>
    `,
    references: [
      '《中华本草》',
      '《中药学》',
      '《常用中药手册》',
      '《中药临床应用指南》'
    ]
  },
  'formulas': {
    title: '方剂学',
    content: `
      <h3>方剂学概述</h3>
      <p>方剂学是研究中药复方配伍规律及其临床应用的学科，包括方剂的组成、配伍、剂型、用法等内容。</p>

      <h3>方剂的组成</h3>
      <h4>四药配伍</h4>
      <ul>
        <li>君药：主治主症的药物</li>
        <li>臣药：辅助君药的药物</li>
        <li>佐药：协助君臣药或制约毒性</li>
        <li>使药：引导药性到达病所</li>
      </ul>

      <h3>常用方剂类型</h3>
      <h4>解表剂</h4>
      <ul>
        <li>麻黄汤：发汗解表，宣肺平喘</li>
        <li>桂枝汤：发汗解肌，调和营卫</li>
        <li>银翘散：疏风清热，宣肺止咳</li>
      </ul>

      <h4>清热剂</h4>
      <ul>
        <li>白虎汤：清热生津，除烦止渴</li>
        <li>黄连解毒汤：清热解毒，泻火除烦</li>
        <li>清营汤：清营解毒，凉血止血</li>
      </ul>

      <h4>补益剂</h4>
      <ul>
        <li>四君子汤：补气健脾</li>
        <li>四物汤：补血调经</li>
        <li>六味地黄丸：滋阴补肾</li>
      </ul>

      <h3>方剂的用法</h3>
      <h4>剂型选择</h4>
      <ul>
        <li>汤剂：效果快，适用范围广</li>
        <li>丸剂：服用方便，作用持久</li>
        <li>散剂：服用简便，见效较快</li>
        <li>膏剂：储存方便，服用简单</li>
      </ul>

      <h3>配伍禁忌</h3>
      <ul>
        <li>十八反：如乌头反半夏</li>
        <li>十九畏：如人参畏五灵脂</li>
        <li>相须：如芍药须甘草</li>
        <li>相使：如黄芪使甘草</li>
      </ul>

      <h3>用药注意事项</h3>
      <ul>
        <li>剂量的把握</li>
        <li>服药时间的选择</li>
        <li>特殊人群用药考虑</li>
        <li>不良反应的预防</li>
      </ul>
    `,
    references: [
      '《伤寒论》',
      '《温病条辨》',
      '《方剂学》',
      '《中医处方学》'
    ]
  }
}

const activeCategory = ref('yin-yang')
const loading = ref(false)

// 最后初始化 currentContent
const currentContent = ref({
  ...knowledgeContent['yin-yang'],
  related: getRelatedContent('yin-yang')
})

// 修改 handleCategorySelect 函数
const handleCategorySelect = async (index) => {
  loading.value = true
  activeCategory.value = index  // 更新选中状态
  try {
    // 模拟API调用，实际项目中应该从后端获取
    if (knowledgeContent[index]) {
      currentContent.value = {
        ...knowledgeContent[index],
        related: getRelatedContent(index) // 根据当前内容获取相关内容
      }
    }
  } catch (error) {
    ElMessage.error('获取内容失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 修改 loadContent 函数
const loadContent = async (contentId) => {
  loading.value = true
  activeCategory.value = contentId  // 更新侧边栏选中状态
  try {
    if (knowledgeContent[contentId]) {
      currentContent.value = {
        ...knowledgeContent[contentId],
        related: getRelatedContent(contentId)
      }
    }
  } catch (error) {
    ElMessage.error('获取内容失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 组件挂载时初始化内容
onMounted(() => {
  handleCategorySelect('yin-yang')
})
</script>

<style>
@import '@/assets/Knowledge.css';
</style>