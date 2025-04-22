<script setup>
import {onMounted, ref, computed} from 'vue'

import {useBaseStore} from '@/stores/baseStore.js'
import { useSingleOrderStore } from '@/stores/trade/singleOrderStore.js'

import AutocompleteCustomer from '@/components/common/AutocompleteCustomer.vue'
import AutocompleteSupplier from '@/components/common/AutocompleteSupplier.vue'
import GenericProductModal from '@/components/common/GenericProductModal.vue'
import Loader from '@/components/Sotcks/Loader.vue'
import OrderLine from '@/components/trade/OrderLine.vue'
import { IconSettings, IconPlus } from '@tabler/icons-vue'

const baseStore = useBaseStore()
const stagesToLoad = ref(3)
const orderStore = useSingleOrderStore()
const selectedCustomer = ref(null)
const selectedSupplier = ref(null)
const selectedProduct = ref(null)
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
})


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
</script>
<template>
  <div class="container-fluid">
    <Loader v-if="isLoading" />
    <div class="bg-light py-4">
      <div class="bg-white shadow-lg border border-2 border-warning rounded-3 p-4 mx-auto">
        <!-- Encabezado -->
         <div class="row">
          <div class="col text-center fs-2 text-kosmo-secondary">
            ORDEN DE VENTA
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
                      <span style="width: 50%;">Variedad</span>
                      <span class="" style="width: 8%;">Largo CM</span>
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
                  <OrderLine @showProductModal="showProductModal"/>
                  <tr>
                    <td colspan="5" class="text-end">
                      <button class="btn btn-primary btn-sm">
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
            <div class="border border-secondary p-3 rounded">
              <div class="row">
                <div class="col-8 text-end"><strong>TOTAL HB:</strong></div>
                <div class="col-4 text-end">{{ orderStore.order.hb_total }}</div>
              </div>
              <div class="row">
                <div class="col-8 text-end"><strong>TOTAL QB:</strong></div>
                <div class="col-4 text-end">{{ orderStore.order.qb_total }}</div>
              </div>
              <div class="row">
                <div class="col-8 text-end"><strong>TOTAL FB:</strong></div>
                <div class="col-4 text-end">{{ orderStore.order.fb_total }}</div>
              </div>
              <div class="row">
                <div class="col-8 text-end"><strong>TOTAL TALLOS:</strong></div>
                <div class="col-4 text-end">{{ orderStore.order.total_stem_flower }}</div>
              </div>
            </div>
          </div>
          <div class="col-6">
            <div class="bg-light bg-gradient rounded shadow-sm p-3">
              <div class="row">
                <div class="col-7 text-end border-end text-success"><strong>Costo:</strong></div>
                <div class="col-5 text-end text-success">$1{{ orderStore.order.total_price }}</div>
              </div>
              <div class="row">
                <div class="col-7 text-end border-end text-success"><strong>Margen:</strong></div>
                <div class="col-5 text-end text-success">${{ orderStore.order.total_margin }}</div>
              </div>
              <div class="row">
                <div class="col-7 text-end border-end text-success"><strong>Total Factura:</strong></div>
                <div class="col-5 text-end text-success fs-5">${{ orderStore.order.total_margin + orderStore.order.total_price }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Botón guardar -->
        <div class="row">
          <div class="col-12 text-end">
            <button class="btn btn-default">
              <i class="bi bi-save me-2"></i>
              Guardar Factura
            </button>
          </div>
        </div>

        <!-- Mensajes de error -->
        <div class="row mt-3">
          <div class="col-12">
            <div class="alert alert-danger d-flex align-items-center">
              <i class="bi bi-exclamation-triangle me-2"></i>
              Error de ejemplo: Seleccione un cliente antes de guardar
            </div>
          </div>
        </div>

      </div>
    </div>
    <GenericProductModal :product="selectedProduct"/>
  </div>
</template>