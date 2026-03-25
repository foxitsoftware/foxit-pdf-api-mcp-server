<template>
  <div class="box">
    <a-layout style="height: 100%px;">
      <a-layout-content>
        <div class="file-upload-container" v-if="fileList.length === 0">
          <!-- Upload Area -->
          <a-upload draggable multiple :auto-upload="false" :file-list="fileList" @change="handleFileChange"
            :show-file-list="false" :on-before-upload="handleBeforeUpload" :accept="acceptFileTypes">
            <template #upload-button>
              <div class="upload-area">
                <a-space direction="vertical" align="center">
                  <DocIcon style="width: 100px; height: 84px;" />
                  <div style="font-weight: 600;">Drag and Drop Your Files</div>
                  <div style="color:#8B8B8B; font-size: 14px; text-align: center; line-height: 1.3; padding:10px 0px;">
                    <div>Or, select them from your computer.</div>
                    <div>Max file size: 100MB</div>
                  </div>
                  <a-button type="primary" class="foxit-btn">Upload Files</a-button>
                </a-space>
              </div>
            </template>
          </a-upload>
        </div>


        <!-- File List -->
        <div class="file-list-section" v-if="fileList.length > 0">
          <div style="flex: 1;">
            <a-space direction="vertical" fill style="width: 100%;">
              <a-space :size="16" style="width: 100%; justify-content: space-between">
                <a-typography-title :heading="5" style="margin: 0; font-weight: 800;">
                  Uploaded Files ({{ fileList.length }})
                </a-typography-title>
                <a-upload multiple :auto-upload="false" @change="handleFileChange" :show-file-list="false"
                  :on-before-upload="handleBeforeUpload">
                  <template #upload-button>
                    <a-button class="add-files-btn">
                      <template #icon>
                        <icon-plus />
                      </template>
                      Add Files
                    </a-button>
                  </template>
                </a-upload>
              </a-space>

              <a-list :data="fileList" :bordered="false">
                <template #item="{ item, index }">
                  <a-list-item class="file-list-item" style="padding: 8px 15px;">
                    <a-space style="width: 100%; justify-content: space-between">
                      <a-space :size="14">
                        <icon-file :size="18" />
                        <a-typography-text class="fileName">{{ item.name }}</a-typography-text>
                        <a-typography-text type="secondary" style=" font-size: 12px; color: #8B8B8B;">
                          {{ formatFileSize(item.size) }}
                        </a-typography-text>
                      </a-space>

                      <a-space :size="8">
                        <LoadingIcon class="spinning" v-if="item.uploading" :size="18" />
                        <VectorIcon v-else-if="item.status === 'done'" :size="18" />
                        <ErrorIcon v-else-if="item.status === 'error'" :size="18" />
                        <a-button type="text" style="color: #666666;" @click="handleRemove(index)"
                          :disabled="item.uploading">
                          <template #icon>
                            <icon-delete :size="18" />
                          </template>
                        </a-button>
                      </a-space>
                    </a-space>
                  </a-list-item>
                </template>
              </a-list>
            </a-space>
          </div>
          <div style="display: flex; justify-content: flex-end; padding-top: 16px;">
            <a-button type="primary" class="foxit-btn" @click="handleProcessFiles" style="width: 87px;"
              :loading="isProcessing" :disabled="uploadDisabled()">Next</a-button>
          </div>
        </div>

        <a-layout-footer v-if="fileList.length === 0">
          <span v-if="fileList.length === 0">By uploading your files, you agree to Foxit's
            <a href="https://www.foxit.com/product/terms-of-service.html"> Terms of Use </a> and <a
              href="https://www.foxit.com/company/privacy-policy.html">Privacy
              Policy</a>.
          </span>
        </a-layout-footer>

      </a-layout-content>

    </a-layout>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import {
  IconFile,
  IconDelete,
  IconPlus,
} from '@arco-design/web-vue/es/icon'
import DocIcon from '@/svg/doc.svg?component'
import ErrorIcon from '@/svg/error.svg?component'
import LoadingIcon from '@/svg/loading.svg?component'
import VectorIcon from '@/svg/vector.svg?component'
import { App } from '@modelcontextprotocol/ext-apps'

// Define file item type
interface ExtendedFileItem {
  uid: string
  name?: string
  size?: number
  file?: File
  status?: 'uploading' | 'done' | 'error'
  documentId?: string  // documentId returned by MCP
  uploading?: boolean
}

const fileList = ref<ExtendedFileItem[]>([])
const isProcessing = ref(false)
const mcpApp = ref<App | null>(null)
const toolInput = ref<Record<string, unknown> | null>(null)

onMounted(async () => {
  const app = new App({ name: 'Foxit PDF Tools', version: '1.0.0' })

  app.ontoolinput = (input) => {
    toolInput.value = input
    if (input === null) {
      app.requestTeardown()
    }
  }

  await app.connect()
  mcpApp.value = app
})

const uploadDisabled = () => {
  return fileList.value.filter(f => f.status === 'uploading').length > 0 || fileList.value.filter(f => f.status === 'done').length === 0
}

// Upload single file to server
const uploadFile = async (fileItem: ExtendedFileItem) => {
  if (!fileItem.file || !mcpApp.value) return

  const index = fileList.value.findIndex(f => f.uid === fileItem.uid)
  if (index === -1) return

  try {
    const base64Content = await fileToBase64(fileItem.file)
    const result = await mcpApp.value.callServerTool({
      name: 'upload_document',
      arguments: {
        file_content: base64Content,
        file_name: fileItem.name
      }
    })

    const textItem = result?.content?.find((c) => c.type === 'text')
    const textContent = textItem && 'text' in textItem ? textItem.text : undefined
    if (!textContent) {
      throw new Error('upload_document did not return text content')
    }
    const parsed = JSON.parse(textContent)

    if (!parsed?.success) {
      const errorMessage = parsed?.error?.message || parsed?.message || 'Upload failed on server side'
      throw new Error(errorMessage)
    }
    if (!parsed?.resultDocumentId) {
      throw new Error('upload_document did not return resultDocumentId')
    }

    fileList.value[index].documentId = parsed.resultDocumentId
    fileList.value[index].status = 'done'
    fileList.value[index].uploading = false
  } catch (error) {
    console.error('Upload error:', error)
    fileList.value[index].status = 'error'
    fileList.value[index].uploading = false
    const message = error instanceof Error ? error.message : 'Unknown error'
    Message.error(`Failed to upload ${fileItem.name}: ${message}`)
  }
}

// Allowed file types
const allowedExtensions = [
  // PDF
  '.pdf',
  // Office documents
  '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
  // Text files
  '.txt',
  // Images
  '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif',
  // HTML files
  '.html',
]

const acceptFileTypes = allowedExtensions.join(',')

// File validation
const validateFile = (file: File): { valid: boolean; error?: string } => {
  // Validate file size (100MB = 100 * 1024 * 1024 bytes)
  const maxSize = 100 * 1024 * 1024
  if (file.size > maxSize) {
    return { valid: false, error: `File "${file.name}" exceeds 100MB limit` }
  }

  const fileName = file.name.toLowerCase()
  const isAllowed = allowedExtensions.some(ext => fileName.endsWith(ext))

  if (!isAllowed) {
    return { valid: false, error: `File "${file.name}" format not supported. Only PDF, Office documents (Word, Excel, PowerPoint), TXT, images, and HTML files are allowed` }
  }

  return { valid: true }
}

// Before upload handler - validate and reject invalid files
const handleBeforeUpload = (file: any) => {
  const actualFile = file.file || file
  const validation = validateFile(actualFile)
  if (!validation.valid) {
    Message.error(validation.error || 'File validation failed')
    return false // Reject the file
  }
  return true // Accept the file
}

// Convert file to base64
const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const base64 = reader.result as string
      const base64Content = base64.split(',')[1]
      resolve(base64Content)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

// Handle file change
const handleFileChange = async (fileItemList: any[]) => {
  for (const file of fileItemList) {
    // Generate UID based on file properties
    const uid = `${file.file.name}-${file.file.size}-${file.file.lastModified}`

    // Skip if already exists in list
    if (fileList.value.some(f => f.uid === uid)) continue

    const newFile: ExtendedFileItem = {
      uid,
      name: file.file.name,
      size: file.file.size,
      file: file.file,
      status: 'uploading',
      uploading: true
    }

    fileList.value.push(newFile)
    uploadFile(newFile)
  }
}

// Handle file processing (call MCP server tools)
const handleProcessFiles = async () => {
  const uploadedFiles = fileList.value.filter(f => f.documentId && f.status === 'done')
  if (uploadedFiles.length === 0) {
    Message.warning('No files uploaded yet')
    return
  }

  if (!mcpApp.value) {
    Message.error('MCP App not connected')
    return
  }

  try {
    isProcessing.value = true

    // Build message containing document IDs
    const fileDetails = uploadedFiles.map(f => `- Document ID: ${f.documentId} (${f.name})`).join('\n')
    const userIntent = toolInput.value?.user_intent ?? ''
    const prompt = `
    user_intent: [${userIntent}]
    uploaded_documents:
      ${fileDetails}
    Please invoke the mcp tool according to the user_intent and the uploaded documents.`
    console.log('Sending prompt:', prompt)
    await mcpApp.value.sendMessage({ role: 'user', content: [{ type: 'text', text: prompt }] })
  } catch (error) {
    console.error('Failed to send message:', error)
  } finally {
    isProcessing.value = false
    mcpApp.value?.requestTeardown()
  }
}

const handleRemove = (index: number) => {
  fileList.value.splice(index, 1)
}

const formatFileSize = (bytes: number | undefined): string => {
  if (!bytes) return '0 B'

  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${size.toFixed(2)} ${units[unitIndex]}`
}
</script>

<style scoped>
body {
  font-family: Segoe UI;
}

.file-upload-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
}

.file-list-section {
  background-color: #FBFBFD;
  overflow-y: auto;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

.file-list-item:not(:last-child) {
  border-bottom: none;
}

.file-list-item {
  background-color: #F5F6FA;
  margin: 15px 0;
  border-radius: 5px;
}

.box :deep(.arco-layout-footer),
.box :deep(.arco-layout-content) {
  display: flex;
  flex-direction: column;
  justify-content: center;
  font-stretch: condensed;
  text-align: center;
}

.box :deep(.arco-layout-footer) {
  height: 64px;
  color: #8B8B8B;
  padding-right: 3%;
}

.box :deep(.arco-layout) {
  height: 100%;
}

.box :deep(.arco-layout-content) {
  /* Dashed border with rounded corners */
  border: 1.5px dashed var(--Border-Frame_border, #C7CCD9);
  padding: 2%;
  border-radius: 10px;
  background-color: #FBFBFD;
  align-items: center;
  height: 100%;
  flex: 1;
}

.box {
  height: 500px;
  padding: 10px 10px;
}

.arco-btn {
  border-radius: 8px;
}

.arco-btn.foxit-btn {
  font-weight: 600;
  background-color: #A236B2;
}

.arco-btn.foxit-btn.arco-btn-primary:hover {
  background-color: #872290;
}

.arco-btn.foxit-btn.arco-btn-disabled {
  background-color: #E0C6F0;
  border-color: #E0C6F0;
}

.arco-btn.foxit-btn.arco-btn-disabled:hover {
  background-color: #E0C6F0;
}

/* Rotation animation */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

.spinning {
  animation: spin 1s linear infinite;
}

.add-files-btn {
  background-color: #FBFBFD;
  border-color: #C7CCD9;
  font-weight: 600;
}

.fileName {
  font-weight: 600;
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
