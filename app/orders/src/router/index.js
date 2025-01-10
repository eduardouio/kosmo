import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ImportView from '@/views/ImportView.vue'
import OrdersView from '@/views/OrdersView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/import/',
      name: 'import',
      component: ImportView,
    },
    {
      path: '/customer-orders/',
      name: 'customer_orders',
      component: OrdersView,
    },
  ],
})

export default router
