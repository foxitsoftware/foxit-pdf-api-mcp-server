import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { viteSingleFile } from 'vite-plugin-singlefile'
import svgLoader from 'vite-svg-loader'
import path from 'path'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
    const entry = process.env.VITE_ENTRY || 'index.html'

    return {
        plugins: [
            vue(),
            svgLoader(),
            viteSingleFile()
        ],
        resolve: {
            alias: {
                '@': path.resolve(__dirname, './src')
            }
        },
        server: {
            port: 5173,
            open: true
        },
        build: {
            cssCodeSplit: false,
            assetsInlineLimit: 100000000,
            rollupOptions: {
                input: resolve(__dirname, entry)
            }
        }
    }
})
