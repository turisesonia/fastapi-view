// Vue 3 & Inertia setup
import { createApp, h } from 'vue'
import { createInertiaApp } from '@inertiajs/vue3'

import "@/css/app.css"

createInertiaApp({
  resolve: async (name) => {
    const pages = import.meta.glob('./Pages/**/*.vue')
    return (await pages[`./Pages/${name}.vue`]()).default
  },

  setup({ el, App, props, plugin }) {
    const app = createApp({ render: () => h(App, props) })

    app.use(plugin)
      .mount(el)
  },
})