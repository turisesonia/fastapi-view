<template>
  <Layout>

    <Head title="Dashboard" />
    <div class="bg-white rounded-lg shadow p-6">
      <h1 class="text-3xl font-bold text-gray-800 mb-4">Dashboard</h1>
      <p class="text-gray-600 mb-6">
        Welcome to Ping CRM, a demo app designed to help illustrate how
        <a href="https://inertiajs.com" class="text-indigo-600 hover:underline">Inertia.js</a>
        works with
        <a href="https://fastapi.tiangolo.com" class="text-indigo-600 hover:underline">FastAPI</a>.
      </p>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <a href="/organizations" class="block p-6 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors">
          <div class="text-3xl font-bold text-indigo-600 mb-2">{{ organizationsCount }}</div>
          <div class="text-gray-700 font-medium">Organizations</div>
        </a>
        <a href="/contacts" class="block p-6 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
          <div class="text-3xl font-bold text-green-600 mb-2">{{ contactsCount }}</div>
          <div class="text-gray-700 font-medium">Contacts</div>
        </a>
        <a href="/users" class="block p-6 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
          <div class="text-3xl font-bold text-purple-600 mb-2">{{ usersCount }}</div>
          <div class="text-gray-700 font-medium">Users</div>
        </a>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Head } from '@inertiajs/vue3'
import Layout from '../../Shared/Layout.vue'

const organizationsCount = computed(() => 3)
const contactsCount = computed(() => 4)
const usersCount = computed(() => 2)
</script>
