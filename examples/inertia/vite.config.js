import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'


export default defineConfig({
    base: '/public/',
    resolve: {
        alias: {
            '@': resolve('/resources/assets'),
        },
    },

    plugins: [
        vue({
            template: {
                transformAssetUrls: {
                    base: null,
                    includeAbsolute: false,
                },
            },
        })
    ],

    build: {
        // generate manifest.json when run vite build
        manifest: true,
        rollupOptions: {
            input: {
                app: resolve(__dirname, '/resources/assets/js/app.js'),
            }
        },
    }
})

