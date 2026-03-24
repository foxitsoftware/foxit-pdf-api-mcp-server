import { createApp } from 'vue'
import ArcoVue from '@arco-design/web-vue'
import '@arco-design/web-vue/dist/arco.css'
import FileUpload from './components/FileUpload.vue'

const app = createApp(FileUpload)
app.use(ArcoVue)
app.mount('#app')
