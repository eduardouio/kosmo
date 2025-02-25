import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ImportView from '@/views/ImportView.vue'
import OrdersView from '@/views/OrdersView.vue'
import PurchasesView from '@/views/PurchasesView.vue'
import CompleteOrderView from '@/views/CompleteOrderView.vue'
import SingleSupplierOrderView from '@/views/SingleSupplierOrderView.vue'

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
      name: 'customerOrders',
      component: OrdersView,
    },
    {
      path: '/suppliers-orders/',
      name: 'suppliersOrders',
      component: PurchasesView,
    },
    {
      path: '/order-detail/:id/',
      name: 'customerOrderDetail',
      component: CompleteOrderView,
    },
    {
      path: '/supplier-order-detail/:id/',
      name: 'supplierOrderDetail',
      component: SingleSupplierOrderView,
    },
  ],
})

export default router
