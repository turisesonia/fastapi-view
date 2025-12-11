<script setup lang="ts">
import { ref } from 'vue'
import { Head, router } from '@inertiajs/vue3'
import Layout from '../../Shared/Layout.vue'

interface Post {
  id: number
  title: string
  excerpt: string
  author: string
  created_at: string
  likes: number
}

interface Pagination {
  current_page: number
  per_page: number
  total: number
  has_more: boolean
}

const props = withDefaults(defineProps<{
  posts?: Post[]
  pagination: Pagination
}>(), { posts: () => [] })

const loading = ref(false)

function loadMore() {
  loading.value = true
  router.reload({
    data: {
      page: props.pagination.current_page + 1
    },
    only: ['posts', 'pagination'],
    onFinish: () => {
      loading.value = false
    }
  })
}

function formatDate(timestamp: string): string {
  return new Date(timestamp).toLocaleDateString()
}
</script>

<template>
  <Layout>

    <Head title="Merge Props - Load More Posts" />
    <div class="bg-white rounded-lg shadow p-6">
      <h1 class="text-3xl font-bold text-gray-800 mb-2">Merge Props Demo: Load More Posts</h1>
      <p class="text-gray-600 mb-6">
        This demonstrates the basic <strong>append merge strategy</strong>. Click "Load More" to append
        additional posts to the list.
      </p>

      <!-- Posts List -->
      <div class="space-y-4 mb-6">
        <div v-for="post in (posts || [])" :key="post.id"
          class="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-indigo-300 transition-colors">
          <div class="flex justify-between items-start mb-2">
            <h3 class="text-lg font-semibold text-gray-800">{{ post.title }}</h3>
            <span class="text-sm text-gray-500">ID: {{ post.id }}</span>
          </div>
          <p class="text-gray-600 text-sm mb-2">{{ post.excerpt }}</p>
          <div class="flex justify-between items-center text-xs text-gray-500">
            <span>By {{ post.author }}</span>
            <div class="flex items-center space-x-4">
              <span>❤️ {{ post.likes }} likes</span>
              <span>{{ formatDate(post.created_at) }}</span>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="!posts || posts.length === 0" class="text-center py-12 text-gray-500">
          <p class="text-lg mb-2">No posts loaded yet</p>
          <p class="text-sm">Click "Load More" to fetch posts</p>
        </div>
      </div>

      <!-- Load More Button -->
      <div class="flex justify-center">
        <button v-if="pagination.has_more" @click="loadMore" :disabled="loading"
          class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors">
          <span v-if="loading">Loading...</span>
          <span v-else>Load More Posts</span>
        </button>
        <div v-else class="text-gray-500">
          All posts loaded! ({{ posts?.length || 0 }} / {{ pagination.total }})
        </div>
      </div>

      <!-- Stats -->
      <div class="mt-6 p-4 bg-indigo-50 rounded-lg">
        <div class="grid grid-cols-3 gap-4 text-center">
          <div>
            <div class="text-2xl font-bold text-indigo-600">{{ posts?.length || 0 }}</div>
            <div class="text-sm text-gray-600">Posts Loaded</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-indigo-600">{{ pagination.current_page }}</div>
            <div class="text-sm text-gray-600">Current Page</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-indigo-600">{{ pagination.total }}</div>
            <div class="text-sm text-gray-600">Total Posts</div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>
