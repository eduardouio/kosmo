<script setup>
import { computed, ref, watch, onMounted } from 'vue'; // Added onMounted
import { useRouter } from 'vue-router';
import { useOrdersStore } from '@/stores/ordersStore.js';
import { useStockStore } from '@/stores/stockStore.js';
import { useBaseStore } from '@/stores/baseStore.js';
import AutocompleteCustomer from '@/components/Sotcks/AutocompleteCustomer.vue';
import { 
  IconTrash,
  IconCheckbox,
  IconSitemap,
  IconBan,
  IconLayersIntersect2
} from '@tabler/icons-vue';

const ordersStore = useOrdersStore();
const stockStore = useStockStore();
const baseStore = useBaseStore();
const router = useRouter();

onMounted(() => {
  if (ordersStore.newOrder.length > 0) {
    baseStore.updateGlobalAlertStatus(ordersStore);
  }
});
  

const calcTotalByProduct = (product) => {
  const totalBunches = parseInt(product.total_bunches) || 0;
  const stemsBunch = parseInt(product.stems_bunch) || 25;
  const cost = parseFloat(product.stem_cost_price) || 0;
  const margin = parseFloat(product.margin) || 0;
  
  return (totalBunches * stemsBunch * (cost + margin)).toFixed(2);
};

const cancelOrder = () => {
  ordersStore.newOrder = [];
  ordersStore.selectedCustomer = null;
  baseStore.stastagesLoaded = 0 ;
  router.push('/');
};  

const delimitedNumber = (event, item) => {
  let value = parseInt(event.target.value);
  const stockItemDetails = ordersStore.limitsNewOrder.find(
    i => i.stock_detail_id === item.stock_detail_id
  );
  const maxQty = stockItemDetails ? stockItemDetails.quantity : Infinity;
  
  const itemNameForAlert = item.box_items[0]?.product_name || 'este item';
  const quantityErrorMessageBase = `La cantidad para ${itemNameForAlert} debe estar entre 1 y ${maxQty === Infinity ? 'el máximo disponible' : maxQty}.`;

  if (value > maxQty || value <= 0) {
    item.quantity = (maxQty > 0 && maxQty !== Infinity) ? maxQty : 1;
    baseStore.setAlert(`${quantityErrorMessageBase} Se ajustó a ${item.quantity}.`, 'error');
  } else {
    // Si la cantidad es válida y la alerta actual era sobre la cantidad de ESTE artículo, la limpiamos
    if (baseStore.alertType === 'error' && baseStore.alertMessage.startsWith(quantityErrorMessageBase)) {
      baseStore.setAlert(baseStore.defaultInfoMessage, 'info'); // Limpiar temporalmente el error específico
      // El watch sobre newOrder en OrdersView activará updateGlobalAlertStatus
    }
  }
};

const selectText = (event) => {
    event.target.select();
}

const deleteOrderItem = (item) => {
  // Reset confirm_delete for other items
  ordersStore.newOrder.forEach(i => {
    if (i !== item && i.confirm_delete) {
      i.confirm_delete = false;
    }
  });

  if (item.confirm_delete) {
    const index = ordersStore.newOrder.findIndex(i => i === item);
    if (index !== -1) {
      ordersStore.newOrder.splice(index, 1); // This will trigger the watch for newOrder in OrdersView
    }
  } else {
    item.confirm_delete = true;
    baseStore.setAlert('El item marcado será eliminado del pedido, click nuevamente para confirmar.', 'warning');
  }
}

const createOrder = async() => {
  const newOrderId = await ordersStore.sendOrder(
    stockStore.stockDay
  );
  if (newOrderId) {
    baseStore.stagesLoaded = 0;
    router.push(`/order-detail/${newOrderId}/`);
  }
}

const handleKeydown = (event, cssClass) => {
    const inputs = document.querySelectorAll(cssClass);
    const currentIndex = Array.prototype.indexOf.call(inputs, event.target);
    if (event.key === 'Enter' && currentIndex < inputs.length - 1) {
        inputs[currentIndex + 1].focus();
    }
    if (event.key === 'Enter' && event.shiftKey && currentIndex > 0) {
        inputs[currentIndex - 1].focus();
    }
}

const formatNumber = (event) => {
  let value = event.target.value;
  value = value.replace(',', '.');
  if (value === '' || value === '.' || value === ',' || isNaN(value) || value === ' ' || value === '0') {
    event.target.value = '0.00';
    return;
  }
  event.target.value = parseFloat(value).toFixed(2);
};

// computed Properties
const isTwoQBSelected = computed(() => {
  const selectedQBs = ordersStore.newOrder.filter(i => i.box_model === 'QB' && i.is_selected);
  
  if (selectedQBs.length === 0) return false;
  
  // Case 1: Exactly 2 QBs are selected
  if (selectedQBs.length === 2) {
    return true;
  }
  
  // Case 2: One QB is selected with quantity >= 2 and even
  if (selectedQBs.length === 1) {
    const item = selectedQBs[0];
    const quantity = item.quantity || 1;
    return quantity >= 2 && quantity % 2 === 0;
  }
  
  // Case 3: More than 2 QBs selected (can merge in pairs)
  if (selectedQBs.length > 2) {
    return true;
  }
  
  return false;
});

const totalOrder = computed(() => {
  let total = 0;
  ordersStore.newOrder.forEach(item => {
    let items = item.box_items.map(item => item)
    total += items.reduce((acc, itm) => {
      return acc + ((itm.stem_cost_price + parseFloat(itm.margin)) * parseFloat(itm.qty_stem_flower));
    }, 0) * item.quantity;
  });
  return total.toFixed(2);
});

const totalMargin = computed(() => {
  let total = 0;
  ordersStore.newOrder.forEach(item => {
    let items = item.box_items.map(item => item)
    total += items.reduce((acc, itm) => {
      return acc + parseFloat(itm.margin * parseFloat(itm.qty_stem_flower));
    }, 0) * item.quantity;
  });
  return total.toFixed(2);
});

const totalCost = computed(() => {
  let total = 0;
  ordersStore.newOrder.forEach(item => {
    let items = item.box_items.map(item => item)
    total += items.reduce((acc, itm) => {
      return acc + (itm.stem_cost_price * parseFloat(itm.qty_stem_flower));
    }, 0) * item.quantity;
  });
  return total.toFixed(2);
});

const totalBoxesQB = computed(() => {
  let total = 0;
  ordersStore.newOrder.forEach(item => {
    total += item.box_model === 'QB' ? parseInt(item.quantity) : 0;
  });
  return total;
});

const totalBoxesHB = computed(() => {
  let total = 0;
  ordersStore.newOrder.forEach(item => {
    total += item.box_model === 'HB' ? parseInt(item.quantity) : 0;
  });
  return total;
});

const totalBoxesEB = computed(() => {
  let total = 0;
  ordersStore.newOrder.forEach(item => {
    total += item.box_model === 'EB' ? parseInt(item.quantity) : 0;
  });
  return total;
});

const totalBoxesFB = computed(() => {
  let totalHB = 0;
  let totalQB = 0;
  let totalEB = 0;
  
  ordersStore.newOrder.forEach(item => {
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
  let total = 0;
  ordersStore.newOrder.forEach(item => {
    total += calculateTotalStemsForItem(item);
  });
  return total;
});

const orderHaveCeroItem = computed(() => {
  // The button should be disabled if there's any error or warning active.
  return baseStore.alertType === 'error' || baseStore.alertType === 'warning';
});

// Función para calcular qty_stem_flower basado en total_bunches y stems_bunch
const calculateQtyStemFlower = (product) => {
  const totalBunches = parseInt(product.total_bunches) || 0;
  
  // Usar un valor predeterminado de 25 si stems_bunch es 0 o nulo
  if (!product.stems_bunch || parseInt(product.stems_bunch) === 0) {
    product.stems_bunch = 25;
  }
  
  const stemsBunch = parseInt(product.stems_bunch);
  product.qty_stem_flower = totalBunches * stemsBunch;
};

// Agregar watch para todos los productos en box_items de cada pedido
watch(() => ordersStore.newOrder, (orders) => {
  if (!orders) return;
  
  orders.forEach(order => {
    order.box_items.forEach(product => {
      calculateQtyStemFlower(product);
    });
  });
}, { deep: true });

// Agregar un método computado para calcular el total de tallos por ítem
const calculateTotalStemsForItem = (item) => {
  // Suma todos los tallos de todos los productos en la caja
  const totalStems = item.box_items.reduce((sum, product) => {
    const bunches = parseInt(product.total_bunches) || 0;
    const stemsPerBunch = parseInt(product.stems_bunch) || 25; // Usa 25 como valor predeterminado
    return sum + (bunches * stemsPerBunch);
  }, 0);
  
  // Multiplica por la cantidad de cajas
  return totalStems * parseInt(item.quantity);
};

</script>

<template>
  <div class="container-fluid p-2">
    <!-- Customer Selection -->
    <div class="row mb-3">
      <div class="col-12">
        <div class="card card-soft border-0">
          <div class="card-body p-reduced">
            <AutocompleteCustomer />
          </div>
        </div>
      </div>
    </div>

    <!-- Customer Information Card -->
    <div class="row mb-3" v-if="ordersStore.selectedCustomer">
      <div class="col-12">
        <div class="card card-soft border-0">
          <div class="card-body bg-soft-primary p-reduced text-soft-primary">
            <div class="row align-items-center mb-2">
              <div class="col">
                <h5 class="mb-0 fw-bold">
                  <i class="fas fa-building me-2"></i>
                  {{ ordersStore.selectedCustomer.name }}
                </h5>
              </div>
            </div>
            
            <div class="row g-2">
              <div class="col-md-6">
                <div class="d-flex align-items-center mb-1">
                  <strong class="me-2">ID:</strong>
                  <span>{{ ordersStore.selectedCustomer.business_tax_id }}</span>
                </div>
                <div class="d-flex align-items-start">
                  <strong class="me-2">Dirección:</strong>
                  <span>{{ ordersStore.selectedCustomer.address }}, {{ ordersStore.selectedCustomer.city }}, {{ ordersStore.selectedCustomer.country }}</span>
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="d-flex align-items-center mb-1">
                  <strong class="me-2">Skype:</strong>
                  <span>{{ ordersStore.selectedCustomer.skype || 'N/A' }}</span>
                </div>
                <div class="d-flex align-items-center">
                  <strong class="me-2">Consolida:</strong>
                  <span class="badge" :class="ordersStore.selectedCustomer.consolidate ? 'badge-soft-success' : 'badge-soft-secondary'">
                    {{ ordersStore.selectedCustomer.consolidate ? 'Sí' : 'No' }}
                  </span>
                </div>
              </div>
            </div>

            <div class="row mt-2" v-if="ordersStore.selectedCustomer.contact">
              <div class="col-12">
                <div class="d-flex flex-wrap align-items-center gap-2">
                  <strong>Contacto:</strong>
                  <span class="badge badge-soft-secondary">{{ ordersStore.selectedCustomer.contact.name }}</span>
                  <span class="badge badge-soft-secondary">{{ ordersStore.selectedCustomer.contact.email }}</span>
                  <span class="badge badge-soft-secondary">{{ ordersStore.selectedCustomer.contact.phone }}</span>
                  <span class="badge badge-soft-success">{{ ordersStore.selectedCustomer.contact.contact_type }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="row mb-2" v-if="isTwoQBSelected">
      <div class="col-12 text-end">
        <button class="btn btn-outline-primary" @click="ordersStore.mergeQB">
          <IconLayersIntersect2 size="16" stroke="1.5" class="me-1" />
          {{ 
            ordersStore.newOrder.filter(i => i.box_model === 'QB' && i.is_selected).length === 1 
            ? 'Convertir QB a HB' 
            : 'Unificar QBs a HB' 
          }}
        </button>
      </div>
    </div>

    <!-- Order Items Table -->
    <div class="row">
      <div class="col-12">
        <div class="card card-soft border-0">
          <div class="card-header header-soft-blue py-reduced">
            <h6 class="mb-0">
              <i class="fas fa-shopping-cart me-2"></i>
              Productos del Pedido
            </h6>
          </div>
          
          <div class="card-body p-0">
            <!-- Table Header -->
            <div class="table-header bg-gray-700 text-white">
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
                <div class="col-2 border-end text-center py-2">
                  <small class="fw-bold">PROVEEDOR</small>
                </div>
                <div class="col-6 border-end bg-blue-600 py-2">
                  <div class="row g-0 text-center">
                    <div class="col" style="flex: 0 0 25%;">
                      <small class="fw-bold">VARIEDAD</small>
                    </div>
                    <div class="col border-start" style="flex: 0 0 10%;">
                      <small class="fw-bold">LARGO</small>
                    </div>
                    <div class="col border-start" style="flex: 0 0 13%;">
                      <small class="fw-bold">BUNCHES</small>
                    </div>
                    <div class="col border-start" style="flex: 0 0 13%;">
                      <small class="fw-bold">T/BUNCH</small>
                    </div>
                    <div class="col border-start" style="flex: 0 0 13%;">
                      <small class="fw-bold">COSTO</small>
                    </div>
                    <div class="col border-start" style="flex: 0 0 13%;">
                      <small class="fw-bold">MARGEN</small>
                    </div>
                    <div class="col border-start" style="flex: 0 0 13%;">
                      <small class="fw-bold">PVP</small>
                    </div>
                  </div>
                </div>
                <div class="col-1 bg-green-600 text-center py-2">
                  <small class="fw-bold">TOTAL</small>
                </div>
              </div>
            </div>

            <!-- Table Body -->
            <div class="table-body">
              <div v-for="(item, idx) in ordersStore.newOrder" :key="item.id" 
                   class="order-row" 
                   :class="{ 'bg-gray-50': idx % 2 === 0 }">
                <div class="row g-0 align-items-center">
                  <!-- Quantity Column -->
                  <div class="col-1 border-end p-1">
                    <div class="d-flex align-items-center gap-1">
                      <button class="btn btn-outline-danger border-0" 
                              @click="deleteOrderItem(item)"
                              :class="{ 'text-danger': item.confirm_delete }">
                        <IconTrash size="14" stroke="1.5" />
                      </button>
                      <input type="number" 
                             step="1" 
                             class="form-control form-control-sm text-end input-soft" 
                             v-model="item.quantity"
                             @change="(event) => delimitedNumber(event, item)" 
                             @focus="selectText"
                             @keydown="event => handleKeydown(event, '.form-control-sm')" />
                    </div>
                  </div>

                  <!-- Model Column -->
                  <div class="col-1 border-end p-1 text-center">
                    <div class="d-flex align-items-center justify-content-center gap-1">
                      <span class="badge badge-soft-secondary">{{ item.box_model }}</span>
                      <div class="d-flex align-items-center gap-1">
                        <IconSitemap size="14" stroke="1.5" 
                                   class="text-primary cursor-pointer" 
                                   @click="ordersStore.splitHB(item)" 
                                   v-if="item.box_model === 'HB'" />
                        <input type="checkbox" 
                               class="form-check-input" 
                               v-model="item.is_selected" 
                               v-if="item.box_model === 'QB'" />
                      </div>
                    </div>
                  </div>

                  <!-- Stems Column -->
                  <div class="col-1 border-end p-1 text-center">
                    <span class="fw-bold text-primary">{{ calculateTotalStemsForItem(item) }}</span>
                  </div>

                  <!-- Supplier Column -->
                  <div class="col-2 border-end p-1">
                    <small class="text-muted">{{ item.partner.name }}</small>
                  </div>

                  <!-- Products Column -->
                  <div class="col-6 border-end p-1">
                    <div v-for="product in item.box_items" :key="product.id" class="product-row mb-1">
                      <div class="row g-1 align-items-center">
                        <div class="col" style="flex: 0 0 25%;">
                          <small class="fw-medium">{{ product.product_name }} {{ product.product_variety }}</small>
                        </div>
                        <div class="col text-center" style="flex: 0 0 10%;">
                          <span class="badge badge-soft-info">{{ product.length }}</span>
                        </div>
                        <div class="col" style="flex: 0 0 13%;">
                          <input type="number" 
                                 step="1" 
                                 class="form-control form-control-sm text-end input-soft my-input-4"
                                 v-model="product.total_bunches" 
                                 @focus="selectText"
                                 @keydown="event => handleKeydown(event, '.my-input-4')" 
                                 @change="(event) => {formatInteger(event); calculateQtyStemFlower(product);}"
                                 :class="{ 
                                   'input-error': !product.total_bunches || parseInt(product.total_bunches) <= 0,
                                   'border-danger': !product.total_bunches || parseInt(product.total_bunches) <= 0
                                 }" />
                        </div>
                        <div class="col" style="flex: 0 0 13%;">
                          <input type="number" 
                                 step="1" 
                                 class="form-control form-control-sm text-end input-soft my-input-5"
                                 v-model="product.stems_bunch" 
                                 @focus="selectText"
                                 @keydown="event => handleKeydown(event, '.my-input-5')" 
                                 @change="(event) => {formatInteger(event); calculateQtyStemFlower(product);}"
                                 :class="{ 
                                   'input-error': !product.stems_bunch || parseInt(product.stems_bunch) <= 0,
                                   'border-danger': !product.stems_bunch || parseInt(product.stems_bunch) <= 0
                                 }" />
                        </div>
                        <div class="col" style="flex: 0 0 13%;">
                          <input type="number" 
                                 step="0.01" 
                                 class="form-control form-control-sm text-end input-soft my-input-2"
                                 v-model="product.stem_cost_price" 
                                 @focus="selectText"
                                 @keydown="event => handleKeydown(event, '.my-input-2')" 
                                 @change="formatNumber"
                                 :class="{ 
                                   'input-error': !product.stem_cost_price || parseFloat(product.stem_cost_price) <= 0.00,
                                   'border-danger': !product.stem_cost_price || parseFloat(product.stem_cost_price) <= 0.00
                                 }" />
                        </div>
                        <div class="col" style="flex: 0 0 13%;">
                          <input type="number" 
                                 step="0.01" 
                                 class="form-control form-control-sm text-end input-soft my-input-3"
                                 v-model="product.margin" 
                                 @focus="selectText" 
                                 @keydown="event => handleKeydown(event, '.my-input-3')"
                                 @change="formatNumber" 
                                 :class="{ 
                                   'input-error': !product.margin || parseFloat(product.margin) <= 0.00,
                                   'border-danger': !product.margin || parseFloat(product.margin) <= 0.00
                                 }" />
                        </div>
                        <div class="col text-center" style="flex: 0 0 13%;">
                          <span class="badge badge-soft-success">
                            {{ (parseFloat(product.stem_cost_price) + parseFloat(product.margin)).toFixed(2) }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Total Column -->
                  <div class="col-1 p-1">
                    <div v-for="product in item.box_items" :key="product.id" class="mb-1">
                      <span class="fw-bold text-success">
                        ${{ calcTotalByProduct(product) }}
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

    <!-- Summary Cards -->
    <div class="row mt-3">
      <!-- Summary Stats -->
      <div class="col-md-4">
        <div class="card card-soft border-0 h-100">
          <div class="card-header header-soft-secondary">
            <h6 class="mb-0">
              <i class="fas fa-chart-bar me-2"></i>
              Resumen de Cajas
            </h6>
          </div>
          <div class="card-body p-reduced">
            <div class="row g-2">
              <div class="col-6">
                <div class="text-center">
                  <div class="h4 mb-0 text-primary">{{ totalBoxesHB }}</div>
                  <small class="text-muted">Half Boxes</small>
                </div>
              </div>
              <div class="col-6">
                <div class="text-center">
                  <div class="h4 mb-0 text-info">{{ totalBoxesQB }}</div>
                  <small class="text-muted">Quarter Boxes</small>
                </div>
              </div>
              <div class="col-6">
                <div class="text-center">
                  <div class="h4 mb-0 text-warning">{{ totalBoxesEB }}</div>
                  <small class="text-muted">Eighth Boxes</small>
                </div>
              </div>
              <div class="col-6">
                <div class="text-center">
                  <div class="h4 mb-0 text-success">{{ totalBoxesFB }}</div>
                  <small class="text-muted">Full Boxes</small>
                </div>
              </div>
              <div class="col-12">
                <div class="text-center pt-2 border-top">
                  <div class="h4 mb-0 text-success">{{ totalStems }}</div>
                  <small class="text-muted">Total Tallos</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Financial Summary -->
      <div class="col-md-8">
        <div class="card card-soft border-0 h-100">
          <div class="card-header header-soft-teal">
            <h6 class="mb-0">
              <i class="fas fa-dollar-sign me-2"></i>
              Resumen Financiero
            </h6>
          </div>
          <div class="card-body p-reduced">
            <div class="row g-2">
              <div class="col-md-4">
                <div class="p-2 bg-soft-secondary rounded text-center">
                  <div class="h5 mb-1 text-warning">${{ totalCost }}</div>
                  <small class="text-muted">Costo Total</small>
                </div>
              </div>
              <div class="col-md-4">
                <div class="p-2 bg-soft-secondary rounded text-center">
                  <div class="h5 mb-1 text-info">${{ totalMargin }}</div>
                  <small class="text-muted">Margen Total</small>
                </div>
              </div>
              <div class="col-md-4">
                <div class="p-2 bg-soft-success rounded text-center">
                  <div class="h5 mb-1 text-success">${{ totalOrder }}</div>
                  <small>Total Pedido</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="row mt-3">
      <div class="col-12">
        <div class="card card-soft border-0">
          <div class="card-body p-reduced">
            <div class="d-flex justify-content-end gap-2">
              <button type="button" 
                      class="btn btn-outline-danger" 
                      @click="cancelOrder">
                <IconBan size="16" stroke="1.5" class="me-1" />
                Cancelar Pedido
              </button>
              <button type="button" 
                      class="btn btn-success" 
                      @click="createOrder" 
                      :disabled="orderHaveCeroItem">
                <IconCheckbox size="16" stroke="1.5" class="me-1" />
                Confirmar Pedido
              </button>
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

.cursor-pointer {
  cursor: pointer;
}

.card {
  border-radius: 6px;
}

.card-header {
  border-radius: 6px 6px 0 0 !important;
}

.badge {
  font-size: 0.7rem;
  padding: 0.25rem 0.5rem;
}

input[type="checkbox"] {
  width: 14px;
  height: 14px;
}

.input-error {
  background-color: #fff3f3;
  border-color: #f5c6cb;
}

/* Mantener las clases my-input para la funcionalidad de navegación */
.my-input,
.my-input-2,
.my-input-3,
.my-input-4,
.my-input-5 {
  border: 1px solid #ccc;
  border-radius: 2px;
  text-align: right;
}

@media (max-width: 768px) {
  .container-fluid {
    padding: 0.75rem;
  }
  
  .card-body {
    padding: 0.75rem;
  }
}
</style>