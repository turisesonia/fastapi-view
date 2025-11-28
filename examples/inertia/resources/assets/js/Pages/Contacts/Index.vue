<template>
  <Layout>

    <Head title="Contacts" />
    <div>
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-3xl font-bold text-gray-900">Contacts</h1>
        <a href="/contacts/create" class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
          Create Contact
        </a>
      </div>

      <SearchFilter :filters="filters" />

      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Organization
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">City</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="contact in contacts" :key="contact.id" class="hover:bg-gray-50 cursor-pointer"
              @click="$inertia.visit(`/contacts/${contact.id}/edit`)">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="text-sm font-medium text-gray-900">
                    {{ contact.first_name }} {{ contact.last_name }}
                  </div>
                  <svg v-if="contact.deleted_at" class="w-4 h-4 ml-2 text-gray-400" fill="currentColor"
                    viewBox="0 0 20 20">
                    <path fill-rule="evenodd"
                      d="M13.477 14.89A6 6 0 015.11 6.524l8.367 8.368zm1.414-1.414L6.524 5.11a6 6 0 018.367 8.367zM18 10a8 8 0 11-16 0 8 8 0 0116 0z"
                      clip-rule="evenodd" />
                  </svg>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ contact.organization?.name || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ contact.city }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ contact.phone }}</td>
            </tr>
            <tr v-if="contacts.length === 0">
              <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">
                No contacts found.
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
  contacts: any[]
  filters: {
    search: string
    trashed: string
  }
}>()
</script>
