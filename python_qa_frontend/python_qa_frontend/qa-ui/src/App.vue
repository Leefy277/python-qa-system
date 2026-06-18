<template>
  <div class="dashboard-container" :class="{ 'result-page-bg': hasResult && !loading }">

    <div v-if="!hasResult || loading" class="homepage-logo">
      <span class="logo-spark">✨</span>
      <div class="logo-text">
        <h2>面向教育领域的智能文档问答系统</h2>
        <p>自研级联模型（TF-IDF精排 + SBERT） vs 科大讯飞星火大模型</p>
      </div>
    </div>

    <aside v-if="hasResult && !loading" class="sidebar-history-area">
      <div class="sidebar-header">
        <span class="history-icon">🕒</span>
        <h2>搜索历史</h2>
      </div>

      <div class="history-list-wrapper">
        <div class="history-list">
          <div
            v-for="(item, index) in searchHistory"
            :key="index"
            class="history-item"
            :class="{ 'active': query.trim() === item }"
            @click="selectHistory(item)"
          >
            <div class="item-dot"></div>
            <span class="item-text">{{ item }}</span>
          </div>
        </div>
      </div>

      <div class="sidebar-footer" @click="clearHistory">
        <span class="trash-icon">🗑️</span>
        <p>清空历史记录</p>
      </div>
    </aside>

    <main class="main-workspace" :class="{ 'split-layout': hasResult && !loading }">
      <div v-if="!hasResult || loading" class="particles-bg-full">
        <span class="particle" style="width: 100px; height: 100px; top: 5%; left: 5%; animation-delay: 0s;"></span>
        <span class="particle" style="width: 60px; height: 60px; top: 15%; right: 10%; animation-delay: 1.5s;"></span>
        <span class="particle" style="width: 120px; height: 120px; bottom: 15%; left: 10%; animation-delay: 3s;"></span>
        <span class="particle" style="width: 80px; height: 80px; top: 70%; right: 15%; animation-delay: 4.5s;"></span>
        <span class="particle" style="width: 90px; height: 90px; bottom: 5%; right: 20%; animation-delay: 2s;"></span>
        <span class="particle" style="width: 50px; height: 50px; top: 30%; left: 5%; animation-delay: 5.5s;"></span>
        <span class="particle" style="width: 70px; height: 70px; top: 5%; right: 40%; animation-delay: 1s;"></span>
        <span class="particle" style="width: 85px; height: 85px; bottom: 25%; left: 50%; animation-delay: 6.5s;"></span>
        <span class="particle" style="width: 55px; height: 55px; top: 45%; right: 5%; animation-delay: 3.5s;"></span>
        <span class="particle" style="width: 75px; height: 75px; bottom: 40%; right: 60%; animation-delay: 0.5s;"></span>
        <span class="particle" style="width: 65px; height: 65px; top: 80%; left: 25%; animation-delay: 4s;"></span>
        <span class="particle" style="width: 95px; height: 95px; top: 20%; left: 35%; animation-delay: 2.5s;"></span>
      </div>

      <div v-if="!hasResult || loading" class="welcome-search-section">
        <div class="waiting-state">
          <h2 class="waiting-title">随时准备好，只等你需要！</h2>
        </div>

        <div class="search-box-wrapper">
          <span class="plus-icon-left">＋</span>
          <input
              v-model="query"
              @keyup.enter="handleCompare"
              type="text"
              placeholder="输入你的问题，例如：你好啊，大模型！"
              class="blue-input"
          />
          <div class="input-right-controls">
            <span class="mic-icon">🎙️</span>
            <button @click="handleCompare" class="blue-btn">
              <span class="arrow-up-icon">🔍</span>
            </button>
          </div>
        </div>

        <div v-if="loading" class="loading-container">
          <div class="gradient-spinner"></div>
          <p>正在检索中，请稍候...</p>
        </div>
      </div>

      <div v-if="hasResult && !loading" class="result-section">
        <div class="result-wrapper">

          <div class="top-header-banner">
            <div class="banner-decoration">
              <span class="float-dot dot1"></span>
              <span class="float-dot dot2"></span>
              <span class="float-dot dot3"></span>
              <span class="float-ring ring1"></span>
              <span class="float-ring ring2"></span>
            </div>

            <div class="banner-right-query">
              <input
                type="text"
                class="query-input-bubble"
                v-model="query"
                @keyup.enter="handleCompare"
                placeholder="在此输入问题，按回车键继续提问..."
              />
              <button class="retry-btn" @click="returnToWelcome">开启新话题</button>
            </div>
          </div>

          <div class="intent-banner">
            <span class="intent-icon">🎯</span>
            <div class="intent-text-box">
              <span class="intent-label">意图识别结果：</span>
              <span class="intent-value">{{ results.intent_name }}</span>
            </div>
            <div class="intent-badge">置信度: {{ results.intent_score }}</div>
          </div>

          <div class="three-columns-grid">
            <div class="card tfidf-card">
              <div class="card-top-bar light-blue-bar"></div>
              <div class="card-main">
                <div class="card-head">
                  <span class="card-icon">📄</span>
                  <h3>自研级联模型 (TF-IDF)</h3>
                </div>
                <div class="meta-section">
                  <label>命中本地知识库问题</label>
                  <p class="meta-question">{{ results.tfidf.match_question || '未匹配到本地知识' }}</p>
                </div>
                <div class="content-section">
                  <label>检索核心回答</label>
                  <div class="text-block">
                    <p>{{ results.tfidf.answer }}</p>
                  </div>
                </div>
                <div class="card-badge">相似度得分: {{ results.tfidf.score }}</div>
              </div>
            </div>

            <div class="card sbert-card">
              <div class="card-top-bar mid-blue-bar"></div>
              <div class="card-main">
                <div class="card-head">
                  <span class="card-icon">🧠</span>
                  <h3>深度语义检索 (SBERT)</h3>
                </div>
                <div class="meta-section">
                  <label>命中语义泛化问题</label>
                  <p class="meta-question">{{ results.sbert.match_question || '未匹配到语义泛化' }}</p>
                </div>
                <div class="content-section">
                  <label>检索核心回答</label>
                  <div class="text-block">
                    <p>{{ results.sbert.answer }}</p>
                  </div>
                </div>
                <div class="card-badge highlight">语义相关度: {{ results.sbert.score }}</div>
              </div>
            </div>

            <div class="card xf-card">
              <div class="card-top-bar deep-blue-bar"></div>
              <div class="card-main">
                <div class="card-head">
                  <span class="card-icon">☁️</span>
                  <h3>科大讯飞星火大模型</h3>
                </div>
                <div class="meta-section">
                  <label>数据源头</label>
                  <p class="meta-question">实时云端解析</p>
                </div>
                <div class="content-section">
                  <label>
                    {{ results.intent_type === 'chat' ? '实时情感流回复' : '大模型深度解析' }}
                  </label>
                  <div class="text-block ai-highlight-block">
                    <p>{{ results.xf_cloud_answer }}</p>
                  </div>
                </div>
                <div class="card-badge ai-tag">Xunfei Spark Cloud</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const query = ref('')
const loading = ref(false)
const hasResult = ref(false)

const searchHistory = ref([
  'is和==的区别',
  '你好啊，大模型！',
  'while循环',
  'Python中的深拷贝和浅拷贝有什么区别？',
])

const results = ref({
  intent_type: '',
  intent_name: '',
  intent_score: '',
  tfidf: {},
  sbert: {},
  xf_cloud_answer: ''
})

const handleCompare = async () => {
  if (!query.value.trim()) return

  // 记录历史
  if (!searchHistory.value.includes(query.value.trim())) {
    searchHistory.value.unshift(query.value.trim())
  }

  loading.value = true

  try {

    // 发起真实的网络请求连接 FastAPI 后端 
    const response = await fetch('/api/compare', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text: query.value.trim(),
        mode: 'tfidf' // 传递给后端的参数
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()

    // 将后端返回的字段完美映射到前端的响应式对象中
    results.value = {
      intent_type: data.intent_type,
      intent_name: data.intent_name,
      intent_score: data.intent_score,
      tfidf: {
        match_question: data.tfidf_result.match_question,
        answer: data.tfidf_result.answer,
        score: data.tfidf_result.score
      },
      sbert: {
        match_question: data.local_system_answer_full.match_question,
        answer: data.local_system_answer_full.answer,
        score: data.local_system_answer_full.score
      },
      xf_cloud_answer: data.xf_cloud_answer
    }

    hasResult.value = true
  } catch (error) {
    console.error('请求后端接口失败:', error)
    alert('系统连接失败，请检查后端服务是否已启动！')
  } finally {
    loading.value = false
  }
}

const selectHistory = (text) => {
  query.value = text
  handleCompare()
}

const returnToWelcome = () => {
  hasResult.value = false
  query.value = ''
}

const clearHistory = () => {
  searchHistory.value = []
}
</script>

<style scoped>


.dashboard-container {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif;
  display: flex;
  height: 100vh;
  background: radial-gradient(circle at center, #E0F2FE 0%, #F0F9FF 50%, #FFFFFF 100%);
  padding: 20px;
  gap: 20px;
  box-sizing: border-box;
  overflow: hidden;
  transition: background 0.3s ease;
  position: relative;
  align-items: flex-end;
}

.homepage-logo {
  position: absolute;
  top: 24px;
  left: 28px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  z-index: 10;
}
.homepage-logo .logo-spark { font-size: 1.2rem; }
.homepage-logo .logo-text h2 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: #1F2937;
  letter-spacing: 0.5px;
}
.homepage-logo .logo-text p {
  margin: 4px 0 0 0;
  font-size: 0.75rem;
  color: #6B7280;
}

.result-page-bg {
  background: #edebeb32;
}

.sidebar-history-area {
  width: 270px;
  height: 100%; /* 1. 让侧边栏撑满容器可用高度 */
  box-sizing: border-box; /* 2. 防止 padding 撑大盒子 */
  background: url('@/assets/images/image.png') center/cover no-repeat;
  border: 1px solid #FEF3C7;
  border-radius: 16px;
  padding: 20px 16px 16px 16px;
  display: flex;
  flex-direction: column; /* 3. 使用纵向 Flex 控制内部组件 */
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
  flex-shrink: 0;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 14px;
  border-bottom: 1px solid #FEF3C7;
  flex-shrink: 0;
}
.sidebar-header h2 { font-size: 1.1rem; font-weight: 800; color: #1F2937; margin: 0; }
.history-icon { font-size: 1.1rem; color: #6B7280; }

/* 历史记录滚动包装层 */
.history-list-wrapper {
  flex: 1;                /* 4. 核心：独占所有剩余的纵向空间 */
  overflow-y: auto;       /* 5. 核心：纵向内容溢出时自动出现滚动条 */
  margin-top: 14px;
  margin-bottom: 14px;    /* 6. 修正：从 120px 缩减至 14px，腾出空间使 footer 沉底 */
  padding-right: 4px;     /* 7. 给滚动条留出小空隙，防止遮挡文本 */
}

/* 美化滚动条样式 */
.history-list-wrapper::-webkit-scrollbar {
  width: 5px;
}
.history-list-wrapper::-webkit-scrollbar-track {
  background: transparent;
}
.history-list-wrapper::-webkit-scrollbar-thumb {
  background: #CBD5E1;
  border-radius: 10px;
}
.history-list-wrapper::-webkit-scrollbar-thumb:hover {
  background: #94A3B8;
}

.history-list { display: flex; flex-direction: column; gap: 8px; }

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  background: #FFFFFF;
  border: 1px solid #F3F4F6;
  transition: all 0.2s ease;
}
.history-item:hover {
  background: #E0F2FE;
  border-color: #BAE6FD;
}
.history-item.active {
  background: #EFF6FF;
  border-color: #BFDBFE;
}
.history-item.active .item-text { color: #1E40AF; font-weight: 700; }
.history-item.active .item-dot { background: #3B82F6; }

.item-dot { width: 6px; height: 6px; background: #38BDF8; border-radius: 50%; flex-shrink: 0; }
.item-text { font-size: 0.88rem; color: #4B5563; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1; }

/* 底部清空历史,固定在最底部 */
.sidebar-footer {
  background: #EFF6FF;
  border: 1px dashed #BFDBFE;
  border-radius: 10px;
  cursor: pointer;
  flex-shrink: 0; /* 8. 确保按钮高度绝对不会被压缩 */
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px;
  color: #2563EB;
}
.sidebar-footer p { margin: 0; font-size: 0.88rem; font-weight: 700; }
.sidebar-footer:hover { background: #DBEAFE; }


.main-workspace {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  height: 100%;
}
.main-workspace.split-layout {
  justify-content: flex-start;
}

.welcome-search-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  position: relative;
  overflow: visible;
}

.particles-bg-full {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.particle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.5) 0%, rgba(14, 165, 233, 0.25) 50%, transparent 100%);
  animation: floatParticle 8s ease-in-out infinite;
}

@keyframes floatParticle {
  0%, 100% { transform: translateY(0) translateX(0) scale(1); opacity: 0.4; }
  25% { transform: translateY(-30px) translateX(20px) scale(1.1); opacity: 0.7; }
  50% { transform: translateY(-60px) translateX(-10px) scale(0.9); opacity: 0.5; }
  75% { transform: translateY(-30px) translateX(-20px) scale(1.05); opacity: 0.6; }
}

.waiting-state { text-align: center; margin-bottom: 35px; position: relative; z-index: 1; }
.waiting-title { font-size: 2.5rem; font-weight: 500; color: #383a3b; margin: 0; letter-spacing: -0.5px; }

.search-box-wrapper {
  display: flex;
  background: #FFFFFF;
  padding: 6px 6px 6px 20px;
  border-radius: 40px;
  width: 100%;
  max-width: 680px;
  align-items: center;
  box-shadow: 0 8px 30px rgba(14, 165, 233, 0.06), 0 1px 2px rgba(0, 0, 0, 0.01);
  border: 1px solid #E0F2FE;
  box-sizing: border-box;
  position: relative;
  z-index: 1;
}

.plus-icon-left { font-size: 1.4rem; color: #9CA3AF; margin-right: 12px; user-select: none; }
.blue-input { border: none; background: transparent; outline: none; font-size: 1.1rem; flex: 1; color: #1F2937; }
.input-right-controls { display: flex; align-items: center; gap: 16px; }
.mic-icon { font-size: 1.5rem; color: #6B7280; }
.blue-btn { background: #93C5FD; color: white; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
.blue-btn:hover { background: #60A5FA; }
.arrow-up-icon { font-size: 1.3rem; font-weight: bold; }

.result-section {
  width: 100%;
  height: 100%;
  animation: fadeIn 0.4s ease-out;
}
.result-wrapper { display: flex; flex-direction: column; gap: 16px; height: 100%; }

.top-header-banner {
  background: linear-gradient(90deg, #E0F2FE 0%, #BAE6FD 50%, #7DD3FC 100%);
  padding: 16px 24px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 15px rgba(14, 165, 233, 0.12);
  position: relative;
  overflow: hidden;
}

.banner-right-query {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  width: 100%;
  position: relative;
  z-index: 1;
}

.banner-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
}

.float-dot {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  animation: floatDot 4s ease-in-out infinite;
}
.float-dot.dot1 { width: 8px; height: 8px; top: 20%; left: 15%; animation-delay: 0s; }
.float-dot.dot2 { width: 6px; height: 6px; top: 60%; left: 85%; animation-delay: 1.5s; }
.float-dot.dot3 { width: 10px; height: 10px; top: 80%; left: 30%; animation-delay: 3s; }

.float-ring {
  position: absolute;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  animation: pulseRing 3s ease-out infinite;
}
.float-ring.ring1 { width: 30px; height: 30px; top: 10%; right: 20%; animation-delay: 0s; }
.float-ring.ring2 { width: 40px; height: 40px; bottom: 10%; left: 25%; animation-delay: 2s; }

@keyframes floatDot {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.6; }
  50% { transform: translateY(-10px) scale(1.2); opacity: 1; }
}

@keyframes pulseRing {
  0% { transform: scale(0.5); opacity: 0.8; }
  100% { transform: scale(1.5); opacity: 0; }
}

.query-input-bubble {
  width: 50%;
  max-width: 450px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(14, 165, 233, 0.3);
  padding: 12px 24px;
  border-radius: 24px;
  font-size: 1rem;
  font-weight: 500;
  color: #075985;
  backdrop-filter: blur(8px);
  outline: none;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.query-input-bubble::placeholder { color: rgba(7, 89, 133, 0.5); }
.query-input-bubble:focus {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(14, 165, 233, 0.5);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15), 0 4px 12px rgba(0, 0, 0, 0.08);
}

.retry-btn {
  background: #f1faa9f0;
  color: #159cfc;
  border: none;
  padding: 12px 24px;
  border-radius: 24px;
  font-weight: 700;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}


.intent-banner {
  display: flex; align-items: center; padding: 14px 20px; border-radius: 12px;
  background: #FFFFFF; border-left: 5px solid #0EA5E9; border-top: 1px solid #E0F2FE; border-bottom: 1px solid #E0F2FE; border-right: 1px solid #E0F2FE;
}
.intent-text-box { flex: 1; font-size: 0.95rem; }
.intent-label { color: #6B7280; font-weight: 600; }
.intent-value { color: #0284C7; font-weight: 800; }
.intent-badge { padding: 4px 12px; background: #E0F2FE; color: #0284C7; border-radius: 6px; font-size: 0.8rem; font-weight: 700; }

.three-columns-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  flex: 1;
  background: url('@/assets/images/ground.png') center/cover no-repeat;
  border-radius: 16px;
  border: 1px solid #DCFCE7;
  padding: 16px;
  min-height: 0;
}

.card {
  background: #FFFFFF; border-radius: 14px; border: 1px solid #E5E7EB;
  display: flex; flex-direction: column; height: 100%; overflow: hidden;
}
.card-top-bar { height: 5px; }
.light-blue-bar { background: #93C5FD; }
.mid-blue-bar { background: #38BDF8; }
.deep-blue-bar { background: #0284C7; }

.card-main { padding: 18px; display: flex; flex-direction: column; flex: 1; min-height: 0; }
.card-head { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; }
.card-head h3 { margin: 0; font-size: 1.05rem; color: #111827; font-weight: 800; }

label { font-size: 0.78rem; font-weight: 700; color: #9CA3AF; margin-bottom: 6px; display: block; }
.meta-section { margin-bottom: 14px; }
.meta-question { margin: 0; font-size: 0.9rem; color: #111827; font-weight: 700; }

.content-section { flex: 1; display: flex; flex-direction: column; margin-bottom: 14px; min-height: 0; }
.text-block { background: #FFFDFA; border: 1px solid #FEF3C7; padding: 12px; border-radius: 8px; flex: 1; overflow-y: auto; }
.text-block p { margin: 0; font-size: 0.9rem; line-height: 1.6; color: #374151; }
.ai-highlight-block { background: #FFFDFA; border-color: #FEF3C7; }

.card-badge { align-self: flex-start; padding: 5px 12px; background: #F3F4F6; color: #4B5563; border-radius: 6px; font-size: 0.8rem; font-weight: 700; }
.card-badge.highlight, .card-badge.ai-tag { background: #E0F2FE; color: #0284C7; border: 1px solid #BEE3F8; }

.loading-container { width: 100%; text-align: center; margin-top: 30px; color: #0EA5E9; font-weight: 600; }
.gradient-spinner { width: 36px; height: 36px; border: 4px solid #E2E8F0; border-top-color: #0EA5E9; border-radius: 50%; margin: 0 auto 12px; animation: spin 0.8s linear infinite; }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>