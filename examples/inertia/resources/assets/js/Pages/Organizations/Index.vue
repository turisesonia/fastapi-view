<template>
  <Layout>

    <Head title="Organizations" />
    <div>
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-3xl font-bold text-gray-900">Organizations</h1>
        <a href="/organizations/create" class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
          Create Organization
        </a>
      </div>

      <SearchFilter :filters="filters" />

      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">City</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="org in organizations" :key="org.id" class="hover:bg-gray-50 cursor-pointer"
              @click="$inertia.visit(`/organizations/${org.id}/edit`)">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="text-sm font-medium text-gray-900">{{ org.name }}</div>
                  <svg v-if="org.deleted_at" class="w-4 h-4 ml-2 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd"
                      d="M13.477 14.89A6 6 0 015.11 6.524l8.367 8.368zm1.414-1.414L6.524 5.11a6 6 0 018.367 8.367zM18 10a8 8 0 11-16 0 8 8 0 0116 0z"
                      clip-rule="evenodd" />
                  </svg>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ org.city }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ org.phone }}</td>
            </tr>
            <tr v-if="organizations.length === 0">
              <td colspan="3" class="px-6 py-4 text-center text-sm text-gray-500">
                No organizations found.
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
  organizations: any[]
  filters: {
    search: string
    trashed: string
  }
}>()
</script>
