import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '@/views/Stocks/HomeView.vue'
import ImportView from '@/views/Stocks/ImportView.vue'
import OrdersView from '@/views/Stocks/OrdersView.vue'
import PurchasesView from '@/views/Stocks/PurchasesView.vue'
import CompleteOrderView from '@/views/Stocks/CompleteOrderView.vue'
import SingleSupplierOrderView from '@/views/Stocks/SingleSupplierOrderView.vue'
import SingleOrderView from '@/views/Trade/SingleOrderView.vue'

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
    {
      path: '/order/:id/',  
      name: 'orderDetail',
      component: SingleOrderView,
    },
    {
      path: '/order/new/',
      name: 'orderDetail',
      component: SingleOrderView,
    },
    {
      path: '/invoice/new/',
      name: 'createInvoice',
      component: SingleOrderView,
    },
    {
      path: '/invoice/:id/',
      name: 'editInvoice',
      component: SingleOrderView,
    }
  ],
})

export default router
