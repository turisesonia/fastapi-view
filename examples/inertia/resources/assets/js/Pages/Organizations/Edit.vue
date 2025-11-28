<template>
  <Layout>

    <Head :title="`Edit ${organization.name}`" />
    <div class="max-w-3xl">
      <h1 class="text-3xl font-bold text-gray-900 mb-6">Edit Organization</h1>

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

          <div class="flex items-center justify-between mt-6">
            <button v-if="!organization.deleted_at" @click.prevent="destroy" type="button"
              class="px-4 py-2 text-red-600 hover:text-red-800">
              Delete Organization
            </button>
            <button v-else @click.prevent="restore" type="button" class="px-4 py-2 text-green-600 hover:text-green-800">
              Restore Organization
            </button>

            <div class="flex space-x-4">
              <a href="/organizations" class="px-4 py-2 text-gray-700 hover:text-gray-900">
                Cancel
              </a>
              <LoadingButton type="submit" :loading="form.processing">
                Update Organization
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
import LoadingButton from '../../Shared/LoadingButton.vue'

const props = defineProps<{
  organization: any
}>()

const form = useForm({
  name: props.organization.name,
  email: props.organization.email,
  phone: props.organization.phone,
  address: props.organization.address,
  city: props.organization.city,
  region: props.organization.region,
  country: props.organization.country,
  postal_code: props.organization.postal_code,
})

function submit() {
  form.put(`/organizations/${props.organization.id}`)
}

function destroy() {
  if (confirm('Are you sure you want to delete this organization?')) {
    router.delete(`/organizations/${props.organization.id}`)
  }
}

function restore() {
  router.put(`/organizations/${props.organization.id}/restore`)
}
</script>
