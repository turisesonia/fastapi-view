<template>
  <Layout>

    <Head :title="`Edit ${contact.first_name} ${contact.last_name}`" />
    <div class="max-w-3xl">
      <h1 class="text-3xl font-bold text-gray-900 mb-6">Edit Contact</h1>

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

          <div class="flex items-center justify-between mt-6">
            <button v-if="!contact.deleted_at" @click.prevent="destroy" type="button"
              class="px-4 py-2 text-red-600 hover:text-red-800">
              Delete Contact
            </button>
            <button v-else @click.prevent="restore" type="button" class="px-4 py-2 text-green-600 hover:text-green-800">
              Restore Contact
            </button>

            <div class="flex space-x-4">
              <a href="/contacts" class="px-4 py-2 text-gray-700 hover:text-gray-900">
                Cancel
              </a>
              <LoadingButton type="submit" :loading="form.processing">
                Update Contact
              </LoadingButton>
            </div>
          </div>
        </form>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { useForm, Head, router } from '@inertiajs/vue3'
import Layout from '../../Shared/Layout.vue'
import TextInput from '../../Shared/TextInput.vue'
import SelectInput from '../../Shared/SelectInput.vue'
import LoadingButton from '../../Shared/LoadingButton.vue'

const props = defineProps<{
  contact: any
  organizations: any[]
}>()

const form = useForm({
  first_name: props.contact.first_name,
  last_name: props.contact.last_name,
  organization_id: props.contact.organization_id,
  email: props.contact.email,
  phone: props.contact.phone,
  address: props.contact.address,
  city: props.contact.city,
  region: props.contact.region,
  country: props.contact.country,
  postal_code: props.contact.postal_code,
})

function submit() {
  form.put(`/contacts/${props.contact.id}`)
}

function destroy() {
  if (confirm('Are you sure you want to delete this contact?')) {
    router.delete(`/contacts/${props.contact.id}`)
  }
}

function restore() {
  router.put(`/contacts/${props.contact.id}/restore`)
}
</script>
