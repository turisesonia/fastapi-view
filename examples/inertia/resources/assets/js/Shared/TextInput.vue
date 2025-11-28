<template>
  <div>
    <label v-if="label" :for="id" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <input :id="id" :type="type" :value="modelValue"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)" :placeholder="placeholder"
      :required="required"
      class="block w-full px-3 py-2 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
      :class="error ? 'border-red-300' : 'border-gray-300'" />
    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

defineProps<{
  modelValue?: string | number
  label?: string
  type?: string
  placeholder?: string
  error?: string
  required?: boolean
}>()

defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const id = computed(() => Math.random().toString(36).substring(7))
</script>
