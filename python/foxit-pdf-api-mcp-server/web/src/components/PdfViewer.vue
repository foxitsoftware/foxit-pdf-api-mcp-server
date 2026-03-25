<template>
    <a-spin :loading="loading" dot id="loading">
        <div class="pdf-viewer-container">
            <div id="foxit-embed-view"></div>
            <button id="fullscreen-btn" @click="toggleFullscreen">
                <FullScreenIcon />
            </button>

            <button id="download-btn" @click="downloadPDF">
                <FileDownloadIcon />
            </button>
        </div>
    </a-spin>
</template>

<script setup lang="ts">
import { onMounted, ref, onUnmounted } from 'vue'
import FullScreenIcon from '@/svg/full_screen.svg?component'
import FileDownloadIcon from '@/svg/file_download.svg?component'
import { App } from '@modelcontextprotocol/ext-apps'

declare global {
    interface Window {
        FoxitEmbed: any
        embedView: any
    }
}

const CLIENT_ID = "dadfa204c63194751e17dcae936f03eb"
const isFullscreen = ref(false)
const loading = ref(true)
const mcpApp = ref<App | null>(null)
const pdfShareUrl = ref<string | null>(null)

const initPdfViewer = (pdfUrl: string) => {
    console.log('PDF URL to load:', pdfUrl)

    window.embedView = new window.FoxitEmbed.View({
        clientId: CLIENT_ID,
        divId: "foxit-embed-view",
        locale: "en-US",
    })

    window.embedView.previewFile(
        {
            content: pdfUrl,
            metaData: {
                fileName: "Embed API Demo.pdf",
            },
        },
        {
            showToolControls: true,
            showLeftHandPanel: true,
            showDownloadPDF: true,
            showPrintPDF: false,
        }
    )

    import('@/svg/editor_logo.svg?url').then(({ default: editorLogo }) => {
        import('@/svg/editor_top_logo.svg?url').then(({ default: editorTopLogo }) => {
            window.embedView.setUIElementsVisible(["Save", "OpenFile"], false)
            window.embedView.setUIGroupVisible(["More", "FloatBar"], false)

            window.embedView.setTheme({
                primaryColor: '#A236B2',
                secondaryColor: '#F4F4F4',
            })

            window.embedView.setCustomLogo({
                url: editorTopLogo,
            })

            window.embedView.setCustomProgress({
                url: editorLogo,
                text: "Loading PDF, please wait...",
            })
        })
    })

    loading.value = false
}

const toggleFullscreen = async () => {
    if (!mcpApp.value) return
    if (!isFullscreen.value) {
        console.log('Requesting fullscreen mode')
        window.embedView.setUIGroupVisible(["FloatBar"], true)
        await mcpApp.value.requestDisplayMode({ mode: 'fullscreen' })
        document.body.style.height = "100%"
        isFullscreen.value = true
    } else {
        console.log('Requesting inline mode')
        window.embedView.setUIGroupVisible(["FloatBar"], false)
        await mcpApp.value.requestDisplayMode({ mode: 'inline' })
        document.body.style.height = "600px"
        isFullscreen.value = false
    }
}

const downloadPDF = async () => {
    if (!mcpApp.value || !pdfShareUrl.value) return
    try {
        await mcpApp.value.openLink({ url: pdfShareUrl.value })
    } catch (e) {
        console.error('Failed to open PDF link:', e)
    }
}

const handleFullscreenChange = () => {
    console.log('Fullscreen change detected')
    isFullscreen.value = !!document.fullscreenElement
}

onMounted(async () => {
    const app = new App({ name: 'Foxit PDF Viewer', version: '1.0.0' })

    // Promise for tool result containing shareUrl
    const toolDataReady = new Promise<{ input: Record<string, unknown> | null; shareUrl: string | null }>((resolve) => {
        let input: Record<string, unknown> | null = null

        app.ontoolinput = (toolInput) => {
            if (!toolInput) {
                app.requestTeardown()
                return
            }
            input = toolInput
        }

        app.ontoolresult = (result) => {
            let shareUrl: string | null = null
            try {
                const textItem = result?.content?.find((c) => c.type === 'text')
                const text = textItem && 'text' in textItem ? textItem.text : undefined
                if (text) {
                    const parsed = JSON.parse(text)
                    shareUrl = parsed.shareUrl || null
                }
            } catch (e) {
                console.warn('Failed to parse shareUrl from tool result:', e)
            }
            resolve({ input, shareUrl })
        }
    })

    // Promise for Foxit Embed API ready
    const foxitReady = new Promise<void>((resolve) => {
        document.addEventListener("foxit_embed_api_ready", () => resolve(), { once: true })
    })

    // Load Foxit Embed API script
    const script = document.createElement('script')
    script.src = `https://embed.developer-api.foxit.com/embed-api-loader.js?clientId=${CLIENT_ID}`
    document.head.appendChild(script)

    // Connect to MCP host
    await app.connect()
    mcpApp.value = app

    // Wait for both Foxit API and tool data
    const [{ input, shareUrl: initialUrl }] = await Promise.all([toolDataReady, foxitReady])

    let url = initialUrl

    // Fallback: create share link via tool call if not in result
    if (!url && input?.document_id) {
        try {
            const result = await app.callServerTool({
                name: 'create_share_link',
                arguments: {
                    document_id: input.document_id as string,
                }
            })
            const textItem = result?.content?.find((c) => c.type === 'text')
            const text = textItem && 'text' in textItem ? textItem.text : undefined
            if (text) {
                const parsed = JSON.parse(text)
                url = parsed.shareUrl || null
            }
            console.log('Got shareUrl from callServerTool:', url)
        } catch (e) {
            console.error('Failed to get shareUrl via callServerTool:', e)
        }
    }

    if (!url) {
        console.error('No PDF URL available to display')
        loading.value = false
        return
    }

    pdfShareUrl.value = url
    initPdfViewer(url)

    document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
    document.removeEventListener('fullscreenchange', handleFullscreenChange)
})
</script>

<style scoped>
.pdf-viewer-container {
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    overflow: hidden;
}

#foxit-embed-view {
    height: 100%;
    width: 100%;
}

#fullscreen-btn,
#download-btn {
    position: fixed;
    right: 20px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    transition: all 0.3s;
    z-index: 9999;
}

#fullscreen-btn:hover,
#download-btn:hover {
    background-color: #D8DBE5;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    transform: scale(1.1);
}

#fullscreen-btn:active,
#download-btn:active {
    transform: scale(0.95);
}

#download-btn {
    bottom: 80px;
}

#fullscreen-btn {
    bottom: 20px;
}

:deep(.arco-dot-loading-item) {
    background-color: #A236B2;
}

#loading {
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}
</style>
