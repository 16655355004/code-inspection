<template>
  <div class="code-analyzer">
    <header class="header">
      <h1>代码命名分析器</h1>
      <p class="subtitle">C# 代码语义命名规范检查</p>
    </header>

    <div class="main-content">
      <div class="input-section">
        <label for="code-input" class="input-label">
          请粘贴您的 C# 代码：
        </label>
        <textarea
          id="code-input"
          v-model="codeInput"
          class="code-textarea"
          placeholder="public class UserData
{
    public string userName;
    public void ProcessData() { }
}"
          rows="15"
        ></textarea>
        
        <div class="button-container">
          <button 
            @click="analyzeCode" 
            :disabled="isAnalyzing || !codeInput.trim()"
            class="analyze-button"
          >
            <span v-if="isAnalyzing" class="analyzing">
              <span class="spinner"></span>
              分析中...
            </span>
            <span v-else>分析代码</span>
          </button>
          
          <button 
            @click="clearCode" 
            :disabled="!codeInput.trim()"
            class="clear-button"
          >
            清空
          </button>
        </div>
      </div>

      <div class="results-section" v-if="showResults">
        <h2>分析结果</h2>
        
        <div class="results-summary">
          <div class="summary-item">
            <span class="count">{{ analysisResults.total_issues }}</span>
            <span class="label">总问题数</span>
          </div>
          <div class="summary-item warning">
            <span class="count">{{ warningCount }}</span>
            <span class="label">警告</span>
          </div>
          <div class="summary-item info">
            <span class="count">{{ infoCount }}</span>
            <span class="label">建议</span>
          </div>
        </div>

        <div v-if="analysisResults.parser_errors.length > 0" class="parser-errors">
          <h3>解析错误</h3>
          <div v-for="error in analysisResults.parser_errors" :key="error.line" class="error-item">
            <span class="error-line">第 {{ error.line }} 行:</span>
            <span class="error-message">{{ error.message }}</span>
          </div>
        </div>

        <div v-if="analysisResults.results.length > 0" class="issues-list">
          <h3>命名问题</h3>
          <div 
            v-for="result in analysisResults.results" 
            :key="`${result.line}-${result.rule_id}`"
            class="issue-item"
            :class="result.severity"
          >
            <div class="issue-header">
              <span class="issue-line">第 {{ result.line }} 行</span>
              <span class="issue-name">{{ result.name }}</span>
              <span class="issue-rule">{{ result.rule_id }}</span>
              <span class="issue-severity" :class="result.severity">
                {{ result.severity === 'warning' ? '警告' : result.severity === 'info' ? '建议' : '错误' }}
              </span>
            </div>
            <div class="issue-message">{{ result.message }}</div>
          </div>
        </div>

        <div v-if="analysisResults.results.length === 0 && analysisResults.parser_errors.length === 0" class="no-issues">
          <div class="success-icon">✅</div>
          <h3>太棒了！</h3>
          <p>您的代码没有发现命名规范问题。</p>
        </div>
      </div>

      <div v-if="errorMessage" class="error-section">
        <h3>错误</h3>
        <p class="error-text">{{ errorMessage }}</p>
      </div>
    </div>
    
    <footer class="disclaimer">
      <p>
        <strong>免责声明：</strong>此工具仅供参考，不代表最终的代码质量标准。
        请结合项目实际情况和团队规范进行判断。
      </p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { analyzeCode as apiAnalyzeCode } from '../services/api'
import type { CodeAnalysisResponse } from '../types'

const codeInput = ref('')
const isAnalyzing = ref(false)
const analysisResults = ref<CodeAnalysisResponse>({
  results: [],
  total_issues: 0,
  parser_errors: []
})
const errorMessage = ref('')
const showResults = ref(false)

const warningCount = computed(() => 
  analysisResults.value.results.filter(r => r.severity === 'warning').length
)

const infoCount = computed(() => 
  analysisResults.value.results.filter(r => r.severity === 'info').length
)

const analyzeCode = async () => {
  if (!codeInput.value.trim()) return

  isAnalyzing.value = true
  errorMessage.value = ''
  showResults.value = false

  try {
    const response = await apiAnalyzeCode({
      language: 'csharp',
      code: codeInput.value
    })
    
    analysisResults.value = response
    showResults.value = true
  } catch (error: any) {
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else if (error.message) {
      errorMessage.value = error.message
    } else {
      errorMessage.value = 'An unexpected error occurred during analysis'
    }
  } finally {
    isAnalyzing.value = false
  }
}

const clearCode = () => {
  codeInput.value = ''
  showResults.value = false
  errorMessage.value = ''
}
</script>

<style scoped>
.code-analyzer {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
}

.subtitle {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin: 0;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  width: 100%;
  max-width: 1000px;
}

@media (min-width: 768px) {
  .main-content {
    grid-template-columns: 1fr 1fr;
  }
}

.input-section {
  display: flex;
  flex-direction: column;
}

.input-label {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.code-textarea {
  width: 100%;
  min-height: 400px;
  padding: 1rem;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  transition: border-color 0.3s;
}

.code-textarea:focus {
  outline: none;
  border-color: #3498db;
}

.button-container {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.analyze-button {
  flex: 1;
  padding: 0.75rem 1.5rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.analyze-button:hover:not(:disabled) {
  background-color: #2980b9;
}

.analyze-button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.clear-button {
  padding: 0.75rem 1.5rem;
  background-color: #95a5a6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.clear-button:hover:not(:disabled) {
  background-color: #7f8c8d;
}

.clear-button:disabled {
  background-color: #ecf0f1;
  cursor: not-allowed;
}

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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.disclaimer {
  margin-top: 2rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  text-align: center;
  max-width: 800px;
  width: 100%;
}

.disclaimer p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
  line-height: 1.4;
}

.results-section {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.results-section h2 {
  color: #2c3e50;
  margin-top: 0;
  margin-bottom: 1rem;
}

.results-summary {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background-color: white;
  border-radius: 6px;
  border: 1px solid #dee2e6;
  flex: 1;
}

.summary-item .count {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.summary-item .label {
  font-size: 0.9rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

.summary-item.warning .count {
  color: #f39c12;
}

.summary-item.info .count {
  color: #3498db;
}

.parser-errors {
  margin-bottom: 1.5rem;
}

.parser-errors h3 {
  color: #e74c3c;
  margin-bottom: 0.5rem;
}

.error-item {
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
}

.error-line {
  font-weight: bold;
  color: #c0392b;
}

.error-message {
  margin-left: 0.5rem;
  color: #e74c3c;
}

.issues-list h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.issue-item {
  background-color: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  transition: box-shadow 0.2s;
}

.issue-item:hover {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.issue-item.warning {
  border-left: 4px solid #f39c12;
}

.issue-item.info {
  border-left: 4px solid #3498db;
}

.issue-item.error {
  border-left: 4px solid #e74c3c;
}

.issue-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.issue-line {
  font-weight: bold;
  color: #2c3e50;
  font-size: 0.9rem;
}

.issue-name {
  font-family: 'Courier New', monospace;
  background-color: #f8f9fa;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  font-size: 0.9rem;
}

.issue-rule {
  background-color: #e9ecef;
  color: #495057;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  font-size: 0.8rem;
  font-weight: bold;
}

.issue-severity {
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  font-size: 0.8rem;
  font-weight: bold;
  text-transform: uppercase;
}

.issue-severity.warning {
  background-color: #fff3cd;
  color: #856404;
}

.issue-severity.info {
  background-color: #d1ecf1;
  color: #0c5460;
}

.issue-severity.error {
  background-color: #f8d7da;
  color: #721c24;
}

.issue-message {
  color: #495057;
  line-height: 1.4;
}

.no-issues {
  text-align: center;
  padding: 2rem;
}

.success-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.no-issues h3 {
  color: #27ae60;
  margin-bottom: 0.5rem;
}

.no-issues p {
  color: #6c757d;
}

.error-section {
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  padding: 1.5rem;
  grid-column: 1 / -1;
}

.error-section h3 {
  color: #e74c3c;
  margin-top: 0;
}

.error-text {
  color: #c0392b;
  margin: 0;
}

@media (prefers-color-scheme: dark) {
  .header h1 {
    color: #ecf0f1;
  }
  
  .disclaimer {
    background-color: #34495e;
    border-color: #2c3e50;
  }
  
  .disclaimer p {
    color: #bdc3c7;
  }
  
  .input-label {
    color: #ecf0f1;
  }
  
  .code-textarea {
    background-color: #2c3e50;
    color: #ecf0f1;
    border-color: #34495e;
  }
  
  .results-section {
    background-color: #34495e;
    border-color: #2c3e50;
  }
  
  .results-section h2,
  .issues-list h3 {
    color: #ecf0f1;
  }
  
  .summary-item,
  .issue-item {
    background-color: #2c3e50;
    border-color: #34495e;
  }
  
  .issue-name {
    background-color: #34495e;
    color: #ecf0f1;
  }
}
</style>
