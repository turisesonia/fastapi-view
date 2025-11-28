<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <h1 class="text-center text-3xl font-extrabold text-gray-900">
        Ping CRM
      </h1>
      <h2 class="mt-6 text-center text-2xl font-bold text-gray-900">
        Sign in to your account
      </h2>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <form @submit.prevent="submit" class="space-y-6">
          <TextInput v-model="form.email" label="Email" type="email" required :error="form.errors.email"
            placeholder="john@example.com" />

          <TextInput v-model="form.password" label="Password" type="password" required :error="form.errors.password"
            placeholder="Enter your password" />

          <div class="flex items-center">
            <input id="remember" v-model="form.remember" type="checkbox"
              class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded" />
            <label for="remember" class="ml-2 block text-sm text-gray-900">
              Remember me
            </label>
          </div>

          <div>
            <LoadingButton type="submit" :loading="form.processing" className="w-full flex justify-center">
              Sign in
            </LoadingButton>
          </div>

        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useForm } from '@inertiajs/vue3'
import TextInput from '../../Shared/TextInput.vue'
import LoadingButton from '../../Shared/LoadingButton.vue'

const form = useForm({
  email: 'john@example.com',
  password: 'secret',
  remember: false,
})

function submit() {
  form.post('/login')
}
</script>