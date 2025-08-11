<script setup>
import { Link } from '@inertiajs/vue3'
import { usePage } from '@inertiajs/vue3'
import { computed } from 'vue'

const page = usePage()
const user = computed(() => page.props.auth?.user)

function logout() {
  if (confirm('確定要登出嗎？')) {
    // 使用表單提交來觸發 POST 請求
    const form = document.createElement('form')
    form.method = 'POST'
    form.action = '/auth/logout'
    document.body.appendChild(form)
    form.submit()
  }
}
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

          <!-- 導航連結 (只有登入時顯示) -->
          <div v-if="user" class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <Link href="/about" class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium" :class="[
              $page.component === 'About'
                ? 'border-blue-500 text-gray-900'
                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
            ]">
            關於
            </Link>
            <Link href="/products" class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium" :class="[
              $page.component === 'Products/Index'
                ? 'border-blue-500 text-gray-900'
                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
            ]">
            產品
            </Link>
          </div>
        </div>

        <!-- 用戶資訊和登出 -->
        <div v-if="user" class="flex items-center space-x-4">
          <span class="text-sm text-gray-700">
            歡迎，{{ user.display_name }}
          </span>
          <button
            @click="logout"
            class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-md text-sm transition-colors">
            登出
          </button>
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