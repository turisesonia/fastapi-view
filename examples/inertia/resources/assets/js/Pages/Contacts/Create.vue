<template>
  <Layout>

    <Head title="Create Contact" />
    <div class="max-w-3xl">
      <h1 class="text-3xl font-bold text-gray-900 mb-6">Create Contact</h1>

      <div class="bg-white rounded-lg shadow p-6">
        <form @submit.prevent="submit">
          <div class="grid grid-cols-1 gap-6">
            <div class="grid grid-cols-2 gap-4">
              <TextInput v-model="form.first_name" label="First Name" :error="form.errors.first_name" required />

              <TextInput v-model="form.last_name" label="Last Name" :error="form.errors.last_name" required />
            </div>

            <SelectInput v-model="form.organization_id" label="Organization" :error="form.errors.organization_id">
              <option v-for="org in organizations" :key="org.id" :value="org.id">
                {{ org.name }}
              </option>
            </SelectInput>

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
            <a href="/contacts" class="px-4 py-2 text-gray-700 hover:text-gray-900">
              Cancel
            </a>
            <LoadingButton type="submit" :loading="form.processing">
              Create Contact
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
import SelectInput from '../../Shared/SelectInput.vue'
import LoadingButton from '../../Shared/LoadingButton.vue'

defineProps<{
  organizations: any[]
}>()

const form = useForm({
  first_name: '',
  last_name: '',
  organization_id: '',
  email: '',
  phone: '',
  address: '',
  city: '',
  region: '',
  country: '',
  postal_code: '',
})

function submit() {
  form.post('/contacts')
}
</script>
