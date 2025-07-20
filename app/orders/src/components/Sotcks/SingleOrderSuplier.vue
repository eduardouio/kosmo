<script setup>
import { computed, ref, watch } from 'vue';
import { usePurchaseStore } from '@/stores/purcharsesStore.js';
import { appConfig } from '@/AppConfig';
import {
  IconCheckbox,
  IconCheck,
  IconPrinter,
  IconFileDollar,
} from '@tabler/icons-vue';

const purchaseStore = usePurchaseStore();

const calcAndGetProductQtyStemFlower = (product) => {
  // Convertimos a números y multiplicamos
  const qty = parseFloat(product.qty_stem_flower) || 0;
  const cost = parseFloat(product.stem_cost_price) || 0;
  // Redondeamos a 2 decimales para evitar problemas de precisión de punto flotante
  return parseFloat((qty * cost).toFixed(2));
};

const calcTotalStemFlower = (item) => {
  let totalStemsInItem = 0;
  if (item.box_items) {
    item.box_items.forEach(product => {
      totalStemsInItem += product.qty_stem_flower * product.stems_bunch;
    });
  }
  const total = totalStemsInItem * (parseInt(item.quantity) || 0);
  return total;
};

const calcLineStemFlower = (item) => {
  let totalStemsInItem = 0;
  if (item.box_items) {
    item.box_items.forEach(product => {
      totalStemsInItem += product.stems_bunch * product.total_bunches;
    });
  }
  const total = totalStemsInItem * (parseInt(item.quantity) || 0);
  item.tot_stem_flower = total;
  return total;
}

// Función para confirmar orden
const updateOrder = async (action) => {
  switch (action) {
    case 'confirm':
      if (purchaseStore.selectedPurchase.is_confirmed) {
        const response = await purchaseStore.confirmOrder();
        if (response) {
          location.reload();
        }
      } else {
        purchaseStore.selectedPurchase.is_confirmed = true;
      }
      break;
  }
};

const getUrlReportSupOrder = (id) => {
  let urlReportSupOrder = appConfig.urlReportSupOrder.replace('{id_order}', id);
  return urlReportSupOrder;
};

// Propiedades computadas - solo lectura

const totalCost = computed(() => {
  if (!purchaseStore.selectedPurchase.order_details) return 0;
  let total = 0;
  purchaseStore.selectedPurchase.order_details.forEach((detail) => {
    total += detail.box_items.reduce((acc, bItem) => {
      return acc + parseFloat(bItem.stem_cost_price) * parseFloat(bItem.qty_stem_flower);
    }, 0) * parseFloat(detail.quantity);
  });
  return total.toFixed(2);
});

const totalBoxesQB = computed(() => {
  if (!purchaseStore.selectedPurchase.order_details) return 0;
  let total = 0;
  purchaseStore.selectedPurchase.order_details.forEach((item) => {
    total += item.box_model === 'QB' ? parseInt(item.quantity) : 0;
  });
  return total;
});

const totalBoxesHB = computed(() => {
  if (!purchaseStore.selectedPurchase.order_details) return 0;
  let total = 0;
  purchaseStore.selectedPurchase.order_details.forEach((item) => {
    total += item.box_model === 'HB' ? parseInt(item.quantity) : 0;
  });
  return total;
});

const totalBoxesEB = computed(() => {
  if (!purchaseStore.selectedPurchase.order_details) return 0;
  let total = 0;
  purchaseStore.selectedPurchase.order_details.forEach((item) => {
    total += item.box_model === 'EB' ? parseInt(item.quantity) : 0;
  });
  return total;
});

const totalBoxesFB = computed(() => {
  if (!purchaseStore.selectedPurchase.order_details) return 0;
  let totalHB = 0;
  let totalQB = 0;
  let totalEB = 0;
  
  purchaseStore.selectedPurchase.order_details.forEach((item) => {
    const quantity = parseInt(item.quantity) || 0;
    if (item.box_model === 'HB') totalHB += quantity;
    if (item.box_model === 'QB') totalQB += quantity;
    if (item.box_model === 'EB') totalEB += quantity;
  });
  
  // FB = HB/2 + QB/4 + EB/8
  const totalFB = (totalHB / 2) + (totalQB / 4) + (totalEB / 8);
  return parseFloat(totalFB.toFixed(2));
});

const totalStems = computed(() => {
  if (!purchaseStore.selectedPurchase.order_details) return 0;
  let total = 0;
  purchaseStore.selectedPurchase.order_details.forEach((item) => {
    total += calcLineStemFlower(item) || 0;
  });
  return total;
});

// watchers - solo para inicializar valores
watch(() => purchaseStore.selectedPurchase,
  (newValue) => {
    console.log('selectedPurchase', newValue);
    // Solo inicializar stems_bunch si es necesario, sin permitir edición
    if (newValue && newValue.order_details) {
      newValue.order_details.forEach(item_detail => {
        if (item_detail.box_items) {
          item_detail.box_items.forEach(product => {
            if (product.stems_bunch === undefined || product.stems_bunch === null) {
              product.stems_bunch = 25;
            }
          });
        }
      });
    }
  }, { deep: true, immediate: true }
);
</script>

<template>
  <div class="container-fluid p-2">
    <div class="row pt-1">
      <div class="col">
        <div class="container-fluid" v-if="purchaseStore.selectedPurchase.order">
          <!-- Supplier Information Header -->
          <div class="row mb-3">
            <div class="col-12">
              <div class="card card-soft border-0">
                <div class="card-body bg-soft-orange p-reduced text-orange-800">
                  <div class="row align-items-center mb-2">
                    <div class="col-md-4">
                      <h5 class="mb-0 fw-bold">
                        <i class="fas fa-industry me-2"></i>
                        {{ purchaseStore.selectedPurchase.order.partner.name }}
                      </h5>
                    </div>
                    <div class="col-md-4 text-center">
                      <h6 class="mb-0">
                        <i class="fas fa-shopping-cart me-2"></i>
                        <span class="badge badge-soft-warning text-center fs-6">ORDEN DE COMPRA</span>
                      </h6>
                    </div>
                    <div class="col-md-4 text-end">
                      <div class="d-flex justify-content-end gap-1 flex-wrap">
                        <span class="badge badge-soft-secondary px-2 py-1 fs-6">
                          Pedido {{ purchaseStore.selectedPurchase.order.serie }}-{{ String(purchaseStore.selectedPurchase.order.consecutive).padStart(6, '0') }}
                        </span>
                        <span class="badge px-2 py-1 fs-6" 
                              :class="{
                                'badge-soft-success': purchaseStore.selectedPurchase.order.status === 'CONFIRMADO',
                                'badge-soft-warning': purchaseStore.selectedPurchase.order.status === 'PENDIENTE',
                                'bg-red-100 text-red-700 border-red-200': purchaseStore.selectedPurchase.order.status === 'CANCELADO',
                                'badge-soft-primary': purchaseStore.selectedPurchase.order.status === 'MODIFICADO',
                                'badge-soft-success': purchaseStore.selectedPurchase.order.status === 'FACTURADO'
                              }">
                          {{ purchaseStore.selectedPurchase.order.status }}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Supplier Details -->
                  <div class="row g-2">
                    <div class="col-md-6">
                      <div class="d-flex align-items-center mb-1">
                        <i class="fas fa-id-card me-2"></i>
                        <strong class="me-2">ID:</strong>
                        <span>{{ purchaseStore.selectedPurchase.order.partner.business_tax_id }}</span>
                      </div>
                      <div class="d-flex align-items-start">
                        <i class="fas fa-map-marker-alt me-2 mt-1"></i>
                        <div>
                          <strong class="me-2">Dirección:</strong>
                          <span>{{ purchaseStore.selectedPurchase.order.partner.address }}, {{ purchaseStore.selectedPurchase.order.partner.city }}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div class="col-md-6">
                      <div class="d-flex align-items-center mb-1">
                        <i class="fab fa-skype me-2"></i>
                        <strong class="me-2">Skype:</strong>
                        <span>{{ purchaseStore.selectedPurchase.order.partner.skype || 'N/A' }}</span>
                      </div>
                      <div class="d-flex align-items-center">
                        <i class="fas fa-shipping-fast me-2"></i>
                        <strong class="me-2">Consolida:</strong>
                        <span class="badge" :class="purchaseStore.selectedPurchase.order.partner.consolidate ? 'badge-soft-success' : 'badge-soft-secondary'">
                          {{ purchaseStore.selectedPurchase.order.partner.consolidate ? 'Sí' : 'No' }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Contact Information -->
                  <div class="row mt-2" v-if="purchaseStore.selectedPurchase.order.partner.contact">
                    <div class="col-12">
                      <div class="d-flex flex-wrap align-items-center gap-1">
                        <i class="fas fa-address-book me-2"></i>
                        <strong>Contacto:</strong>
                        <span class="badge badge-soft-secondary">{{ purchaseStore.selectedPurchase.order.partner.contact.name }}</span>
                        <span class="badge badge-soft-secondary">{{ purchaseStore.selectedPurchase.order.partner.contact.email }}</span>
                        <span class="badge badge-soft-secondary">{{ purchaseStore.selectedPurchase.order.partner.contact.phone }}</span>
                        <span class="badge badge-soft-success">{{ purchaseStore.selectedPurchase.order.partner.contact.contact_type }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Order Items Table -->
          <div class="row">
            <div class="col-12">
              <div class="card card-soft border-0">
                <div class="card-header header-soft-orange py-reduced">
                  <h6 class="mb-0">
                    <i class="fas fa-list-alt me-2"></i>
                    Detalles de la Orden de Compra
                  </h6>
                </div>
                
                <div class="card-body p-0">
                  <!-- Table Header -->
                  <div class="table-header bg-gray-700 text-white sticky-top">
                    <div class="row g-0">
                      <div class="col-1 border-end text-center py-2">
                        <small class="fw-bold">CANT</small>
                      </div>
                      <div class="col-1 border-end text-center py-2">
                        <small class="fw-bold">MODELO</small>
                      </div>
                      <div class="col-1 border-end text-center py-2">
                        <small class="fw-bold">TALLOS</small>
                      </div>
                      <div class="col-8 border-end bg-blue-600 py-2">
                        <div class="row g-0 text-center">
                          <div class="col" style="flex: 0 0 28%;">
                            <small class="fw-bold">VARIEDAD</small>
                          </div>
                          <div class="col border-start" style="flex: 0 0 18%;">
                            <small class="fw-bold">LARGO</small>
                          </div>
                          <div class="col border-start" style="flex: 0 0 18%;">
                            <small class="fw-bold">BUNCHES</small>
                          </div>
                          <div class="col border-start" style="flex: 0 0 18%;">
                            <small class="fw-bold">T/BUNCH</small>
                          </div>
                          <div class="col border-start" style="flex: 0 0 18%;">
                            <small class="fw-bold">COSTO</small>
                          </div>


                        </div>
                      </div>
                      <div class="col-1 bg-green-600 text-center py-2">
                        <small class="fw-bold">T COMPRA</small>
                      </div>
                    </div>
                  </div>

                  <!-- Table Body -->
                  <div class="table-body">
                    <div v-for="(item, idx) in purchaseStore.selectedPurchase.order_details" :key="item.order_item_id"
                         class="order-row"
                         :class="{ 'bg-gray-50': idx % 2 === 0 }">
                      <div class="row g-0 align-items-center">
                        <!-- Quantity -->
                        <div class="col-1 border-end p-1">
                          <div class="d-flex align-items-center justify-content-center">
                            <span class="fw-medium">{{ item.quantity }}</span>
                          </div>
                        </div>

                        <!-- Model -->
                        <div class="col-1 border-end p-1 text-center">
                          <span class="badge badge-soft-secondary">{{ item.box_model }}</span>
                        </div>

                        <!-- Stems -->
                        <div class="col-1 border-end p-1 text-center">
                          <span class="fw-bold text-primary">{{ calcLineStemFlower(item) }}</span>
                        </div>

                        <!-- Products -->
                        <div class="col-8 border-end p-1">
                          <div v-for="product in item.box_items" :key="product.id" class="product-row mb-1">
                            <div class="row g-1 align-items-center">
                              <div class="col" style="flex: 0 0 28%;">
                                <small class="fw-medium">{{ product.product_name }} {{ product.product_variety }}</small>
                              </div>
                              <div class="col text-center" style="flex: 0 0 18%;">
                                <span class="badge badge-soft-info">{{ product.length }}</span>
                              </div>
                              <div class="col text-center" style="flex: 0 0 18%;">
                                <span class="fw-medium">{{ product.total_bunches }}</span>
                              </div>
                              <div class="col text-center" style="flex: 0 0 18%;">
                                <span class="fw-medium">{{ product.stems_bunch }}</span>
                              </div>
                              <div class="col text-center" style="flex: 0 0 18%;">
                                <span class="fw-medium">${{ parseFloat(product.stem_cost_price).toFixed(2) }}</span>
                              </div>


                            </div>
                          </div>
                        </div>

                        <!-- Total Purchase -->
                        <div class="col-1 p-1">
                          <div v-for="product in item.box_items" :key="product.id" class="mb-1 text-center">
                            <span class="fw-bold text-warning">

                              ${{ purchaseStore.formatNumber(calcAndGetProductQtyStemFlower(product) * item.quantity) }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Summary & Actions -->
          <div class="row mt-3">
            <!-- Summary Stats -->
            <div class="col-md-4">
              <div class="card card-soft border-0 h-100">
                <div class="card-header header-soft-orange">
                  <h6 class="mb-0">
                    <i class="fas fa-chart-bar me-2"></i>
                    Resumen
                  </h6>
                </div>
                <div class="card-body p-reduced">
                  <div class="row g-2 text-center">
                    <div class="col-6">
                      <div class="h5 mb-0 text-primary">{{ totalBoxesHB }}</div>
                      <small class="text-muted">HB's</small>
                    </div>
                    <div class="col-6">
                      <div class="h5 mb-0 text-info">{{ totalBoxesQB }}</div>
                      <small class="text-muted">QB's</small>
                    </div>
                    <div class="col-6">
                      <div class="h5 mb-0 text-warning">{{ totalBoxesEB }}</div>
                      <small class="text-muted">EB's</small>
                    </div>
                    <div class="col-6">
                      <div class="h5 mb-0 text-success">{{ totalBoxesFB }}</div>
                      <small class="text-muted">FB's</small>
                    </div>
                    <div class="col-12 pt-2 border-top">
                      <div class="h5 mb-0 text-success">{{ totalStems }}</div>
                      <small class="text-muted">Tallos</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Financial Summary -->
            <div class="col-md-8">
              <div class="card card-soft border-0 h-100">
                <div class="card-header header-soft-orange">
                  <h6 class="mb-0">
                    <i class="fas fa-dollar-sign me-2"></i>
                    Resumen Financiero
                  </h6>
                </div>
                <div class="card-body p-reduced">
                  <div class="row g-2">
                    <div class="col-md-6">
                      <div class="p-2 bg-soft-secondary rounded text-center">
                        <div class="h6 mb-1 text-warning">${{ purchaseStore.formatNumber(totalCost) }}</div>
                        <small class="text-muted">Costo</small>
                      </div>
                    </div>

                    <div class="col-md-6">
                      <div class="p-2 bg-soft-success rounded text-center">
                        <div class="h6 mb-1 text-success">${{ purchaseStore.formatNumber(totalCost) }}</div>
                        <small>Total Compra</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons - Solo Confirmar y Reportes -->
          <div class="row mt-3">
            <div class="col-12">
              <div class="card card-soft border-0">
                <div class="card-body p-reduced">
                  <div class="d-flex justify-content-end gap-2 flex-wrap">
                    <button class="btn btn-default btn-sm" @click="updateOrder('confirm')">
                      <IconCheck size="16" stroke="1.5" class="me-1" v-if="!purchaseStore.selectedPurchase.is_confirmed" />
                      <IconCheckbox size="16" stroke="1.5" class="me-1" v-if="purchaseStore.selectedPurchase.is_confirmed" />
                      <span v-if="!purchaseStore.selectedPurchase.is_confirmed">Confirmar OC</span>
                      <span v-if="purchaseStore.selectedPurchase.is_confirmed">OC Confirmada</span>
                    </button>
                    
                    <button class="btn btn-default btn-sm">
                      <a :href="getUrlReportSupOrder(purchaseStore.selectedPurchase.order.id)" class="text-decoration-none">
                        <IconPrinter size="16" stroke="1.5" class="me-1" />
                        Orden de Compra
                      </a>
                    </button>
                    
                    <button class="btn btn-default btn-sm" 
                            v-if="purchaseStore.selectedPurchase.order.status === 'FACTURADO'">
                      <a :href="getUrlReportinvoice(purchaseStore.selectedPurchase.id_invoice)" class="text-decoration-none">
                        <IconFileDollar size="16" stroke="1.5" class="me-1" />
                        Ver Factura
                      </a>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.table-header {
  position: sticky;
  top: 0;
  z-index: 10;
}

.order-row {
  transition: background-color 0.15s ease;
  border-bottom: 1px solid #f1f5f9;
}

.order-row:hover {
  background-color: #f8fafc !important;
}

.product-row {
  padding: 0.125rem 0;
}

.card {
  border-radius: 6px;
}

.card-header {
  border-radius: 6px 6px 0 0 !important;
}

.badge {
  font-size: 0.7rem;
}

@media (max-width: 768px) {
  .container-fluid {
    padding: 0.75rem;
  }
  
  .card-body {
    padding: 0.75rem;
  }
  
  .d-flex.gap-2 {
    gap: 0.375rem !important;
  }
}
</style>