<script setup>
import AppLayout from '@/js/Layouts/AppLayout.vue'

const props = defineProps({})
</script>

<template>
  <AppLayout>

    <template #body>
      <div class="relative py-3 sm:max-w-xl sm:mx-auto">
        <div
          class="absolute inset-0 bg-gradient-to-r from-cyan-400 to-light-blue-500 shadow-lg transform -skew-y-6 sm:skew-y-0 sm:-rotate-6 sm:rounded-3xl">
        </div>
        <div class="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <div class="max-w-md mx-auto">
            <div class="divide-y divide-gray-200">
              <div class="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <h1 class="text-3xl font-bold text-gray-900 mb-8">歡迎</h1>
                <p class="mb-4">這是一個使用 FastAPI 和 Vue.js 建立的專案</p>
                <p>使用以下技術建置:</p>
                <ul class="list-disc space-y-2 ml-4">
                  <li>FastAPI</li>
                  <li>Vue 3</li>
                  <li>Vite</li>
                  <li>Tailwind CSS</li>
                  <li>Inertia.js</li>
                </ul>

              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

  </AppLayout>
</template>