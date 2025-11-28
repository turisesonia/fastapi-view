<template>
  <Layout>

    <Head title="Users" />
    <div>
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-3xl font-bold text-gray-900">Users</h1>
        <a href="/users/create" class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
          Create User
        </a>
      </div>

      <SearchFilter :filters="filters" />

      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 cursor-pointer"
              @click="$inertia.visit(`/users/${user.id}/edit`)">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="text-sm font-medium text-gray-900">
                    {{ user.first_name }} {{ user.last_name }}
                  </div>
                  <svg v-if="user.deleted_at" class="w-4 h-4 ml-2 text-gray-400" fill="currentColor"
                    viewBox="0 0 20 20">
                    <path fill-rule="evenodd"
                      d="M13.477 14.89A6 6 0 015.11 6.524l8.367 8.368zm1.414-1.414L6.524 5.11a6 6 0 018.367 8.367zM18 10a8 8 0 11-16 0 8 8 0 0116 0z"
                      clip-rule="evenodd" />
                  </svg>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.email }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span v-if="user.owner" class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">Owner</span>
                <span v-else class="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">User</span>
              </td>
            </tr>
            <tr v-if="users.length === 0">
              <td colspan="3" class="px-6 py-4 text-center text-sm text-gray-500">
                No users found.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { Head } from '@inertiajs/vue3'
import Layout from '../../Shared/Layout.vue'
import SearchFilter from '../../Shared/SearchFilter.vue'

defineProps<{
  users: any[]
  filters: {
    search: string
    trashed: string
  }
}>()
</script>
