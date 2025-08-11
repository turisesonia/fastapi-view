<script setup>
import AppLayout from '@/js/Layouts/AppLayout.vue'
import { Link } from '@inertiajs/vue3'

const props = defineProps({
  item: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <AppLayout>
    <template #body>
      <div class="max-w-4xl mx-auto my-8">
        
        <!-- 返回按鈕 -->
        <div class="mb-6">
          <Link href="/products" 
            class="inline-flex items-center text-blue-600 hover:text-blue-800 transition-colors">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            返回商品列表
          </Link>
        </div>

        <div class="bg-white rounded-lg shadow-lg overflow-hidden">
          <div class="md:flex">
            <!-- 商品圖片 -->
            <div class="md:w-1/2">
              <img :src="item.image" :alt="item.name" 
                class="w-full h-96 md:h-full object-cover object-center">
            </div>

            <!-- 商品資訊 -->
            <div class="md:w-1/2 p-8">
              <div class="uppercase tracking-wide text-sm text-indigo-500 font-semibold">
                商品編號: {{ item.id }}
              </div>
              
              <h1 class="mt-2 text-3xl font-bold text-gray-900">{{ item.name }}</h1>
              
              <p class="mt-4 text-gray-600 leading-relaxed">
                {{ item.description }}
              </p>

              <!-- 價格 -->
              <div class="mt-6">
                <span class="text-3xl font-bold text-indigo-600">${{ item.price }}</span>
              </div>

              <!-- 商品特色 -->
              <div class="mt-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-3">商品特色</h3>
                <ul class="space-y-2 text-gray-600">
                  <li class="flex items-center">
                    <svg class="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                    </svg>
                    高品質保證
                  </li>
                  <li class="flex items-center">
                    <svg class="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                    </svg>
                    快速配送
                  </li>
                  <li class="flex items-center">
                    <svg class="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                    </svg>
                    7天鑑賞期
                  </li>
                </ul>
              </div>

              <!-- 操作按鈕 -->
              <div class="mt-8 space-y-3">
                <button class="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 transition-colors">
                  立即購買
                </button>
                <button class="w-full bg-gray-200 text-gray-800 py-3 px-6 rounded-lg font-semibold hover:bg-gray-300 transition-colors">
                  加入購物車
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </AppLayout>
</template>