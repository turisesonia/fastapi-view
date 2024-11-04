<script setup>
import { Link } from '@inertiajs/vue3'

const props = defineProps({

})
</script>

<template>
  <!-- 導航列 -->
  <nav class="bg-white shadow-lg fixed w-full top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex">
          <!-- Logo -->
          <div class="flex-shrink-0 flex items-center">
            <Link href="/" class="text-xl font-bold text-gray-800">FastAPI Demo</Link>
          </div>

          <!-- 導航連結 -->
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">

            <Link href="/about" class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium" :class="[
              $page.component === 'About'
                ? 'border-blue-500 text-gray-900'
                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
            ]">
            關於
            </Link>
            <Link href="/items" class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium" :class="[
              $page.component === 'Item'
                ? 'border-blue-500 text-gray-900'
                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
            ]">
            產品
            </Link>
          </div>
        </div>

        <!-- 手機版選單按鈕 -->
        <div class="sm:hidden flex items-center">
          <button
            class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>