import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const { resolve } = require('path');


export default defineConfig({
    resolve: {
        alias: {
            '@': resolve('./assets/js'),
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
                app: resolve(__dirname, '/assets/js/app.js'),
            }
        },
    }
})

