<script setup>
import AppLayout from '@/js/Layouts/AppLayout.vue'

const features = [
  { title: '快速整合', desc: '輕鬆整合 FastAPI 後端服務' },
  { title: 'Inertia.js & Vite', desc: '支援 Inertia.js 以及 Vite' },
]

const codeExample = `
import os

from fastapi import FastAPI

from fastapi_view import inertia

app = FastAPI(title="api")
inertia.setup(app, directory="resources/views")

@app.get("/")

@app.get("/")
def index():
    return inertia("Index")

@app.get("/about")
def about():
    return inertia("About")
`
</script>

<template>
  <AppLayout>
    <template #body>
      <div class="max-w-5xl mx-auto my-12">
        <!-- 標題區域 -->
        <div class="text-center mb-16">
          <h1 class="text-4xl font-bold text-gray-900 mb-4">FastAPI Client Library</h1>
          <p class="text-xl text-gray-600">強大且易用的 FastAPI 前端整合方案</p>
        </div>

        <!-- 功能特點 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
          <div v-for="feature in features" :key="feature.title"
            class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <h3 class="text-xl font-semibold text-gray-800 mb-2">{{ feature.title }}</h3>
            <p class="text-gray-600">{{ feature.desc }}</p>
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
        <div class="bg-gray-900 rounded-b-lg p-4 font-mono text-sm">
          <pre class="language-python">
            <code class="text-gray-300">
              {{ codeExample }}
            </code>
          </pre>
        </div>
      </div>
    </template>
  </AppLayout>
</template>
