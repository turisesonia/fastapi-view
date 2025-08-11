<script setup>
import AppLayout from '@/js/Layouts/AppLayout.vue'
import { Link } from '@inertiajs/vue3'

const props = defineProps({
  title: String,
  description: String,
  technologies: Array,
  features: Array,
  featured_products: Array
})
</script>

<template>
  <AppLayout>
    <template #body>
      <div class="relative py-3 sm:max-w-6xl sm:mx-auto">
        <div
          class="absolute inset-0 bg-gradient-to-r from-cyan-400 to-light-blue-500 shadow-lg transform -skew-y-6 sm:skew-y-0 sm:-rotate-6 sm:rounded-3xl">
        </div>
        <div class="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <div class="max-w-5xl mx-auto">
            <div class="divide-y divide-gray-200">
              
              <!-- 標題區域 -->
              <div class="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <h1 class="text-3xl font-bold text-gray-900 mb-8">{{ title }}</h1>
                <p class="mb-4">{{ description }}</p>
                
                <p>使用以下技術建置:</p>
                <ul class="list-disc space-y-2 ml-4">
                  <li v-for="tech in technologies" :key="tech">{{ tech }}</li>
                </ul>
              </div>

              <!-- 功能特色 -->
              <div class="pt-6 pb-8 text-base leading-6 font-bold sm:text-lg sm:leading-7">
                <h2 class="text-2xl text-gray-900 mb-6">主要特色</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div v-for="feature in features" :key="feature.title"
                    class="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">{{ feature.title }}</h3>
                    <p class="text-gray-600 font-normal">{{ feature.description }}</p>
                  </div>
                </div>
              </div>

              <!-- 精選商品 -->
              <div class="pt-6 text-base leading-6 font-bold sm:text-lg sm:leading-7" v-if="featured_products.length">
                <h2 class="text-2xl text-gray-900 mb-6">精選商品</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div v-for="product in featured_products" :key="product.id"
                    class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                    <img :src="product.image" :alt="product.name" class="w-full h-48 object-cover">
                    <div class="p-4">
                      <h3 class="text-lg font-semibold text-gray-800 mb-2">{{ product.name }}</h3>
                      <p class="text-gray-600 text-sm mb-4 font-normal">{{ product.description }}</p>
                      <div class="flex items-center justify-between">
                        <span class="text-lg font-bold text-indigo-600">${{ product.price }}</span>
                        <Link :href="`/products/${product.id}`"
                          class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700 transition-colors">
                          查看詳情
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="text-center">
                  <Link href="/products"
                    class="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
                    查看所有商品
                  </Link>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </template>
  </AppLayout>
</template>