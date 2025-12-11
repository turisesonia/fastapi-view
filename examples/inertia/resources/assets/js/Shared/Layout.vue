<template>
  <div>
    <div id="dropdown"></div>
    <div class="flex h-screen bg-gray-200 overflow-hidden md:flex-row">
      <!-- Sidebar -->
      <div class="flex-shrink-0 w-56 bg-indigo-900 overflow-y-auto">
        <div class="flex flex-col h-screen">
          <!-- Logo -->
          <div class="flex items-center justify-between px-6 py-4 bg-indigo-800">
            <a href="/" class="text-white text-xl font-bold">
              Ping CRM
            </a>
          </div>

          <!-- Navigation -->
          <div class="flex-1 px-4 py-8">
            <div class="space-y-1">
              <a href="/" class="flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors"
                :class="isUrl('') ? 'bg-indigo-800 text-white' : 'text-indigo-300 hover:bg-indigo-800 hover:text-white'">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6">
                  </path>
                </svg>
                Dashboard
              </a>
              <a href="/organizations"
                class="flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors"
                :class="isUrl('organizations') ? 'bg-indigo-800 text-white' : 'text-indigo-300 hover:bg-indigo-800 hover:text-white'">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4">
                  </path>
                </svg>
                Organizations
              </a>
              <a href="/contacts" class="flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors"
                :class="isUrl('contacts') ? 'bg-indigo-800 text-white' : 'text-indigo-300 hover:bg-indigo-800 hover:text-white'">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z">
                  </path>
                </svg>
                Contacts
              </a>
              <a href="/users" class="flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors"
                :class="isUrl('users') ? 'bg-indigo-800 text-white' : 'text-indigo-300 hover:bg-indigo-800 hover:text-white'">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                Users
              </a>

              <!-- Merge Props Demo Link -->
              <div class="pt-4 mt-4 border-t border-indigo-700">
                <div class="px-4 py-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider">
                  Demos
                </div>
                <a href="/merge-demo" class="flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors"
                  :class="isUrl('merge-demo') ? 'bg-indigo-800 text-white' : 'text-indigo-300 hover:bg-indigo-800 hover:text-white'">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"></path>
                  </svg>
                  Merge Props
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main content area -->
      <div class="flex-1 overflow-x-hidden overflow-y-auto">
        <!-- Top bar -->
        <div class="bg-white border-b flex items-center justify-between px-8 py-4">
          <div class="flex items-center space-x-4">
            <h1 class="text-2xl font-bold text-gray-800">{{ pageTitle }}</h1>
          </div>

          <!-- User menu -->
          <div class="relative">
            <button @click="showUserMenu = !showUserMenu"
              class="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-gray-900 focus:outline-none">
              <span>{{ auth.user?.first_name }} {{ auth.user?.last_name }}</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </button>

            <div v-if="showUserMenu"
              class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10 border">
              <button @click="logout" type="button" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">
                Logout
              </button>
            </div>
          </div>
        </div>

        <!-- Page content -->
        <div class="p-8">
          <slot />
        </div>
      </div>
    </div>

    <!-- Toast notifications for flash messages -->
    <Toast
      v-if="flashMessage.message"
      :type="flashMessage.type"
      :message="flashMessage.message"
      :duration="5000"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { router, usePage } from '@inertiajs/vue3'
import Toast from './Toast.vue'

const showUserMenu = ref(false)
const page = usePage()
const flashMessage = ref<{ type: 'success' | 'error' | 'warning' | 'info'; message: string }>({
  type: 'info',
  message: '',
})

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})

const auth = computed(() => (page.props.auth as any) || {})
const pageTitle = computed(() => {
  const component = page.component as string
  const parts = component.split('/')

  return parts[parts.length - 1]
})

function isUrl(path: string) {
  const url = page.url as string

  if (path === '') {
    return url === '/'
  }

  return url.startsWith(`/${path}`)
}

function logout() {
  router.post('/logout')
}

// Watch for flash messages from page props
watch(
  () => page.props,
  (props: any) => {
    const flash = props.flash || {}
    if (flash.success) {
      flashMessage.value = { type: 'success', message: flash.success }
    } else if (flash.error) {
      flashMessage.value = { type: 'error', message: flash.error }
    } else if (flash.warning) {
      flashMessage.value = { type: 'warning', message: flash.warning }
    } else if (flash.info) {
      flashMessage.value = { type: 'info', message: flash.info }
    } else {
      flashMessage.value = { type: 'info', message: '' }
    }
  },
  { immediate: true, deep: true }
)
</script>

