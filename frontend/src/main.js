import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import '@/assets/scss/custom.scss'
import axios from 'axios'

import App from './App.vue'
import router from './router'

// --- AXIOS GLOBAL CONFIGURATION ---

// Always send cookies with requests
axios.defaults.withCredentials = true;

// Base url
axios.defaults.baseURL = 'http://localhost:5000';
// ----------------------------------

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
