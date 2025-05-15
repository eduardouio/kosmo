<script setup>
import {onMounted, ref, computed, watch, onUnmounted } from 'vue' 
import {useBaseStore} from '@/stores/baseStore.js'
import { useSingleOrderStore } from '@/stores/trade/singleOrderStore.js'

import AutocompleteCustomer from '@/components/common/AutocompleteCustomer.vue'
import AutocompleteSupplier from '@/components/common/AutocompleteSupplier.vue'
import GenericProductModal from '@/components/common/GenericProductModal.vue'
import Loader from '@/components/Sotcks/Loader.vue'
import OrderLine from '@/components/trade/OrderLine.vue'
import { IconSettings, IconPlus, IconDeviceFloppy } from '@tabler/icons-vue'
import { appConfig } from '@/AppConfig'

const baseStore = useBaseStore()
const stagesToLoad = ref(3)
const orderStore = useSingleOrderStore()
const selectedCustomer = ref(null)
const selectedSupplier = ref(null)
const selectedProduct = ref(null)
const errorMessage = ref('')
const hasError = ref(false)
orderStore.order.date = baseStore.formatDate(new Date())

// computed
const isLoading = computed(() => {
  return baseStore.stagesLoaded != stagesToLoad.value
})

// mouted
onMounted(() => {
  baseStore.loadSuppliers()
  baseStore.loadProducts()
  baseStore.loadCustomers(true)
  validateData()
  // Calcular totales iniciales después de cargar los datos
  setTimeout(calculateOrderTotals, 500)
})

onUnmounted(() => {clearInterval(validateInterval)});

function showProductModal($event) {
  console.log('Activamos el modal del ---', $event)
  selectedProduct.value = $event
}

function onSelectCustomer(customer) {
  selectedCustomer.value = customer
  baseStore.selectedCustomer = customer
}

function onSelectSupplier(supplier) {
  selectedSupplier.value = supplier
  baseStore.selectedSupplier = supplier
}

// Calcular totales del documento - versión mejorada
function calculateOrderTotals() {
  let hb_total = 0
  let qb_total = 0
  let fb_total = 0
  let total_stem_flower = 0
  let total_price = 0
  let total_margin = 0

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

        total_stem_flower += qtyStems;
        total_price += costPrice * qtyStems;
        total_margin += profitMargin * qtyStems;
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
    total_margin: parseFloat(total_margin.toFixed(2))
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

// Mejorar la función updateOrderLineTotal para evitar recursión
function updateOrderLineTotal(idx, tempLine) {
  if (idx >= 0 && idx < orderStore.orderLines.length) {
    // Crear un nuevo objeto para asegurar la reactividad
    const updatedLine = {
      ...orderStore.orderLines[idx], // Mantener propiedades existentes
      quantity: tempLine.quantity,
      box_model: tempLine.box_model,
      // Asegurar una copia profunda de los items para la reactividad
      order_box_items: JSON.parse(JSON.stringify(tempLine.order_box_items))
    };

    // Actualizar el store directamente con el objeto nuevo
    // Usar Vue.set o similar si splice no es reactivo, pero en Pinia/Vue 3 debería serlo.
    orderStore.orderLines.splice(idx, 1, updatedLine);

    // Llamar directamente a calculateOrderTotals después de la actualización
    // Usar nextTick para asegurar que el DOM se actualice antes de calcular si fuera necesario,
    // pero aquí calculamos sobre los datos del store, así que puede ser inmediato o con pequeño delay.
    setTimeout(calculateOrderTotals, 10); // Pequeño delay por si acaso
  } else {
    console.error("Índice inválido para updateOrderLineTotal:", idx);
  }
}

function validateData(){
  // validamos datos sminimos de orden de venta
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
  return true;
}

async function saveOrder() {
  const result = await orderStore.saveOrder(
    baseStore.selectedCustomer, 
    baseStore.selectedSupplier
  )
  
  if (result.success) {
    window.location.href =  `${appConfig.apiBaseUrlTest}/trade/order/61/`
  } else {
    alert(result.message)
  }
}

// Inicializar un validador recurrente para verificar datos
const validateInterval = setInterval(validateData, 2000);

</script>
<template>
  <div class="container-fluid">
    <Loader :show="isLoading" />
    <div v-if="!isLoading" class="bg-light py-4">
      <div class="bg-white shadow-lg border border-2 border-warning rounded-3 p-4 mx-auto">
        <!-- Encabezado -->
         <div class="row">
          <div class="col text-center fs-2 text-kosmo-secondary">
            PROMESA DE VENTA
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
                <span class="text-danger fs-4">{{ orderStore.order.serie }}-{{ orderStore.order.consecutive }}</span>
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
                <AutocompleteCustomer @select="onSelectCustomer"/>
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
                <p class="small mb-1 text-muted">Seleccione un cliente para ver la información de contacto.</p>
              </div>
            </div>
          </div>
          <div class="col-6">
            <div class="border border-2 border-warning p-3 rounded h-100">
              <h6 class="fw-bold mb-3">Información del Proveedor</h6>
              <div class="mb-3">
                <AutocompleteSupplier @select="onSelectSupplier"/>
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
              <table class="table table-bordered table-sm">
                <thead class="bg-warning bg-opacity-25">
                  <tr class="text-center small">
                    <th class="">CANT</th>
                    <th class="">MODELO</th>
                    <th class="d-flex gap-1">
                      <span style="width: 40%;">Variedad</span>
                      <span class="" style="width: 8%;">Largo CM</span>
                      <span class="" style="width: 8%;">T/B</span>
                      <span class="" style="width: 8%;">Bunches</span>
                      <span class="" style="width: 8%;">Tallos</span>
                      <span class="" style="width: 10%;">Costo</span>
                      <span class="" style="width: 10%;">Margen</span>
                      <span class="" style="width: 10%;">Total U</span>
                    </th>
                    <th>TOTAL</th>
                    <th><IconSettings size="15" stroke="1.5"/> </th>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="(line, idx) in orderStore.orderLines" :key="idx">
                    <OrderLine
                      v-model:quantity="line.quantity"
                      v-model:box_model="line.box_model"
                      v-model:boxItems="line.order_box_items"
                      :line_total="orderStore.calculateOrderLineTotal(line)"
                      @showProductModal="showProductModal"
                      @remove="removeOrderLine(idx)"
                      @updateLineTotal="tempLine => updateOrderLineTotal(idx, tempLine)"
                    />
                  </template>
                  <tr>
                    <td colspan="5" class="text-end">
                      <button class="btn btn-primary btn-sm" @click="addOrderLine">
                        <IconPlus size="15" stroke="1.5" class="text-white"/>
                        Agregar
                      </button>
                    </td>
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
                <div class="col-8 text-end border-end fs-5 fw-bold">TOTAL HB:</div>
                <div class="col-4 text-end fs-5 fw-bold">{{ orderStore.order.hb_total }}</div>
              </div>
              <div class="row">
                <div class="col-8 text-end border-end fs-5 fw-bold">TOTAL QB:</div>
                <div class="col-4 text-end fs-5 fw-bold">{{ orderStore.order.qb_total }}</div>
              </div>
              <div class="row">
                <div class="col-8 text-end border-end fs-5 fw-bold">TOTAL FB:</div>
                <div class="col-4 text-end fs-5 fw-bold">{{ orderStore.order.fb_total }}</div>
              </div>
              <div class="row">
                <div class="col-8 text-end border-end fs-5 fw-bold">TOTAL TALLOS:</div>
                <div class="col-4 text-end fs-5 fw-bold">{{ orderStore.order.total_stem_flower }}</div>
              </div>
              <div class="row">
                <div class="col-8 text-end border-end fs-5 fw-bold">TOTAL BUNCHES:</div>
                <div class="col-4 text-end fs-5 fw-bold">{{ orderStore.order.total_bunches }}</div>
              </div>
            </div>
          </div>
          <div class="col-6">
            <div class="bg-light bg-gradient rounded shadow-sm p-3 border-gray-500">
              <div class="row mt-4">
                <div class="col-7 text-end border-end text-success fs-5"><strong>Costo:</strong></div>
                <div class="col-5 text-end text-success fs-5">
                  ${{ typeof orderStore.order.total_price === 'number' ? orderStore.order.total_price.toFixed(2) : '0.00' }}
                </div>
              </div>
              <div class="row">
                <div class="col-7 text-end border-end text-success fs-5"><strong>Margen:</strong></div>
                <div class="col-5 text-end text-success fs-5">
                  ${{ typeof orderStore.order.total_margin === 'number' ? orderStore.order.total_margin.toFixed(2) : '0.00' }}
                </div>
              </div>
              <div class="row mb-1">
                <div class="col-7 text-end border-end text-success fs-5"><strong>Total Factura:</strong></div>
                <div class="col-5 text-end text-success fs-5">
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
          <div class="col-12"  v-if="hasError">
            <div class="alert alert-danger d-flex align-items-center">
              <i class="bi bi-exclamation-triangle me-2"></i>
              {{ errorMessage}}
            </div>
          </div>
          <div class="col-12 text-end" v-else>
            <button class="btn btn-default" @click="saveOrder">
              <IconDeviceFloppy size="20" stroke="1.5" class="text-primary"/> 
              Guardar Promesa
            </button>
          </div>
        </div>
      </div>
    </div>
    <GenericProductModal :product="selectedProduct"/>
  </div>
</template>