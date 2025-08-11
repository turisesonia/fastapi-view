<script setup>
import { useForm } from '@inertiajs/vue3'
import { ref } from 'vue'

const props = defineProps({
  error: String,
  username: String
})

const form = useForm({
  username: props.username || '',
  password: ''
})

const isLoading = ref(false)

function submit() {
  isLoading.value = true
  form.post('/auth/login', {
    onFinish: () => {
      isLoading.value = false
    },
    onError: () => {
      form.password = '' // 清除密碼欄位
    }
  })
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          登入您的帳號
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          FastAPI View 範例應用
        </p>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="submit">
        <!-- 錯誤訊息 -->
        <div v-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">
                {{ error }}
              </h3>
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <!-- 用戶名 -->
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">
              用戶名
            </label>
            <input id="username" v-model="form.username" name="username" type="text" required
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="請輸入用戶名" />
            <div v-if="form.errors.username" class="mt-1 text-sm text-red-600">
              {{ form.errors.username }}
            </div>
          </div>

          <!-- 密碼 -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              密碼
            </label>
            <input id="password" v-model="form.password" name="password" type="password" required
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="請輸入密碼" />
            <div v-if="form.errors.password" class="mt-1 text-sm text-red-600">
              {{ form.errors.password }}
            </div>
          </div>
        </div>

        <div>
          <button type="submit" :disabled="form.processing || isLoading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed">
            <span v-if="form.processing || isLoading" class="mr-2">
              <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none"
                viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                </path>
              </svg>
            </span>
            {{ (form.processing || isLoading) ? '登入中...' : '登入' }}
          </button>
        </div>
      </form>

      <!-- 測試帳號提示 -->
      <div class="mt-8">
        <div class="bg-blue-50 border border-blue-200 rounded-md p-4">
          <h3 class="text-sm font-medium text-blue-800 mb-2">測試帳號</h3>
          <div class="text-sm text-blue-700 space-y-1">
            <p><strong>管理員:</strong> admin / password</p>
            <p><strong>一般用戶:</strong> user / password</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>