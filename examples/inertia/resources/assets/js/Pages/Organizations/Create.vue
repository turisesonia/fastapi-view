<template>
  <Layout>

    <Head title="Create Organization" />
    <div class="max-w-3xl">
      <h1 class="text-3xl font-bold text-gray-900 mb-6">Create Organization</h1>

      <div class="bg-white rounded-lg shadow p-6">
        <form @submit.prevent="submit">
          <div class="grid grid-cols-1 gap-6">
            <TextInput v-model="form.name" label="Name" :error="form.errors.name" required />

            <TextInput v-model="form.email" label="Email" type="email" :error="form.errors.email" />

            <TextInput v-model="form.phone" label="Phone" :error="form.errors.phone" />

            <TextInput v-model="form.address" label="Address" :error="form.errors.address" />

            <div class="grid grid-cols-2 gap-4">
              <TextInput v-model="form.city" label="City" :error="form.errors.city" />

              <TextInput v-model="form.region" label="State/Province" :error="form.errors.region" />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <TextInput v-model="form.country" label="Country" :error="form.errors.country" />

              <TextInput v-model="form.postal_code" label="Postal Code" :error="form.errors.postal_code" />
            </div>
          </div>

          <div class="flex items-center justify-end mt-6 space-x-4">
            <a href="/organizations" class="px-4 py-2 text-gray-700 hover:text-gray-900">
              Cancel
            </a>
            <LoadingButton type="submit" :loading="form.processing">
              Create Organization
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
  name: '',
  email: '',
  phone: '',
  address: '',
  city: '',
  region: '',
  country: '',
  postal_code: '',
})

function submit() {
  form.post('/organizations')
}
</script>
