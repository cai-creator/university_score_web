import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import localeData from 'dayjs/plugin/localeData'

// 配置Day.js
dayjs.locale('zh-cn')
dayjs.extend(localeData)

const app = createApp(App)

// 配置Ant Design Vue
app.use(Antd)

// 配置路由
app.use(router)

app.mount('#app')
