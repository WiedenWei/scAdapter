import { createRouter, createWebHistory} from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import StatusView from '../views/StatusView.vue'
import AboutView from '../views/AboutView.vue'

const routes: Array<RouteRecordRaw> = [
  { path: '/', name: 'Home', component: HomeView },
  { path: '/status', name: 'Status', component: StatusView },
  { path: '/about', name: 'About', component: AboutView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
