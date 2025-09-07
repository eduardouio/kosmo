import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '@/views/Stocks/HomeView.vue'
import ImportView from '@/views/Stocks/ImportView.vue'
import OrdersView from '@/views/Stocks/OrdersView.vue'
import PurchasesView from '@/views/Stocks/PurchasesView.vue'
import CompleteOrderView from '@/views/Stocks/CompleteOrderView.vue'
import SingleSupplierOrderView from '@/views/Stocks/SingleSupplierOrderView.vue'
import SingleOrderView from '@/views/Trade/SingleOrderView.vue'
import SingleEditOrderViewVue from '@/views/Trade/SingleEditOrderView.vue'
import PaymentCreateView from '@/views/Payments/PymentCreateView.vue'

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
      component: SingleEditOrderViewVue,
    },
    {
      path: '/order/new/',
      name: 'createOrder',
      component: SingleOrderView,
    },
    {
      path: '/payment/new/',
      name: 'PaymentCreateView',
      component: PaymentCreateView,
    }
  ],
})

// Variables para controlar navegación y prevenir loops
let navigationHistory = []
let isNavigating = false
let redirectionTimeout = null

// Función para detectar loops de navegación
const isNavigationLoop = (to, from) => {
  const currentTime = Date.now()
  const navigation = `${from.name}->${to.name}`
  
  // Agregar navegación al historial
  navigationHistory.push({ navigation, time: currentTime })
  
  // Mantener solo las últimas 5 navegaciones
  if (navigationHistory.length > 5) {
    navigationHistory.shift()
  }
  
  // Detectar si hay más de 3 navegaciones similares en los últimos 3 segundos
  const recentSimilar = navigationHistory.filter(nav => 
    nav.navigation === navigation && 
    (currentTime - nav.time) < 3000
  )
  
  return recentSimilar.length > 3
}

// Guard para prevenir loops
router.beforeEach((to, from, next) => {
  // Prevenir navegaciones múltiples simultáneas
  if (isNavigating) {
    console.warn('[Router] Navegación bloqueada - ya hay una en progreso')
    return next(false)
  }
  
  // Detectar loops de navegación
  if (isNavigationLoop(to, from)) {
    console.error('[Router] Loop detectado, bloqueando navegación:', from.name, '->', to.name)
    return next(false)
  }
  
  // Cancelar redirecciones automáticas pendientes si el usuario navega manualmente
  if (redirectionTimeout) {
    clearTimeout(redirectionTimeout)
    redirectionTimeout = null
  }
  
  // Log para debug en producción
  console.log('[Router] Navegando:', from.name, '->', to.name)
  
  isNavigating = true
  next()
})

router.afterEach((to, from) => {
  // Resetear flag después de navegación exitosa
  setTimeout(() => {
    isNavigating = false
  }, 100)
})

// Función utilitaria para navegación segura
export const safeNavigate = (routeName, params = {}, delay = 100) => {
  if (isNavigating) {
    console.warn('[Router] Navegación cancelada - ya hay una en progreso')
    return Promise.reject(new Error('Navigation in progress'))
  }
  
  // Cancelar redirección pendiente
  if (redirectionTimeout) {
    clearTimeout(redirectionTimeout)
  }
  
  return new Promise((resolve, reject) => {
    redirectionTimeout = setTimeout(() => {
      redirectionTimeout = null
      router.push({ name: routeName, ...params })
        .then(resolve)
        .catch(err => {
          console.error('[Router] Error en navegación:', err)
          isNavigating = false
          reject(err)
        })
    }, delay)
  })
}

// Cancelar redirecciones pendientes
export const cancelPendingRedirects = () => {
  if (redirectionTimeout) {
    clearTimeout(redirectionTimeout)
    redirectionTimeout = null
    console.log('[Router] Redirecciones pendientes canceladas')
  }
}

export default router
