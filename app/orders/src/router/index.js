import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ImportView from '@/views/ImportView.vue'
import OrdersView from '@/views/OrdersView.vue'
import PurchasesView from '@/views/PurchasesView.vue'

const router = createRouter({
  history: createWebHashHistory(),
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
    {
      path: '/suppliers-orders/',
      name: 'suppliers_orders',
      component: PurchasesView,
    },
  ],
})

export default router
