<template>
  <div class="flex items-center space-x-4 mb-6">
    <div class="flex-1">
      <input type="text" v-model="form.search" @input="onChange" placeholder="Search..."
        class="block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
    </div>
    <select v-model="form.trashed" @change="onChange"
      class="px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
      <option value="">Not Trashed</option>
      <option value="with">With Trashed</option>
      <option value="only">Only Trashed</option>
    </select>
    <button v-if="hasFilters" @click="reset" class="px-4 py-2 text-sm text-gray-700 hover:text-gray-900">
      Reset
    </button>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed } from 'vue'
import { router } from '@inertiajs/vue3'
import { debounce } from '../utils'

const props = defineProps<{
  filters: {
    search: string
    trashed: string
  }
}>()

const form = reactive({
  search: props.filters.search || '',
  trashed: props.filters.trashed || '',
})

const hasFilters = computed(() => form.search || form.trashed)

const onChange = debounce(() => {
  router.get(window.location.pathname, form as any, {
    preserveState: true,
    replace: true,
  })
}, 300)

function reset() {
  form.search = ''
  form.trashed = ''
  onChange()
}
</script>
