<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useBaseStore } from '@/stores/baseStore.js'
import { useSingleOrderStore } from '@/stores/trade/singleOrderStore.js'

import { appConfig } from '@/AppConfig'
import AutocompleteSupplier from '@/components/common/AutocompleteSupplier.vue'
import GenericProductModal from '@/components/common/GenericProductModal.vue'
import Loader from '@/components/Sotcks/Loader.vue'
import OrderLine from '@/components/trade/OrderLine.vue'

import {
    IconDeviceFloppy,
    IconSettings,
    IconPlus,
    IconBan,
    IconArrowLeft
} from '@tabler/icons-vue';

const route = useRoute()
const baseStore = useBaseStore()
const stagesToLoad = ref(3)
const orderStore = useSingleOrderStore()
const selectedCustomer = ref(null)
const selectedSupplier = ref(null)
const selectedProduct = ref(null)
const errorMessage = ref('')
const hasError = ref(false)
const isLoading = ref(true)
const orderId = computed(() => route.params.id)

// computed
const formLoading = computed(() => {
  return baseStore.stagesLoaded != stagesToLoad.value
})

async function loadOrderData() {
    console.log("Cargando datops de pedido existente")
  if (!orderId.value) {
    errorMessage.value = 'ID de orden no proporcionado'
    hasError.value = true
    isLoading.value = false
    return
  }
  
  isLoading.value = true
  try {
    const result = await orderStore.loadOrder(orderId.value, baseStore)
    
    if (result.success) {
      selectedCustomer.value = baseStore.selectedCustomer
      selectedSupplier.value = baseStore.selectedSupplier
      calculateOrderTotals()
      validateData()
    } else {
      errorMessage.value = orderStore.errorMessage
      hasError.value = true
    }
  } catch (error) {
    console.error('Error al cargar la orden:', error)
    errorMessage.value = `Error al cargar la orden: ${error.message}`
    hasError.value = true
  } finally {
    isLoading.value = false
  }
}

function showProductModal($event) {
  selectedProduct.value = $event
}

function onSelectCustomer(customer) {
  // Esta función ya no se utilizará activamente, pero la mantenemos 
  // por si se necesita para la carga inicial de datos
  selectedCustomer.value = customer
  baseStore.selectedCustomer = customer
}

function onSelectSupplier(supplier) {
  selectedSupplier.value = supplier
  baseStore.selectedSupplier = supplier
}

// Calcular totales del documento
function calculateOrderTotals() {
  let hb_total = 0
  let qb_total = 0
  let fb_total = 0
  let total_stem_flower = 0
  let total_price = 0
  let total_margin = 0
  let total_bunches = 0  // Añadimos esta variable para calcular el total de bunches

  const lines = orderStore.orderLines.slice()
  lines.forEach(line => {
    // Asegurarse que quantity es un número
    const quantity = Number(line.quantity) || 0;
    if (line.box_model === 'HB') hb_total += quantity;
    if (line.box_model === 'QB') qb_total += quantity;

    if (Array.isArray(line.order_box_items)) {
      line.order_box_items.forEach(item => {
        // Asegurarnos de limpiar cualquier formato y convertir a número
        const qtyStems = parseFloat(String(item.qty_stem_flower || '0').replace(/,/g, '')) || 0;
        const costPrice = parseFloat(String(item.stem_cost_price || '0.00').replace(/,/g, '')) || 0;
        const profitMargin = parseFloat(String(item.profit_margin || '0.00').replace(/,/g, '')) || 0;
        const bunches = parseInt(String(item.total_bunches || '0')) || 0; // Calcular bunches

        total_stem_flower += qtyStems;
        total_price += costPrice * qtyStems;
        total_margin += profitMargin * qtyStems;
        total_bunches += bunches * quantity; // Multiplicar por la cantidad del item
      })
    }
  })

  // FB = (HB/2) + (QB/4)
  fb_total = (hb_total / 2) + (qb_total / 4)

  // Asegurarnos que los valores son números válidos antes de asignarlos
  orderStore.updateOrderTotals({
    hb_total: parseFloat(hb_total.toFixed(2)),
    qb_total: parseFloat(qb_total.toFixed(2)),
    fb_total: parseFloat(fb_total.toFixed(2)),
    total_stem_flower: parseFloat(total_stem_flower.toFixed(2)),
    total_price: parseFloat(total_price.toFixed(2)),
    total_margin: parseFloat(total_margin.toFixed(2)),
    total_bunches: parseInt(total_bunches) // Añadir total_bunches al objeto que actualiza el store
  })
}

// Recalcular totales cuando cambian las líneas - versión mejorada
let totalCalculationTimeout = null;
watch(() => orderStore.orderLines, () => {
  clearTimeout(totalCalculationTimeout);
  totalCalculationTimeout = setTimeout(calculateOrderTotals, 200);
}, { deep: true })

function addOrderLine() {
  orderStore.addOrderLine()
}

function removeOrderLine(index) {
  orderStore.removeOrderLine(index)
}

function updateOrderLineTotal(idx, tempLine) {
  // Actualiza la línea con los nuevos valores y recalcula el total
  orderStore.orderLines[idx].quantity = tempLine.quantity
  orderStore.orderLines[idx].box_model = tempLine.box_model
  orderStore.orderLines[idx].order_box_items = tempLine.order_box_items
  orderStore.updateOrderLineTotal(idx)
}

function validateData(){
  // validamos datos minimos de orden de venta
  hasError.value = false;
  errorMessage.value = '';

  if (!baseStore.selectedCustomer || !baseStore.selectedSupplier) {
    errorMessage.value = 'Debe seleccionar un cliente y un proveedor.';
    hasError.value = true;
    return false;
  }
  if (orderStore.orderLines.length === 0) {
    errorMessage.value = 'Debe agregar al menos una línea de pedido.';
    hasError.value = true;
    return false;
  }

  // Usar bucle for tradicional en lugar de forEach para poder retornar correctamente
  for (let i = 0; i < orderStore.orderLines.length; i++) {
    const line = orderStore.orderLines[i];
    if (!line.quantity) {
      errorMessage.value = 'Cada línea debe tener cantidad y modelo de caja.';
      hasError.value = true;
      return false;
    }
    
    if (Array.isArray(line.order_box_items)) {
      for (let j = 0; j < line.order_box_items.length; j++) {
        const itm = line.order_box_items[j];
        // Verificar si product es un objeto válido y tiene la propiedad variety
        if (!itm.qty_stem_flower || !itm.product || !itm.stem_cost_price || !itm.profit_margin ) {
          errorMessage.value = 'Cada item debe tener cantidad y producto.';
          hasError.value = true;
          return false;
        }
      }
    }
  }

  // Si llega hasta aquí, no hay errores
  return true;
}

async function updateOrder() {
  const result = await orderStore.updateOrder(
    orderId.value,
    baseStore.selectedCustomer, 
    baseStore.selectedSupplier
  )
  if (result.success) {
    window.location.href =  `${appConfig.apiBaseUrlTest}/trade/order/${orderId.value}/`
  } else {
    alert(result.message)
  }
}

onMounted(async () => {
  baseStore.loadSuppliers()
  baseStore.loadProducts()
  baseStore.loadCustomers(true)
  await loadOrderData()
  
  setInterval(() => {
    validateData()
  }, 2000)
})

// Agregar función de navegación por teclado
const handleKeydown = (event) => {
    const targetElement = event.target;

    // Solo actuar si el target es un input/select de nuestra clase y no es readonly/disabled
    if (!targetElement.matches('.trade-nav-input:not([readonly]):not([disabled])')) {
        return;
    }

    // Obtener todos los inputs/selects navegables que están actualmente visibles y no deshabilitados
    const allNavigableInputs = Array.from(document.querySelectorAll('.trade-nav-input:not([readonly]):not([disabled])'));
    const visibleNavigableInputs = allNavigableInputs.filter(input => {
        const style = window.getComputedStyle(input);
        return style.display !== 'none' && style.visibility !== 'hidden' && input.tabIndex !== -1;
    });

    const currentIndex = visibleNavigableInputs.indexOf(targetElement);

    if (event.key === 'Enter') {
        event.preventDefault(); // Prevenir comportamiento por defecto
        
        let nextIndex;
        if (event.shiftKey) { // Shift + Enter: Moverse al anterior
            nextIndex = currentIndex - 1;
        } else { // Enter: Moverse al siguiente
            nextIndex = currentIndex + 1;
        }

        if (nextIndex >= 0 && nextIndex < visibleNavigableInputs.length) {
            const nextInput = visibleNavigableInputs[nextIndex];
            nextInput.focus();
            // Siempre seleccionar todo el texto al navegar
            if (typeof nextInput.select === 'function') {
                nextInput.select(); // Seleccionar texto si es un input de texto/número
            }
        }
    }
};
</script>
<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-1"></div>
      <div class="col-10">
    <Loader :show="formLoading || isLoading" />
    <div v-if="!formLoading && !isLoading" class="bg-light py-4">
      <div class="bg-white shadow-lg border border-2 border-warning rounded-3 p-4 mx-auto">
        <!-- Encabezado -->
         <div class="row">
          <div class="col text-center fs-2 text-kosmo-secondary">
            EDITAR ORDEN DE VENTA
          </div>
         </div>
        <div class="row mb-4 align-items-center">
          <div class="col-9">
            <img src="https://kosmoflowers.com/wp-content/uploads/2022/07/Mesa-de-trabajo-6.svg" class="img-fluid" style="height: 60px"/>
          </div>
          <div class="col-3">
            <div class="border border-2 border-warning p-2 rounded">
              <div class="d-flex justify-content-end align-items-center mb-1">
                <span class="small fw-bold me-2">PEDIDO:</span>
                <span class="text-danger fs-4">{{ orderStore.order.serie }}-0000{{ orderStore.order.consecutive }}</span>
              </div>
              <div class="d-flex justify-content-end align-items-center border-top border-success pt-1">
                <span class="small fw-bold me-2">FECHA:</span>
                <span class="fs-4">{{ orderStore.order.date }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Información del cliente y proveedor -->
        <div class="row mb-4">
          <div class="col-6">
            <div class="border border-2 border-warning p-3 rounded h-100">
              <h6 class="fw-bold mb-3">Información del Cliente</h6>
              <div class="mb-3">
                <!-- Reemplazar el autocomplete por un campo de solo lectura -->
                <div class="form-control bg-light">
                  {{ baseStore.selectedCustomer?.name || 'Cliente no seleccionado' }}
                </div>
              </div>
              <div v-if="baseStore.selectedCustomer">
                <p class="small mb-1"><strong>Dirección:</strong> {{ baseStore.selectedCustomer.address || 'No disponible' }}</p>
                <p class="small mb-1"><strong>Ciudad - País:</strong> {{ baseStore.selectedCustomer.city || 'No disponible' }} - {{ baseStore.selectedCustomer.country || 'No disponible' }}</p>
                <div class="d-flex justify-content-between">
                  <p class="small mb-1"><strong>Email:</strong> {{ baseStore.selectedCustomer.email || 'No disponible' }}</p>
                  <p class="small mb-1"><strong>Crédito:</strong> {{ baseStore.selectedCustomer.credit || 'No disponible' }}</p>
                </div>
              </div>
              <div v-else>
                <p class="small mb-1 text-muted">Información del cliente no disponible.</p>
              </div>
            </div>
          </div>
          <div class="col-6">
            <div class="border border-2 border-warning p-3 rounded h-100">
              <h6 class="fw-bold mb-3">Información del Proveedor</h6>
              <div class="mb-3">
                <AutocompleteSupplier @select="onSelectSupplier" :initialValue="baseStore.selectedSupplier?.name"/>
              </div>
              <div v-if="baseStore.selectedSupplier">
                <p class="small mb-1"><strong>Dirección:</strong> {{ baseStore.selectedSupplier.address || 'No disponible' }}</p>
                <p class="small mb-1"><strong>Ciudad - País:</strong> {{ baseStore.selectedSupplier.city || 'No disponible' }} - {{ baseStore.selectedSupplier.country || 'No disponible' }}</p>
                <div class="d-flex justify-content-between">
                  <p class="small mb-1"><strong>Email:</strong> {{ baseStore.selectedSupplier.email || 'No disponible' }}</p>
                  <p class="small mb-1"><strong>Crédito:</strong> {{ baseStore.selectedSupplier.credit || 'No disponible' }}</p>
                </div>
              </div>
              <div v-else>
                <p class="small mb-1 text-muted">Seleccione un proveedor para ver la información de contacto.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Tabla de productos -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="table-responsive">
              <table class="table table-bordered table-sm" @keydown="handleKeydown">
                <thead class="bg-warning bg-opacity-25">
                  <tr class="text-center">
                    <th class="bg-gray-200 bg-gradient">Cant</th>
                    <th class="bg-gray-200 bg-gradient">Mod</th>
                    <th class="d-flex gap-1 bg-gray-200 bg-gradient">
                      <span style="width: 45%;">Variedad</span>
                      <span class="" style="width: 8%;">Largo CM</span>
                      <span class="" style="width: 8%;">Bunches</span>
                      <span class="" style="width: 8%;">T/B</span>
                      <span class="" style="width: 10%;">Costo</span>
                      <span class="" style="width: 10%;">Margen</span>
                      <span class="" style="width: 10%;">Total U</span>
                      <span class="" style="width: 10%;">Total</span>
                    </th>
                    <th class="bg-red-400 bg-gradient"><IconSettings size="15" stroke="1.5"/> </th>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="(line, idx) in orderStore.orderLines" :key="idx">
                    <OrderLine
                      v-model:quantity="line.quantity"
                      v-model:box_model="line.box_model"
                      v-model:boxItems="line.order_box_items"
                      @showProductModal="showProductModal"
                      @remove="removeOrderLine(idx)"
                    />
                  </template>
                  <tr>
                    <td colspan="4" class="text-end">
                      <button class="btn btn-default btn-sm" @click="addOrderLine">
                        <IconPlus size="15" stroke="1.5" class="text-primary"/>
                        Agregar
                      </button>
                    </td>
                     <td></td> <!-- Celda vacía para alinear con la columna de eliminar -->
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Totales -->
        <div class="row mb-4">
          <div class="col-6">
            <div class="bg-light bg-gradient rounded shadow-sm p-3 border-gray-500">
              <div class="row">
                <div class="col-8 text-end border-end fs-6 fw-bold">TOTAL HB:</div>
                <div class="col-4 text-end fs-6 fw-bold">{{ orderStore.order.hb_total }}</div>
              </div>
              <div class="row">
                <div class="col-8 text-end border-end fs-6 fw-bold">TOTAL QB:</div>
                <div class="col-4 text-end fs-6 fw-bold">{{ orderStore.order.qb_total }}</div>
              </div>
              <div class="row">
                <div class="col-8 text-end border-end fs-6 fw-bold">TOTAL FB:</div>
                <div class="col-4 text-end fs-6 fw-bold">{{ orderStore.order.fb_total }}</div>
              </div>
              <div class="row">
                <div class="col-8 text-end border-end fs-6 fw-bold">TOTAL TALLOS:</div>
                <div class="col-4 text-end fs-6 fw-bold">{{ orderStore.order.total_stem_flower }}</div>
              </div>
              <div class="row">
                <div class="col-8 text-end border-end fs-6 fw-bold">TOTAL BUNCHES:</div>
                <div class="col-4 text-end fs-6 fw-bold">{{ orderStore.order.total_bunches }}</div>
              </div>
            </div>
          </div>
          <div class="col-6">
            <div class="bg-light bg-gradient rounded shadow-sm p-3 border-gray-500">
              <div class="row mt-4">
                <div class="col-7 text-end border-end text-success fs-6"><strong>Costo:</strong></div>
                <div class="col-5 text-end text-success fs-6">
                  ${{ typeof orderStore.order.total_price === 'number' ? orderStore.order.total_price.toFixed(2) : '0.00' }}
                </div>
              </div>
              <div class="row">
                <div class="col-7 text-end border-end text-success fs-6"><strong>Margen:</strong></div>
                <div class="col-5 text-end text-success fs-6">
                  ${{ typeof orderStore.order.total_margin === 'number' ? orderStore.order.total_margin.toFixed(2) : '0.00' }}
                </div>
              </div>
              <div class="row mb-1">
                <div class="col-7 text-end border-end text-success fs-6"><strong>Total Factura:</strong></div>
                <div class="col-5 text-end text-success fs-6">
                  ${{
                    ((typeof orderStore.order.total_margin === 'number' ? orderStore.order.total_margin : 0) +
                     (typeof orderStore.order.total_price === 'number' ? orderStore.order.total_price : 0)).toFixed(2)
                  }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Botón guardar -->
        <div class="row">
          <div class="col-12" v-if="hasError">
            <div class="alert alert-danger d-flex align-items-center">
              <i class="bi bi-exclamation-triangle me-2"></i>
              {{ errorMessage }}
            </div>
          </div>
          <div class="col-12 d-flex justify-content-end gap-3" v-else>
            <button class="btn btn-default btn-sm" @click="updateOrder">
              <IconDeviceFloppy size="20" stroke="1.5" class="me-1"/>
              Actualizar
            </button>
            <a href="/trade/order/{{ orderStore.order.id }}" class="btn btn-default btn-sm">
              <IconBan size="20" stroke="1.5" class="text-danger"/>
              Cancelar
            </a>
            <a href="/trade/customer-orders/" class="btn btn-default btn-sm">
              <IconArrowLeft size="20" stroke="1.5" class="me-1"/>
              Lista de Pedidos
            </a>
          </div>
        </div>
      </div>
    </div>
    <GenericProductModal :product="selectedProduct"/>
  </div>
   </div>
      <div class="col-1"></div>
    </div>
</template>
