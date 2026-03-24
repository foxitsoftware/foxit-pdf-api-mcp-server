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
import { onMounted, ref, watch, onUnmounted } from 'vue'
import FullScreenIcon from '@/svg/full_screen.svg?component'
import FileDownloadIcon from '@/svg/file_download.svg?component'
declare global {
    interface Window {
        FoxitEmbed: any
        embedView: any
    }
}

const getBridge = () => {
    const mcp = window.mcpClient
    const openai = window.openai
    return {
        toolInput: mcp?.toolInput ?? openai?.toolInput,
        toolOutput: mcp?.toolOutput ?? openai?.toolOutput,
        callTool: mcp?.callTool ?? openai?.callTool,
        uploadFile: mcp?.uploadFile ?? openai?.uploadFile,
        getFileDownloadUrl: mcp?.getFileDownloadUrl ?? openai?.getFileDownloadUrl,
        requestDisplayMode: mcp?.requestDisplayMode ?? openai?.requestDisplayMode,
        openExternal: mcp?.openExternal ?? openai?.openExternal,
        requestClose: mcp?.requestClose ?? openai?.requestClose,
        displayMode: mcp?.displayMode ?? openai?.displayMode,
    }
}

const CLIENT_ID = "dadfa204c63194751e17dcae936f03eb"
const isFullscreen = ref(false)
const loading = ref(true)
const displayMode = ref<string>('')

// Watch displayMode changes
watch(displayMode, (newMode, oldMode) => {
    console.log('Display mode changed:', { from: oldMode, to: newMode })
})

// Poll for displayMode changes
let displayModeInterval: number | null = null


const initPdfViewer = async () => {
    const bridge = getBridge()
    if (!bridge.toolInput) {
        bridge.requestClose?.()
        return
    }
    const toolInput = bridge.toolInput
    console.log('Tool input received:', toolInput)

    let pdfUrl: string | null = null

    // Try to get share URL from tool output first (pre-created by server)
    try {
        const toolOutput = bridge.toolOutput
        const rawOutput = toolOutput?.result || toolOutput?.structuredContent?.result
        if (rawOutput) {
            const output = JSON.parse(typeof rawOutput === 'string' ? rawOutput : JSON.stringify(rawOutput))
            if (output.shareUrl) {
                pdfUrl = output.shareUrl
                console.log('Got shareUrl from toolOutput:', pdfUrl)
            }
        }
    } catch (e) {
        console.warn('Failed to parse shareUrl from toolOutput:', e)
    }

    // Fall back to callTool if shareUrl not available
    if (!pdfUrl && bridge.callTool) {
        try {
            const result = await bridge.callTool('create_share_link', {
                document_id: toolInput.document_id,
            })
            const rawToolResponse = result?.result || result?.structuredContent?.result
            const parsed = JSON.parse(rawToolResponse)
            pdfUrl = parsed.shareUrl
            console.log('Got shareUrl from callTool:', pdfUrl)
        } catch (e) {
            console.error('Failed to get shareUrl via callTool:', e)
        }
    }

    if (!pdfUrl) {
        console.error('No PDF URL available to display')
        loading.value = false
        return
    }

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

    const editorLogo = (await import('@/svg/editor_logo.svg?url')).default;
    const editorTopLogo = (await import('@/svg/editor_top_logo.svg?url')).default;

    window.embedView.setUIElementsVisible(["Save", "OpenFile"], false);
    window.embedView.setUIGroupVisible(["More", "FloatBar"], false);

    window.embedView.setTheme({
        primaryColor: '#A236B2',
        secondaryColor: '#F4F4F4',
    })

    window.embedView.setCustomLogo({
        url: editorTopLogo,
    });

    window.embedView.setCustomProgress({
        url: editorLogo, // url to a custom loading image
        text: "Loading PDF, please wait...",
    });

    loading.value = false
}

const toggleFullscreen = () => {
    const bridge = getBridge()
    console.log('Current display mode:', bridge.displayMode)
    if (bridge.displayMode === "inline") {
        console.log('Requesting fullscreen mode')
        window.embedView.setUIGroupVisible(["FloatBar"], true);
        bridge.requestDisplayMode?.({ mode: "fullscreen" })
        document.body.style.height = "100%"
    } else {
        console.log('Requesting inline mode')
        window.embedView.setUIGroupVisible(["FloatBar"], false);
        bridge.requestDisplayMode?.({ mode: "inline" })
        document.body.style.height = "600px"
    }
}

const downloadPDF = async () => {
    loading.value = true
    let bufferArray: ArrayBuffer[] = []

    await window.embedView.pdfDoc
        .getStream(function ({ arrayBuffer }: { arrayBuffer: ArrayBuffer; offset: number; size: number }) {
            if (arrayBuffer) {
                bufferArray.push(arrayBuffer)
            }
        })
        .then(async function () {
            const bridge = getBridge()
            const blob = new Blob(bufferArray, { type: "application/pdf" })
            const file = new File([blob], "Embed API Demo.pdf", { type: "application/pdf" })
            const { fileId } = await bridge.uploadFile?.(file)
            const { downloadUrl } = await bridge.getFileDownloadUrl?.({ fileId });

            console.log('PDF Download URL:', downloadUrl)
            await bridge.openExternal?.({ href: downloadUrl })
        }).finally(() => {
            loading.value = false
        })
}

const handleFullscreenChange = () => {
    console.log('Fullscreen change detected')
    isFullscreen.value = !!document.fullscreenElement
}

onMounted(() => {
    // Load Foxit Embed API script
    const script = document.createElement('script')
    script.src = `https://embed.developer-api.foxit.com/embed-api-loader.js?clientId=${CLIENT_ID}`
    document.head.appendChild(script)

    // Wait for API ready event
    document.addEventListener("foxit_embed_api_ready", initPdfViewer)

    // Listen for fullscreen changes
    document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
    if (displayModeInterval) {
        clearInterval(displayModeInterval)
    }
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
