<template>
  <div id="app">
    <CodeAnalyzer />
  </div>
</template>

<script setup lang="ts">
import CodeAnalyzer from './components/CodeAnalyzer.vue'
</script>

<style>
#app {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
}

body {
  margin: 0;
  padding: 0;
  background-color: #f5f5f5;
}

@media (prefers-color-scheme: dark) {
  body {
    background-color: #1a1a1a;
  }
}
</style>
