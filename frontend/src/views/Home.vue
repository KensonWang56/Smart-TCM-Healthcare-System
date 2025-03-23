<template>
  <div class="home">
    <!-- 轮播图部分 -->
    <el-carousel :interval="4000" type="card" height="400px" class="banner">
      <el-carousel-item v-for="item in carouselItems" :key="item.id">
        <div class="carousel-content" :style="{ backgroundImage: `url(${item.image})` }">
          <div class="carousel-text">
            <h2>{{ item.title }}</h2>
            <p>{{ item.description }}</p>
          </div>
        </div>
      </el-carousel-item>
    </el-carousel>

    <!-- 功能卡片部分 -->
    <div class="section">
      <h2 class="section-title">主要功能</h2>
      <el-row :gutter="20">
        <el-col :span="8" v-for="(card, index) in cards" :key="index">
          <el-card class="feature-card" :body-style="{ padding: '0px' }">
            <div class="card-image-container">
              <img :src="card.image" class="card-image">
              <div class="card-overlay">
                <el-button type="success" @click="navigateTo(card.route)">立即使用</el-button>
              </div>
            </div>
            <div class="card-content">
              <h3>{{ card.title }}</h3>
              <p>{{ card.description }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 中医知识部分 -->
    <div class="section knowledge-section">
      <h2 class="section-title">中医药知识</h2>
      <el-row :gutter="20">
        <el-col :span="8" v-for="(item, index) in knowledgeItems" :key="index">
          <el-card class="knowledge-card" shadow="hover">
            <img :src="item.image" class="knowledge-image">
            <div class="knowledge-content">
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
              <el-link type="success" :href="item.link" target="_blank">了解更多</el-link>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 健康资讯部分 -->
    <div class="section news-section">
      <h2 class="section-title">健康资讯</h2>
      <el-row :gutter="20">
        <el-col :span="12" v-for="(news, index) in newsItems" :key="index">
          <el-card class="news-card" shadow="hover">
            <div class="news-content">
              <div class="news-text">
                <h3>{{ news.title }}</h3>
                <p>{{ news.summary }}</p>
                <div class="news-meta">
                  <span>{{ news.date }}</span>
                </div>
              </div>
              <img :src="news.image" class="news-image">
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const carouselItems = ref([
  {
    id: 1,
    image: '/src/img/1.avif',
    title: '传承千年中医智慧',
    description: '探索传统中医药文化，感受东方医学的魅力'
  },
  {
    id: 2,
    image: '/src/img/2.avif',
    title: '智能中医诊断',
    description: '运用现代技术，提供精准的中医诊断服务'
  },
  {
    id: 3,
    image: '/src/img/3.avif',
    title: '中药材知识库',
    description: '全面的中药材信息，助您深入了解中医药文化'
  }
])

const cards = ref([
  {
    title: '中药材智能识别',
    description: '基于深度学习的中药材图像识别系统，快速准确识别中药材品种',
    image: '/src/img/4.avif',
    route: '/herbs'
  },
  {
    title: '舌诊智能分析',
    description: '上传舌苔照片，AI智能分析身体状况，提供健康建议',
    image: '/src/img/5.avif',
    route: '/tongue'
  },
  {
    title: '智能问诊系统',
    description: '基于大模型的智能问答系统，为您解答中医相关问题',
    image: '/src/img/6.avif',
    route: '/ai-chat'
  }
])

const knowledgeItems = ref([
  {
    title: '常见中药材介绍',
    description: '详细介绍常见中药材的功效与用法',
    image: '/src/img/7.avif',
    link: 'https://www.pharmnet.com.cn/tcm/knowledge/ycrs/'
  },
  {
    title: '中医基础理论',
    description: '阐述中医药的基本理论与核心概念',
    image: '/src/img/8.avif',
    link: 'http://www.zlnow.com/'
  },
  {
    title: '养生保健知识',
    description: '传统中医养生方法与现代生活的结合',
    image: '/src/img/9.avif',
    link: 'https://www.zhzyw.com/zybj/zyys/'
  }
])

const newsItems = ref([
  {
    title: '中医药防治新冠病毒研究最新进展',
    summary: '探讨中医药在抗击新冠疫情中的重要作用和最新研究成果...',
    date: '2024-03-16',
    image: '/src/img/10.avif'
  },
  {
    title: '国家推动中医药传承创新发展',
    summary: '解读最新中医药发展政策，探讨传统医学的现代化道路...',
    date: '2024-03-15',
    image: '/src/img/11.avif'
  }
])

const navigateTo = (route) => {
  router.push(route)
}
</script>

<style>
@import '@/assets/Home.css';
</style>