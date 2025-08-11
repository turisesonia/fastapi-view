<script setup>
import AppLayout from '@/js/Layouts/AppLayout.vue'

const props = defineProps({
  title: String,
  subtitle: String,
  features: Array,
  code_example: String
})
</script>

<template>
  <AppLayout>
    <template #body>
      <div class="max-w-5xl mx-auto my-12">
        <!-- 標題區域 -->
        <div class="text-center mb-16">
          <h1 class="text-4xl font-bold text-gray-900 mb-4">{{ title }}</h1>
          <p class="text-xl text-gray-600">{{ subtitle }}</p>
        </div>

        <!-- 功能特點 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <div v-for="feature in features" :key="feature.title"
            class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <h3 class="text-xl font-semibold text-gray-800 mb-2">{{ feature.title }}</h3>
            <p class="text-gray-600">{{ feature.description }}</p>
          </div>
        </div>

        <!-- 安裝說明 -->
        <div class="bg-white rounded-lg shadow-md p-8 mb-16">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">快速開始</h2>
          <div class="bg-gray-800 rounded-lg p-4 mb-4">
            <code class="text-gray-100">pip install fastapi-view</code>
          </div>
        </div>

        <!-- 使用示例 -->
        <div class="bg-white rounded-lg shadow-md overflow-hidden">
          <div class="bg-gray-700 px-4 py-2">
            <h3 class="text-white font-semibold">使用範例</h3>
          </div>
          <div class="bg-gray-900 p-4 font-mono text-sm">
            <pre class="language-python">
              <code class="text-gray-300">{{ code_example }}</code>
            </pre>
          </div>
        </div>
      </div>
    </template>
  </AppLayout>
</template>