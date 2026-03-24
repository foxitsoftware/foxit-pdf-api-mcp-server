import { createApp } from 'vue'
import ArcoVue from '@arco-design/web-vue'
import '@arco-design/web-vue/dist/arco.css'
import PdfViewer from './components/PdfViewer.vue'

const app = createApp(PdfViewer)
app.use(ArcoVue)
app.mount('#app')
