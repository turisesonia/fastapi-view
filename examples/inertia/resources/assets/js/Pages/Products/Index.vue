<script setup>
import AppLayout from '@/js/Layouts/AppLayout.vue'
import { Link } from '@inertiajs/vue3'

const props = defineProps({
  items: {
    type: Array,
    default() {
      return []
    }
  }
})
</script>

<template>
  <AppLayout class="py-8">
    <template #body>
      <div class="mx-auto">
        <!-- 頁面標題 -->
        <div class="text-center mb-12">
          <h1 class="text-3xl font-bold text-gray-900 sm:text-4xl">產品列表</h1>
          <p class="mt-4 text-lg text-gray-600">探索我們的精選商品</p>
        </div>

        <!-- 產品網格 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <div v-for="item in items" :key="item.id"
            class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300">
            <!-- 產品圖片 -->
            <div class="aspect-w-1 aspect-h-1 w-full">
              <img :src="item.image" :alt="item.name" class="w-full h-48 object-cover object-center">
            </div>

            <!-- 產品資訊 -->
            <div class="p-4">
              <h2 class="text-lg font-semibold text-gray-800 mb-2">{{ item.name }}</h2>
              <p class="text-gray-600 text-sm mb-4">{{ item.description }}</p>
              <div class="flex items-center justify-between">
                <span class="text-lg font-bold text-indigo-600">${{ item.price }}</span>
                <div class="space-x-2">
                  <Link :href="`/products/${item.id}`"
                    class="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors">
                    詳情
                  </Link>
                  <button
                    class="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700 transition-colors">
                    購買
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 空狀態 -->
        <div v-if="!items.length" class="text-center py-12">
          <div class="text-gray-500 text-lg">目前沒有商品</div>
        </div>
      </div>
    </template>
  </AppLayout>
</template>