<template>
  <Layout>

    <Head title="Create User" />
    <div class="max-w-3xl">
      <h1 class="text-3xl font-bold text-gray-900 mb-6">Create User</h1>

      <div class="bg-white rounded-lg shadow p-6">
        <form @submit.prevent="submit">
          <div class="grid grid-cols-1 gap-6">
            <div class="grid grid-cols-2 gap-4">
              <TextInput v-model="form.first_name" label="First Name" :error="form.errors.first_name" required />

              <TextInput v-model="form.last_name" label="Last Name" :error="form.errors.last_name" required />
            </div>

            <TextInput v-model="form.email" label="Email" type="email" :error="form.errors.email" required />

            <TextInput v-model="form.password" label="Password" type="password" :error="form.errors.password"
              required />

            <div class="flex items-center">
              <input id="owner" v-model="form.owner" type="checkbox"
                class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded" />
              <label for="owner" class="ml-2 block text-sm text-gray-900">
                Owner
              </label>
            </div>
          </div>

          <div class="flex items-center justify-end mt-6 space-x-4">
            <a href="/users" class="px-4 py-2 text-gray-700 hover:text-gray-900">
              Cancel
            </a>
            <LoadingButton type="submit" :loading="form.processing">
              Create User
            </LoadingButton>
          </div>
        </form>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { useForm, Head } from '@inertiajs/vue3'
import Layout from '../../Shared/Layout.vue'
import TextInput from '../../Shared/TextInput.vue'
import LoadingButton from '../../Shared/LoadingButton.vue'

const form = useForm({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  owner: false,
})

function submit() {
  form.post('/users')
}
</script>
