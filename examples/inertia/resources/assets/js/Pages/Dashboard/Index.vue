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

      <!-- User Info (loaded immediately) -->
      <div v-if="user" class="mb-8 p-4 bg-blue-50 rounded-lg">
        <h2 class="text-xl font-semibold text-gray-800 mb-2">Welcome, {{ user.name }}</h2>
        <p class="text-gray-600">{{ user.email }}</p>
      </div>

      <!-- Quick Stats (loaded immediately) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <a href="/organizations" class="block p-6 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors">
          <div class="text-3xl font-bold text-indigo-600 mb-2">{{ quick_stats?.organizations || 0 }}</div>
          <div class="text-gray-700 font-medium">Organizations</div>
        </a>
        <a href="/contacts" class="block p-6 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
          <div class="text-3xl font-bold text-green-600 mb-2">{{ quick_stats?.contacts || 0 }}</div>
          <div class="text-gray-700 font-medium">Contacts</div>
        </a>
        <a href="/users" class="block p-6 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
          <div class="text-3xl font-bold text-purple-600 mb-2">{{ quick_stats?.users || 0 }}</div>
          <div class="text-gray-700 font-medium">Users</div>
        </a>
      </div>

      <!-- Deferred Props Example: Analytics (loaded after initial render) -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">Analytics (Deferred Loading)</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Statistics Card -->
          <div class="p-6 bg-gray-50 rounded-lg">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">Detailed Statistics</h3>
            <div v-if="statistics">
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span class="text-gray-600">Total Users:</span>
                  <span class="font-semibold text-gray-800">{{ statistics.total_users }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Owner Users:</span>
                  <span class="font-semibold text-gray-800">{{ statistics.owner_users }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Organizations:</span>
                  <span class="font-semibold text-gray-800">{{ statistics.total_organizations }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Contacts:</span>
                  <span class="font-semibold text-gray-800">{{ statistics.total_contacts }}</span>
                </div>
              </div>
            </div>
            <div v-else class="animate-pulse">
              <div class="h-4 bg-gray-300 rounded mb-2"></div>
              <div class="h-4 bg-gray-300 rounded mb-2"></div>
              <div class="h-4 bg-gray-300 rounded mb-2"></div>
              <div class="h-4 bg-gray-300 rounded"></div>
            </div>
          </div>

          <!-- Recent Activities Card -->
          <div class="p-6 bg-gray-50 rounded-lg">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">Recent Activities</h3>
            <div v-if="recent_activities">
              <div class="space-y-3">
                <div v-for="activity in recent_activities" :key="activity.id"
                  class="p-3 bg-white rounded border border-gray-200">
                  <div class="text-sm font-medium text-gray-800">{{ activity.description }}</div>
                  <div class="text-xs text-gray-500 mt-1">{{ formatDate(activity.timestamp) }}</div>
                </div>
              </div>
            </div>
            <div v-else class="animate-pulse space-y-3">
              <div class="h-16 bg-gray-300 rounded"></div>
              <div class="h-16 bg-gray-300 rounded"></div>
              <div class="h-16 bg-gray-300 rounded"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Chart Data (separate deferred group) -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">Chart Preview (Separate Group)</h2>
        <div class="p-6 bg-gray-50 rounded-lg">
          <div v-if="chart_data">
            <div class="flex items-end space-x-4 h-32">
              <div v-for="(value, index) in chart_data.values" :key="index" class="flex-1 bg-indigo-500 rounded-t"
                :style="{ height: `${(value / 20) * 100}%` }">
                <div class="text-center text-white text-xs mt-2">{{ value }}</div>
              </div>
            </div>
            <div class="flex justify-around mt-2 text-sm text-gray-600">
              <span v-for="label in chart_data.labels" :key="label">{{ label }}</span>
            </div>
          </div>
          <div v-else class="animate-pulse">
            <div class="h-32 bg-gray-300 rounded mb-2"></div>
            <div class="flex justify-around">
              <div class="h-4 w-12 bg-gray-300 rounded"></div>
              <div class="h-4 w-12 bg-gray-300 rounded"></div>
              <div class="h-4 w-12 bg-gray-300 rounded"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Implementation Notes -->
      <div class="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h3 class="text-lg font-semibold text-yellow-800 mb-2">💡 Deferred Props Implementation</h3>
        <ul class="text-sm text-yellow-700 space-y-1 list-disc list-inside">
          <li><code class="bg-yellow-100 px-1 rounded">quick_stats</code> and <code
              class="bg-yellow-100 px-1 rounded">user</code> are loaded immediately</li>
          <li><code class="bg-yellow-100 px-1 rounded">statistics</code> and <code
              class="bg-yellow-100 px-1 rounded">recent_activities</code> are in the "analytics" group (deferred)</li>
          <li><code class="bg-yellow-100 px-1 rounded">chart_data</code> is in the "charts" group (deferred separately)
          </li>
          <li>Skeleton loaders show while deferred data is loading</li>
          <li>Check the backend code in <code class="bg-yellow-100 px-1 rounded">app/routers/view/dashboard.py</code> to
            see how deferred props are defined</li>
        </ul>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { Head } from '@inertiajs/vue3'
import Layout from '../../Shared/Layout.vue'

interface QuickStats {
  users: number
  organizations: number
  contacts: number
}

interface Statistics {
  total_users: number
  total_organizations: number
  total_contacts: number
  owner_users: number
}

interface Activity {
  id: number
  type: string
  description: string
  timestamp: string
}

interface ChartData {
  labels: string[]
  values: number[]
}

interface User {
  name: string
  email: string
}

defineProps<{
  quick_stats?: QuickStats
  user?: User
  statistics?: Statistics
  recent_activities?: Activity[]
  chart_data?: ChartData
}>()

function formatDate(timestamp: string): string {
  return new Date(timestamp).toLocaleString()
}
</script>
