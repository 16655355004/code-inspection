<template>
  <div class="video-bg-wrapper">
    <video class="bg-video" autoplay loop muted playsinline>
      <source src="../video/1.mp4" type="video/mp4" />
      您的浏览器不支持视频播放。
    </video>
    <div class="code-analyzer">
      <!-- 顶部导航栏 -->
      <!-- <nav class="navbar" ref="navbar">
        <div class="nav-container">
          <div class="nav-brand">
            <h1>代码命名分析器</h1>
            <span class="nav-subtitle">多语言代码命名规范检查工具</span>
          </div>
          <div class="nav-stats" v-if="showResults">
            <div class="stat-item">
              <span class="stat-number">{{ analysisResults.total_issues }}</span>
              <span class="stat-label">问题</span>
            </div>
            <div class="stat-item warning">
              <span class="stat-number">{{ warningCount }}</span>
              <span class="stat-label">警告</span>
            </div>
            <div class="stat-item info">
              <span class="stat-number">{{ infoCount }}</span>
              <span class="stat-label">建议</span>
            </div>
          </div>
        </div>
      </nav> -->

      <!-- 主要内容区域 -->
      <div class="main-container">
        <!-- 左侧输入面板 -->
        <div class="left-panel" ref="leftPanel">
          <div class="panel-header">
            <h2 style="color: white;">代码输入</h2>
            <div class="language-selector">
              <button
                v-for="lang in supportedLanguages"
                :key="lang.value"
                @click="switchLanguage(lang.value)"
                :class="[
                  'language-tab',
                  { active: selectedLanguage === lang.value },
                ]"
              >
                {{ lang.name }}
              </button>
            </div>
          </div>

          <div class="code-input-container">
            <div class="input-header">
              <label class="input-label">
                {{ getCurrentLanguageDisplay() }} 代码
              </label>
              <div class="input-actions">
                <button
                  @click="clearCode"
                  class="action-btn clear-btn"
                  :disabled="!codeInput.trim()"
                >
                  清空
                </button>
              </div>
            </div>

            <textarea
              ref="codeTextarea"
              v-model="codeInput"
              class="code-textarea"
              :placeholder="getCurrentPlaceholder()"
              @input="onCodeInput"
            ></textarea>

            <div class="input-footer">
              <div class="code-stats">
                <span>行数: {{ codeLines }}</span>
                <span>字符: {{ codeInput.length }}</span>
              </div>
              <button
                @click="analyzeCode"
                :disabled="isAnalyzing || !codeInput.trim()"
                class="analyze-button"
                ref="analyzeBtn"
              >
                <span v-if="isAnalyzing" class="analyzing">
                  <span class="spinner"></span>
                  分析中...
                </span>
                <span v-else>开始分析</span>
              </button>
            </div>
          </div>
        </div>

        <!-- 右侧结果面板 -->
        <div class="right-panel" ref="rightPanel" v-if="showResults">
          <div class="panel-header">
            <h2>分析结果</h2>
            <div class="result-actions">
              <button @click="exportResults" class="action-btn export-btn">
                导出报告
              </button>
            </div>
          </div>

          <!-- 解析错误 -->
          <div
            v-if="analysisResults.parser_errors.length > 0"
            class="error-section"
            ref="errorSection"
          >
            <div class="section-header">
              <h3>解析错误</h3>
              <span class="error-count">{{
                analysisResults.parser_errors.length
              }}</span>
            </div>
            <div class="error-list">
              <div
                v-for="(error, index) in analysisResults.parser_errors"
                :key="error.line"
                class="error-item"
                :ref="(el) => setErrorRef(el, index)"
              >
                <div class="error-header">
                  <span class="error-line">第 {{ error.line }} 行</span>
                </div>
                <div class="error-message">{{ error.message }}</div>
              </div>
            </div>
          </div>

          <!-- 命名问题 -->
          <div
            v-if="analysisResults.results.length > 0"
            class="issues-section"
            ref="issuesSection"
          >
            <div class="section-header">
              <h3>命名问题</h3>
              <div class="issue-filters">
                <button
                  @click="filterSeverity = 'all'"
                  :class="{ active: filterSeverity === 'all' }"
                  class="filter-btn"
                >
                  全部 ({{ analysisResults.results.length }})
                </button>
                <button
                  @click="filterSeverity = 'warning'"
                  :class="{ active: filterSeverity === 'warning' }"
                  class="filter-btn warning"
                >
                  警告 ({{ warningCount }})
                </button>
                <button
                  @click="filterSeverity = 'info'"
                  :class="{ active: filterSeverity === 'info' }"
                  class="filter-btn info"
                >
                  建议 ({{ infoCount }})
                </button>
              </div>
            </div>

            <div class="issues-list">
              <div
                v-for="(result, index) in filteredResults"
                :key="`${result.line}-${result.rule_id}`"
                class="issue-item"
                :class="result.severity"
                :ref="(el) => setIssueRef(el, index)"
              >
                <div class="issue-header">
                  <div class="issue-meta">
                    <span class="issue-line">第 {{ result.line }} 行</span>
                    <span class="issue-rule">{{ result.rule_id }}</span>
                    <span class="issue-severity" :class="result.severity">
                      {{ result.severity === "warning" ? "警告" : "建议" }}
                    </span>
                  </div>
                  <div class="issue-name">{{ result.name }}</div>
                </div>
                <div class="issue-message">{{ result.message }}</div>
              </div>
            </div>
          </div>

          <!-- 无问题状态 -->
          <div
            v-if="
              analysisResults.results.length === 0 &&
              analysisResults.parser_errors.length === 0
            "
            class="no-issues"
            ref="noIssuesSection"
          >
            <div class="success-content">
              <div class="success-icon">PASS</div>
              <h3>分析完成</h3>
              <p>您的代码没有发现命名规范问题</p>
            </div>
          </div>
        </div>

        <!-- 错误状态 -->
        <div v-if="errorMessage" class="error-panel" ref="errorPanel">
          <div class="error-content">
            <h3>分析失败</h3>
            <p class="error-text">{{ errorMessage }}</p>
            <button @click="errorMessage = ''" class="action-btn">重试</button>
          </div>
        </div>

        <!-- 空状态 -->
        <div
          v-if="!showResults && !errorMessage"
          class="empty-panel"
          ref="emptyPanel"
        >
          <div class="empty-content">
            <div class="empty-icon">CODE</div>
            <h3>开始分析</h3>
            <p>在左侧输入您的代码，然后点击"开始分析"按钮</p>
            <div class="feature-list">
              <div class="feature-item">
                <span class="feature-icon">CHECK</span>
                <span>智能命名检查</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">FAST</span>
                <span>实时语法分析</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">IDEA</span>
                <span>改进建议</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from "vue";
import { analyzeCode as apiAnalyzeCode } from "../services/api";
import type { CodeAnalysisResponse } from "../types";
import { gsap } from "gsap";

// 响应式数据
const codeInput = ref("");
const selectedLanguage = ref("csharp");
const isAnalyzing = ref(false);
const analysisResults = ref<CodeAnalysisResponse>({
  results: [],
  total_issues: 0,
  parser_errors: [],
});
const errorMessage = ref("");
const showResults = ref(false);
const filterSeverity = ref<"all" | "warning" | "info">("all");

// DOM引用
const navbar = ref<HTMLElement>();
const leftPanel = ref<HTMLElement>();
const rightPanel = ref<HTMLElement>();
const emptyPanel = ref<HTMLElement>();
const errorPanel = ref<HTMLElement>();
const codeTextarea = ref<HTMLTextAreaElement>();
const analyzeBtn = ref<HTMLButtonElement>();

// 动画引用数组
const issueRefs = ref<HTMLElement[]>([]);
const errorRefs = ref<HTMLElement[]>([]);

const supportedLanguages = [
  {
    value: "csharp",
    name: "C#",
    placeholder: `public class UserData
{
    public string userName;
    public void ProcessData() { }
}`,
  },
  {
    value: "vue",
    name: "Vue.js",
    placeholder: `<template>
  <div>{{ message }}</div>
</template>

<script setup>
import { ref } from 'vue';
const message = ref('Hello World');
<\/script>`,
  },
];

// 计算属性
const warningCount = computed(
  () =>
    analysisResults.value.results.filter((r) => r.severity === "warning").length
);

const infoCount = computed(
  () =>
    analysisResults.value.results.filter((r) => r.severity === "info").length
);

const codeLines = computed(() => {
  return codeInput.value ? codeInput.value.split("\n").length : 0;
});

const filteredResults = computed(() => {
  if (filterSeverity.value === "all") {
    return analysisResults.value.results;
  }
  return analysisResults.value.results.filter(
    (r) => r.severity === filterSeverity.value
  );
});

// 工具方法
const getCurrentLanguageDisplay = () => {
  const lang = supportedLanguages.find(
    (l) => l.value === selectedLanguage.value
  );
  return lang ? lang.name : "C#";
};

const getCurrentPlaceholder = () => {
  const lang = supportedLanguages.find(
    (l) => l.value === selectedLanguage.value
  );
  return lang ? lang.placeholder : supportedLanguages[0].placeholder;
};

// 引用设置方法
const setIssueRef = (el: any, index: number) => {
  if (el) {
    issueRefs.value[index] = el;
  }
};

const setErrorRef = (el: any, index: number) => {
  if (el) {
    errorRefs.value[index] = el;
  }
};

// 动画方法
const animateNavbar = () => {
  if (navbar.value) {
    gsap.fromTo(
      navbar.value,
      { y: -100, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.8, ease: "power3.out" }
    );
  }
};

const animateLeftPanel = () => {
  if (leftPanel.value) {
    gsap.fromTo(
      leftPanel.value,
      { x: -50, opacity: 0 },
      { x: 0, opacity: 1, duration: 0.8, delay: 0.2, ease: "power3.out" }
    );
  }
};

const animateRightPanel = () => {
  if (rightPanel.value) {
    gsap.fromTo(
      rightPanel.value,
      { x: 50, opacity: 0 },
      { x: 0, opacity: 1, duration: 0.8, ease: "power3.out" }
    );
  }
};

const animateResults = () => {
  // 动画化问题项
  issueRefs.value.forEach((el, index) => {
    if (el) {
      gsap.fromTo(
        el,
        { y: 30, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.5,
          delay: index * 0.1,
          ease: "power2.out",
        }
      );
    }
  });

  // 动画化错误项
  errorRefs.value.forEach((el, index) => {
    if (el) {
      gsap.fromTo(
        el,
        { y: 30, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.5,
          delay: index * 0.1,
          ease: "power2.out",
        }
      );
    }
  });
};

// 事件处理方法
const switchLanguage = (language: string) => {
  selectedLanguage.value = language;

  // 语言切换动画
  if (codeTextarea.value) {
    gsap.to(codeTextarea.value, {
      scale: 0.98,
      duration: 0.1,
      yoyo: true,
      repeat: 1,
      ease: "power2.inOut",
    });
  }
};

const onCodeInput = () => {
  // 可以添加实时检查或其他功能
};

const exportResults = () => {
  const data = {
    language: selectedLanguage.value,
    total_issues: analysisResults.value.total_issues,
    results: analysisResults.value.results,
    parser_errors: analysisResults.value.parser_errors,
    timestamp: new Date().toISOString(),
  };

  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `code-analysis-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
};

const analyzeCode = async () => {
  if (!codeInput.value.trim()) return;

  // 分析按钮动画
  if (analyzeBtn.value) {
    gsap.to(analyzeBtn.value, {
      scale: 0.95,
      duration: 0.1,
      yoyo: true,
      repeat: 1,
    });
  }

  isAnalyzing.value = true;
  errorMessage.value = "";
  showResults.value = false;

  try {
    const response = await apiAnalyzeCode({
      language: selectedLanguage.value,
      code: codeInput.value,
    });

    analysisResults.value = response;
    showResults.value = true;

    // 等待DOM更新后执行动画
    await nextTick();
    animateRightPanel();
    setTimeout(() => animateResults(), 300);
  } catch (error: any) {
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail;
    } else if (error.message) {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = "An unexpected error occurred during analysis";
    }
  } finally {
    isAnalyzing.value = false;
  }
};

const clearCode = () => {
  // 清空动画
  if (codeTextarea.value) {
    gsap.to(codeTextarea.value, {
      opacity: 0.5,
      duration: 0.2,
      yoyo: true,
      repeat: 1,
      onComplete: () => {
        codeInput.value = "";
        showResults.value = false;
        errorMessage.value = "";
      },
    });
  } else {
    codeInput.value = "";
    showResults.value = false;
    errorMessage.value = "";
  }
};

// 生命周期
onMounted(() => {
  animateNavbar();
  animateLeftPanel();
});
</script>

<style scoped>
.video-bg-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  z-index: 0;
}
.bg-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  object-fit: cover;
  z-index: 0;
  pointer-events: none;
  user-select: none;
}
.code-analyzer {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  padding: 0;
  margin: 0;
  width: 100%;
}

/* 导航栏 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(248, 219, 219, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  /* padding: 1rem 0; */
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.nav-subtitle {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-left: 1rem;
}

.nav-stats {
  display: flex;
  gap: 1.5rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
}

.stat-item.warning .stat-number {
  color: #f39c12;
}

.stat-item.info .stat-number {
  color: #3498db;
}

.stat-label {
  font-size: 0.8rem;
  color: #7f8c8d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 主容器 */
.main-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  /* padding: 6rem 2rem 2rem; */
  min-height: calc(100vh - 4rem);
  margin-top: 30px;
}
/* 内容区半透明和毛玻璃效果，提升优先级 */
.main-container,
.left-panel,
.right-panel,
.empty-panel,
.error-panel {
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(16px) !important;
  -webkit-backdrop-filter: blur(16px) !important;
  border-radius: 20px !important;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
}

/* 移除面板的固定背景色，确保透明和毛玻璃生效 */
.left-panel,
.right-panel,
.empty-panel,
.error-panel {
  /* 移除 background: #fff; 和 background: #f8f9fa; 等 */
  /* 只保留透明背景和毛玻璃 */
  background: rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(18px) !important;
  -webkit-backdrop-filter: blur(18px) !important;
  border-radius: 20px !important;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
}

/* 左侧面板 */
.left-panel {
  /* background: rgba(255, 255, 255, 0.95); */
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  /* border-bottom: 2px solid #f8f9fa; */
}

.panel-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.language-selector {
  display: flex;
  gap: 0.5rem;
}

.language-tab {
  padding: 0.5rem 1rem;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 600;
  color: #6c757d;
}

.language-tab:hover {
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
}

.language-tab.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.code-input-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.input-label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1.1rem;
}

.input-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
}

.action-btn:hover:not(:disabled) {
  background: #f8f9fa;
  transform: translateY(-1px);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.clear-btn:hover:not(:disabled) {
  border-color: #dc3545;
  color: #dc3545;
}

.code-textarea {
  flex: 1;
  width: 100%;
  min-height: 500px;
  /* padding: 1.5rem; */
  /* border: 2px solid #e9ecef; */
  border-radius: 15px;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(18px) !important;
  -webkit-backdrop-filter: blur(18px) !important;
  border-radius: 20px !important;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
}

.code-textarea:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 1rem;
}

.code-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #6c757d;
}

.analyze-button {
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.analyze-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.analyze-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 右侧面板 */
.right-panel {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow-y: auto;
  max-height: calc(100vh - 8rem);
}

.result-actions {
  display: flex;
  gap: 0.5rem;
}

.export-btn {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  border-radius: 8px;
}

.export-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #218838, #1ea085);
}

/* 动画和交互 */
.analyzing {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 结果区域 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f8f9fa;
}

.section-header h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.error-count {
  background: #dc3545;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 600;
}

.issue-filters {
  display: flex;
  gap: 0.5rem;
}

.filter-btn {
  padding: 0.5rem 1rem;
  border: 2px solid #e9ecef;
  border-radius: 20px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.85rem;
  font-weight: 600;
  color: #6c757d;
}

.filter-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.filter-btn.active {
  border-color: #667eea;
  background: #667eea;
  color: white;
}

.filter-btn.warning.active {
  border-color: #f39c12;
  background: #f39c12;
}

.filter-btn.info.active {
  border-color: #3498db;
  background: #3498db;
}

/* 问题列表 */
.issues-list {
  max-height: 600px;
  overflow-y: auto;
}

.issue-item {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
  position: relative;
}

.issue-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.issue-item.warning {
  border-left: 5px solid #f39c12;
}

.issue-item.info {
  border-left: 5px solid #3498db;
}

.issue-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.issue-meta {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.issue-line {
  font-weight: 700;
  color: #2c3e50;
  font-size: 0.9rem;
}

.issue-rule {
  background: #f8f9fa;
  color: #6c757d;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 600;
}

.issue-severity {
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.issue-severity.warning {
  background: rgba(243, 156, 18, 0.1);
  color: #f39c12;
}

.issue-severity.info {
  background: rgba(52, 152, 219, 0.1);
  color: #3498db;
}

.issue-name {
  font-family: "JetBrains Mono", "Fira Code", monospace;
  background: #f8f9fa;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
}

.issue-message {
  color: #495057;
  line-height: 1.6;
  font-size: 0.95rem;
}

/* 错误列表 */
.error-list {
  max-height: 400px;
  overflow-y: auto;
}

.error-item {
  background: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  border-left: 5px solid #e53e3e;
}

.error-header {
  margin-bottom: 0.5rem;
}

.error-line {
  font-weight: 700;
  color: #e53e3e;
}

.error-message {
  color: #c53030;
  line-height: 1.5;
}

/* 空状态和成功状态 */
.empty-panel,
.error-panel {
  grid-column: 2;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 3rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content,
.error-content,
.success-content {
  text-align: center;
  max-width: 400px;
}

.empty-icon,
.success-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.7;
}

.success-icon {
  color: #28a745;
  font-weight: bold;
}

.empty-content h3,
.error-content h3,
.success-content h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.empty-content p,
.error-content p,
.success-content p {
  color: #6c757d;
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 2rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.feature-icon {
  font-size: 1.5rem;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-container {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .empty-panel,
  .error-panel {
    grid-column: 1;
  }

  .nav-stats {
    display: none;
  }
}

@media (max-width: 768px) {
  .nav-container {
    padding: 0 1rem;
  }

  .nav-brand h1 {
    font-size: 1.2rem;
  }

  .nav-subtitle {
    display: none;
  }

  .main-container {
    padding: 5rem 1rem 2rem;
  }

  .left-panel,
  .right-panel {
    padding: 1.5rem;
  }
}
/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 3px;
}
::-webkit-scrollbar-track {
  background: #f1f1f1;
}
::-webkit-scrollbar-thumb {
  background: #888;
}
::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
