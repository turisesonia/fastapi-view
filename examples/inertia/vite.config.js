import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'


export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '')

    const viteHost = env.VITE_DEV_HOST || 'localhost'
    const vitePort = parseInt(env.VITE_DEV_PORT || '5173')
    const viteCorsOrigins = env.VITE_DEV_CORS_ORIGINS
        ? env.VITE_DEV_CORS_ORIGINS.split(',').map(origin => origin.trim())
        : ['http://localhost', 'http://127.0.0.1']

    return {
        plugins: [tailwindcss(), vue()],
        resolve: {
            alias: {
                '@': fileURLToPath(new URL('./resources/assets', import.meta.url)),
            },
        },
        build: {
            manifest: true,
            outDir: 'public/build',
            rollupOptions: {
                input: {
                    app: fileURLToPath(new URL('./resources/assets/js/app.ts', import.meta.url)),
                },
            },
        },
        server: {
            host: viteHost,
            port: vitePort,
            strictPort: true,
            cors: {
                origin: viteCorsOrigins,
                credentials: true,
            },
        },
    }
}
)