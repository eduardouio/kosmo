<script setup>
import { computed, ref, watch } from 'vue';
import { useOrdersStore } from '@/stores/ordersStore.js';
import { appConfig } from '@/AppConfig';
import {
  IconTrash,
  IconSitemap,
  IconBan,
  IconLayersIntersect2,
  IconAlertTriangle,
  IconRefresh,
  IconSettingsDollar,
  IconPrinter,
  IconBox,
  IconFileDollar
} from '@tabler/icons-vue';

const orderStore = useOrdersStore();
const confirmDelete = ref(false);
const exceedLimit = ref(false);
const deleteMessage = ref('El item marcado será elimnado del pedido, click nuevamente para confirmar');
const exceedLimitMessage = ref();
const isModified = ref(false);

const calcAndGetProductQtyStemFlower = (product) => {
  const bunches = parseInt(product.total_bunches) || 0;
  const stemsPerBunch = parseInt(product.stems_bunch) || 25;
  return bunches * stemsPerBunch;
};

const calcTotalByProduct = (product) => {
  const totalBunches = parseInt(product.total_bunches) || 0;
  const stemsBunch = parseInt(product.stems_bunch) || 25;
  const cost = parseFloat(product.stem_cost_price) || 0;
  const margin = parseFloat(product.margin) || 0;

  return (totalBunches * stemsBunch * (cost + margin)).toFixed(2);
};

const delimitedNumber = (event, item) => {
  exceedLimit.value = false;
  let value = parseInt(event.target.value);
  let maxValue = orderStore.limitsNewOrder.filter(i => i.order_item_id === item.order_item_id).map(i => i.quantity);
  if (value > maxValue || value == 0) {
    item.quantity = maxValue;
    exceedLimitMessage.value = `La cantidad máxima permitida para este item es de ${maxValue}`;
    exceedLimit.value = true;
  }
};

const selectText = (event) => {
  event.target.select();
}

const deleteOrderItem = (item) => {
  if (item.confirm_delete) {
    orderStore.selectedOrder.order_details = orderStore.selectedOrder.order_details.filter(
      i => i.order_item_id !== item.order_item_id
    );
  } else {
    confirmDelete.value = true;
    item.confirm_delete = true;
  }
}

const careteOrderInvoice = async () => {
  const response = await orderStore.createInvoice();
  if (response) {
    orderStore.selectedOrder.is_invoiced = true;
    orderStore.selectedOrder.is_modified = false;
    location.reload();
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

const formatInteger = (event) => {
  let value = event.target.value;
  value = value.replace(',', '.');
  if (value === '' || value === '.' || value === ',' || isNaN(value) || value === ' ' || value === '0') {
    event.target.value = '0';
    return;
  }
  event.target.value = parseInt(value);
}

const handleBunchOrStemChange = (event, item, product, fieldName) => {
  if (fieldName === 'total_bunches') {
    const bunches = parseInt(product.total_bunches) || 0;
    const stemsValue = product.stems_bunch;
    if (bunches > 0 && (stemsValue === undefined || stemsValue === null || stemsValue === '' || parseInt(stemsValue) === 0)) {
      product.stems_bunch = 25;
    }
  }

  totalStemFlowerOrderItem(item);
};

const splitHB = (item) => {
  const newDetails = orderStore.selectedOrder.order_details.filter(i => i.order_item_id !== item.order_item_id);
  const stem_flower = item.box_items.map(i => i.qty_stem_flower);
  const id = item.order_item_id;

  if ((item.tot_stem_flower % 2) === 0) {
    newDetails.push({
      ...item,
      tot_stem_flower: item.tot_stem_flower / 2,
      box_model: 'QB',
    });
    newDetails.push({
      ...item,
      tot_stem_flower: item.tot_stem_flower / 2,
      box_model: 'QB',
    });
  } else {
    newDetails.push({
      ...item,
      tot_stem_flower: Math.floor(item.tot_stem_flower / 2),
      box_model: 'QB',
    });
    newDetails.push({
      ...item,
      tot_stem_flower: Math.ceil(item.tot_stem_flower / 2),
      box_model: 'QB',
    });
  }

  newDetails.forEach((itm) => {
    if (itm.order_item_id === id) {
      itm.box_items.forEach((i, index) => {
        i.qty_stem_flower = stem_flower[index] / 2;
      });
    }
  });

  orderStore.selectedOrder.order_details = newDetails.map(i => ({ ...i }));

};

const mergeQB = () => {
  const selectedQBs = orderStore.selectedOrder.order_details.filter(i => i.is_selected);
  const newOrderItem = { ...selectedQBs[0], box_model: 'HB', is_selected: false };

  let totalStems = 0
  selectedQBs.forEach(oitm => {
    totalStems += oitm.tot_stem_flower;
  });
  newOrderItem.tot_stem_flower = totalStems;
  newOrderItem.box_items = selectedQBs.reduce((acc, item) => {
    return acc.concat(item.box_items);
  }, []);

  const groupedBoxItems = Object.values(
    newOrderItem.box_items.reduce((acc, item) => {
      const key = `${item.product_name}-${item.product_variety}-${item.length}`;
      if (!acc[key]) {
        acc[key] = { ...item };
      } else {
        acc[key].qty_stem_flower += item.qty_stem_flower;
      }
      return acc;
    }, {})
  );

  orderStore.selectedOrder.order_details = orderStore.selectedOrder.order_details.filter(
    i => !i.is_selected
  ).map(i => ({ ...i }));

  orderStore.selectedOrder.order_details.push({
    ...newOrderItem,
    box_items: groupedBoxItems,
  });

};

const updateOrder = async (action) => {
  console.log('Actualizando pedido ' + action);
  switch (action) {
    case 'confirm':
      if (orderStore.selectedOrder.is_confirmed) {
        orderStore.selectedOrder.is_modified = false;
        orderStore.selectedOrder.order.status = 'CONFIRMADO';
        orderStore.updateOrder()
      } else {
        orderStore.selectedOrder.is_confirmed = true;
      }
      break;
    case 'update':
      if (orderStore.selectedOrder.is_modified) {
        const response = await orderStore.updateOrder()
        if (response) {
          orderStore.selectedOrder.is_modified = false;
          location.reload();
        }
      } else {
        orderStore.selectedOrder.is_modified = true;
      }
      break;
    case 'cancell':
      if (orderStore.selectedOrder.is_cancelled) {
        orderStore.selectedOrder.order.status = 'CANCELADO';
        const response = await orderStore.cancellOrder();
        if (response) {
          orderStore.selectedOrder.is_cancelled = true;
          orderStore.selectedOrder.is_modified = false;
          location.reload();
        }
      } else {
        orderStore.selectedOrder.is_cancelled = true;
      }
      break;
  }
}


const isTwoQBSelected = computed(() => {
  let qb = orderStore.selectedOrder.order_details.filter(i => i.box_model === 'QB' && i.is_selected);
  return qb.length === 2;
});


const totalStemFlowerOrderItem = (order_item) => {
  let total_stems = order_item.box_items.reduce((acc, item) => {
    const bunches = parseInt(item.total_bunches) || 0;
    const stemsPerBunch = parseInt(item.stems_bunch) || 25;
    const stems = bunches * stemsPerBunch;
    item.qty_stem_flower = stems;
    return acc + stems;
  }, 0);
  total_stems = total_stems * parseInt(order_item.quantity);
  order_item.tot_stem_flower = total_stems;
  return total_stems;
}

const totalMargin = computed(() => {
  if (orderStore.selectedOrder === null) return 0;
  let total = 0;
  orderStore.selectedOrder.order_details.forEach(order_detail => {
    total += order_detail.box_items.reduce((acc, item) => {
      return acc + parseFloat(item.margin * parseFloat(item.qty_stem_flower));
    }, 0) * order_detail.quantity;
  });
  return total.toFixed(2);
});

const totalCost = computed(() => {
  if (orderStore.selectedOrder === null) return 0;
  let total = 0;
  orderStore.selectedOrder.order_details.forEach(order_detail => {
    total += order_detail.box_items.reduce((acc, item) => {
      return acc + (item.stem_cost_price * parseFloat(item.qty_stem_flower));
    }, 0) * order_detail.quantity;
  });
  return total.toFixed(2);
});

const totalBoxesQB = computed(() => {
  let total = 0;
  orderStore.selectedOrder.order_details.forEach(item => {
    total += item.box_model === 'QB' ? parseInt(item.quantity) : 0;
  });
  return total;
});

const totalBoxesHB = computed(() => {
  let total = 0;
  orderStore.selectedOrder.order_details.forEach(item => {
    total += item.box_model === 'HB' ? parseInt(item.quantity) : 0;
  });
  return total;
});

const totalStems = computed(() => {
  let total = 0;
  orderStore.selectedOrder.order_details.forEach(item => {
    total += item.tot_stem_flower;
  });
  return total;
});

const orderHaveCeroItem = computed(() => {
  for (const order of orderStore.selectedOrder.order_details) {
    let ceroBoxesStem = order.box_items.filter(
      i => i.qty_stem_flower === 0
    );

    let ceroBoxesCost = order.box_items.filter(
      i => i.stem_cost_price === 0
    );

    if (ceroBoxesStem.length > 0 || ceroBoxesCost.length > 0) {
      exceedLimitMessage.value = 'No se permiten items con cantidad 0 o costo 0';
      exceedLimit.value = true;
      return true;
    }

    exceedLimitMessage.value = '';
    exceedLimit.value = false;
    return false;
  }

  exceedLimitMessage.value = '';
  exceedLimit.value = false;
  return false;
});

const getUrlReportCusOrder = (id) => {
  let urlReportOrder = appConfig.urlReportCustOrder.replace('{id_order}', id);
  return urlReportOrder;
};

const getUrlReportinvoice = (id) => {
  let urlInvoiceReport = appConfig.urlInvoiceReport.replace('{id_invoice}', id);
  return urlInvoiceReport;
};

watch(() => orderStore.selectedOrder,
  (newValue) => {
    isModified.value = true;
    if (newValue && newValue.order_details) {
      newValue.order_details.forEach(item_detail => {
        if (item_detail.box_items) {
          item_detail.box_items.forEach(product => {
            if (product.stems_bunch === undefined || product.stems_bunch === null) {
              product.stems_bunch = 25;
            }
          });
        }
        totalStemFlowerOrderItem(item_detail);
      });
    }
  },
  { deep: true, immediate: true }
);


</script>

<template>
  <div class="container-fluid p-2">
    <!-- Alert Messages -->
    <div class="row mb-3" v-if="exceedLimit || confirmDelete">
      <div class="col-12">
        <div class="alert alert-soft-warning d-flex align-items-center" role="alert">
          <IconAlertTriangle size="18" stroke="1.5" class="me-2" />
          <div>
            <span v-if="confirmDelete">{{ deleteMessage }}</span>
            <span v-if="exceedLimit">{{ exceedLimitMessage }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Customer Information Header -->
    <div class="row mb-3">
      <div class="col-12">
        <div class="card card-soft border-0">
          <div class="card-body bg-soft-primary p-reduced text-soft-primary">
            <div class="row align-items-center mb-2 pb-2">
              <div class="col-4">
                <h5 class="mb-0 fw-bold">
                  <i class="fas fa-building me-2"></i>
                  {{ orderStore.selectedOrder.order.partner.name }}
                </h5>
              </div>
              <div class="col-4 text-center">
                <span class="badge badge-soft-info text-center fs-6">PEDIDO DE CLIENTE</span>
              </div>
              <div class="col-4">
                <div class="d-flex justify-content-end align-items-end">
                  <div class="d-flex gap-1 flex-wrap">
                    <span class="badge badge-soft-secondary px-2 py-1 fs-6">
                      Pedido {{ orderStore.selectedOrder.order.serie }}-{{ orderStore.selectedOrder.order.consecutive ?
                        String(orderStore.selectedOrder.order.consecutive).padStart(6, '0') : 'N/A' }}
                    </span>
                    <span class="badge px-2 py-1 fs-6" :class="{
                      'badge-soft-success': orderStore.selectedOrder.order.status === 'CONFIRMADO',
                      'badge-soft-warning': orderStore.selectedOrder.order.status === 'PENDIENTE',
                      'bg-red-100 text-red-700 border-red-200': orderStore.selectedOrder.order.status === 'CANCELADO',
                      'badge-soft-primary': orderStore.selectedOrder.order.status === 'MODIFICADO'
                    }">
                      {{ orderStore.selectedOrder.order.status }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div class="row g-2">
              <div class="col-md-6">
                <div class="d-flex align-items-center mb-1">
                  <strong class="me-2">ID:</strong>
                  <span>{{ orderStore.selectedOrder.order.partner.business_tax_id }}</span>
                </div>
                <div class="d-flex align-items-start">
                  <strong class="me-2">Dirección:</strong>
                  <span>{{ orderStore.selectedOrder.order.partner.address }}, {{
                    orderStore.selectedOrder.order.partner.city }}, {{ orderStore.selectedOrder.order.partner.country
                    }}</span>
                </div>
              </div>

              <div class="col-md-6">
                <div class="d-flex align-items-center mb-1">
                  <strong class="me-2">Skype:</strong>
                  <span>{{ orderStore.selectedOrder.order.partner.skype || 'N/A' }}</span>
                </div>
                <div class="d-flex align-items-center">
                  <strong class="me-2">Consolida:</strong>
                  <span class="badge"
                    :class="orderStore.selectedOrder.order.partner.consolidate ? 'badge-soft-success' : 'badge-soft-secondary'">
                    {{ orderStore.selectedOrder.order.partner.consolidate ? 'Sí' : 'No' }}
                  </span>
                </div>
              </div>
            </div>

            <div class="row mt-2" v-if="orderStore.selectedOrder.order.partner.contact">
              <div class="col-12">
                <div class="d-flex flex-wrap align-items-center gap-2">
                  <strong>Contacto:</strong>
                  <span class="badge badge-soft-secondary">{{ orderStore.selectedOrder.order.partner.contact.name
                    }}</span>
                  <span class="badge badge-soft-secondary">{{ orderStore.selectedOrder.order.partner.contact.email
                    }}</span>
                  <span class="badge badge-soft-secondary">{{ orderStore.selectedOrder.order.partner.contact.phone
                    }}</span>
                  <span class="badge badge-soft-success">{{ orderStore.selectedOrder.order.partner.contact.contact_type
                    }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Status Message & Actions -->
    <div class="row mb-2">
      <div class="col-md-8">
        <div class="alert alert-soft-info mb-0" v-if="orderStore.selectedOrder.is_modified">
          <i class="fas fa-exclamation-triangle me-2"></i>
          Orden de Compra Modificada, si actualiza el pedido se actualizarán la o las ordenes de compra
        </div>
      </div>
      <div class="col-md-4 text-end">
        <button class="btn btn-outline-primary " v-if="isTwoQBSelected" @click="mergeQB">
          <IconLayersIntersect2 size="16" stroke="1.5" class="me-1" />
          Unificar a HB
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
              Detalle Orden de Compra
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
              <div v-for="(item, idx) in orderStore.selectedOrder.order_details" :key="item" class="order-row"
                :class="{ 'bg-gray-50': idx % 2 === 0 }">
                <div class="row g-0 align-items-center">
                  <!-- Quantity & Delete -->
                  <div class="col-1 border-end p-1">
                    <div class="d-flex align-items-center gap-1">
                      <button class="btn  btn-outline-danger border-0" @click="deleteOrderItem(item)"
                        :class="{ 'text-danger': item.confirm_delete }"
                        v-if="!orderStore.selectedOrder.is_confirmed && !orderStore.selectedOrder.is_invoiced">
                        <IconTrash size="14" stroke="1.5" />
                      </button>
                      <input type="number" step="1" class="form-control form-control-sm text-end input-soft"
                        v-model="item.quantity" @change="(event) => delimitedNumber(event, item)" @focus="selectText"
                        @keydown="event => handleKeydown(event, '.form-control-sm')"
                        :disabled="orderStore.selectedOrder.is_confirmed || orderStore.selectedOrder.is_invoiced" />
                    </div>
                  </div>

                  <!-- Model -->
                  <div class="col-1 border-end p-1 text-center">
                    <div class="d-flex align-items-center justify-content-center gap-1">
                      <span class="badge badge-soft-secondary">{{ item.box_model }}</span>
                      <div v-if="!orderStore.selectedOrder.is_invoiced" class="d-flex align-items-center gap-1">
                        <IconSitemap size="14" stroke="1.5" class="text-primary cursor-pointer" @click="splitHB(item)"
                          v-if="item.box_model === 'HB' && !orderStore.selectedOrder.is_invoiced" />
                        <input type="checkbox" class="form-check-input" v-model="item.is_selected"
                          v-if="item.box_model === 'QB' && !orderStore.selectedOrder.is_invoiced" />
                      </div>
                    </div>
                  </div>

                  <!-- Stems -->
                  <div class="col-1 border-end p-1 text-center">
                    <span class="fw-bold text-primary">{{ totalStemFlowerOrderItem(item) }}</span>
                  </div>

                  <!-- Supplier -->
                  <div class="col-2 border-end p-1">
                    <small class="text-muted">{{ item.partner.partner.name }}</small>
                  </div>

                  <!-- Products -->
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
                                 class="form-control form-control-sm text-end input-soft"
                                 v-model="product.total_bunches" 
                                 @focus="selectText"
                                 @keydown="event => handleKeydown(event, '.my-input-4')"
                                 @blur="event => handleBunchOrStemChange(event, item, product, 'total_bunches')"
                                 :class="{ 
                                   'input-error': !product.total_bunches || parseInt(product.total_bunches) <= 0,
                                   'border-danger': !product.total_bunches || parseInt(product.total_bunches) <= 0
                                 }"
                                 :disabled="orderStore.selectedOrder.is_confirmed || orderStore.selectedOrder.is_invoiced" />
                        </div>
                        <div class="col" style="flex: 0 0 13%;">
                          <input type="number" 
                                 step="1" 
                                 class="form-control form-control-sm text-end input-soft"
                                 v-model="product.stems_bunch" 
                                 @focus="selectText"
                                 @keydown="event => handleKeydown(event, '.my-input-5')"
                                 @blur="event => handleBunchOrStemChange(event, item, product, 'stems_bunch')"
                                 :class="{ 
                                   'input-error': !product.stems_bunch || parseInt(product.stems_bunch) <= 0,
                                   'border-danger': !product.stems_bunch || parseInt(product.stems_bunch) <= 0
                                 }"
                                 :disabled="orderStore.selectedOrder.is_confirmed || orderStore.selectedOrder.is_invoiced" />
                        </div>
                        <div class="col" style="flex: 0 0 13%;">
                          <input type="number" 
                                 step="0.01" 
                                 class="form-control form-control-sm text-end input-soft"
                                 v-model="product.stem_cost_price" 
                                 @focus="selectText"
                                 @keydown="event => handleKeydown(event, '.my-input-2')" 
                                 @blur="formatNumber"
                                 :class="{ 
                                   'input-error': !product.stem_cost_price || parseFloat(product.stem_cost_price) <= 0.00,
                                   'border-danger': !product.stem_cost_price || parseFloat(product.stem_cost_price) <= 0.00
                                 }"
                                 :disabled="orderStore.selectedOrder.is_confirmed || orderStore.selectedOrder.is_invoiced" />
                        </div>
                        <div class="col" style="flex: 0 0 13%;">
                          <input type="number" 
                                 step="0.01" 
                                 class="form-control form-control-sm text-end input-soft"
                                 v-model="product.margin" 
                                 @focus="selectText" 
                                 @keydown="event => handleKeydown(event, '.my-input-3')"
                                 @blur="formatNumber" 
                                 :class="{ 
                                   'input-error': !product.margin || parseFloat(product.margin) <= 0.00,
                                   'border-danger': !product.margin || parseFloat(product.margin) <= 0.00
                                 }"
                                 :disabled="orderStore.selectedOrder.is_confirmed || orderStore.selectedOrder.is_invoiced" />
                        </div>
                        <div class="col text-center" style="flex: 0 0 13%;">
                          <span class="badge badge-soft-success">
                            {{ (parseFloat(product.stem_cost_price) + parseFloat(product.margin)).toFixed(2) }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Total -->
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
                  <small class="text-muted fw-bold">Half Boxes (HB)</small>
                </div>
              </div>
              <div class="col-6">
                <div class="text-center">
                  <div class="h4 mb-0 text-info">{{ totalBoxesQB }}</div>
                  <small class="text-muted fw-bold">Quarter Boxes (QB)</small>
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
                  <div class="h5 mb-1 text-warning">${{ orderStore.formatNumber(totalCost) }}</div>
                  <small class="text-muted">Costo Total</small>
                </div>
              </div>
              <div class="col-md-4">
                <div class="p-2 bg-soft-secondary rounded text-center">
                  <div class="h5 mb-1 text-info">${{ orderStore.formatNumber(totalMargin) }}</div>
                  <small class="text-muted">Margen Total</small>
                </div>
              </div>
              <div class="col-md-4">
                <div class="p-2 bg-soft-success rounded text-center">
                  <div class="h5 mb-1 text-success">${{ orderStore.formatNumber(parseFloat(totalMargin) +
                    parseFloat(totalCost)) }}</div>
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
              <button type="button" class="btn btn-outline-danger " @click="updateOrder('cancell')"
                v-if="orderStore.selectedOrder.is_confirmed && !orderStore.selectedOrder.is_invoiced">
                <IconBan size="16" stroke="1.5" class="me-1" />
                <span v-if="orderStore.selectedOrder.is_cancelled">Confirmar Cancelación</span>
                <span v-else>Cancelar Pedido</span>
              </button>

              <button type="button" class="btn btn-primary " @click="updateOrder('update')"
                :disabled="orderHaveCeroItem"
                v-if="isModified && (!orderStore.selectedOrder.is_confirmed && !orderStore.selectedOrder.is_invoiced)">
                <IconRefresh size="16" stroke="1.5" class="me-1" />
                <span v-if="orderStore.selectedOrder.is_modified">Confirmar Actualización</span>
                <span v-else>Actualizar</span>
              </button>

              <button class="btn btn-outline-secondary "
                v-if="!orderStore.selectedOrder.is_confirmed && !orderStore.selectedOrder.is_invoiced">
                <a :href="getUrlReportCusOrder(orderStore.selectedOrder.order.id)" class="text-decoration-none">
                  <IconPrinter size="16" stroke="1.5" class="me-1" />
                  Imprimir Ord Venta
                </a>
              </button>

              <button class="btn btn-outline-secondary " v-if="orderStore.selectedOrder.is_invoiced">
                <a :href="getUrlReportinvoice(orderStore.selectedOrder.id_invoice)" class="text-decoration-none">
                  <IconPrinter size="16" stroke="1.5" class="me-1" />
                  Imprimir Factura
                </a>
              </button>

              <button class="btn btn-success "
                v-if="orderStore.selectedOrder.is_confirmed && !orderStore.selectedOrder.is_invoiced"
                @click="careteOrderInvoice">
                <IconSettingsDollar size="16" stroke="1.5" class="me-1" />
                Generar Factura
              </button>

              <a :href="appConfig.apiBaseUrl + '/trade/invoice/' + orderStore.selectedOrder.order.id_invoice"
                class="btn btn-info " v-if="orderStore.selectedOrder.is_invoiced">
                <IconFileDollar size="16" stroke="1.5" class="me-1" />
                Ver Factura
              </a>

              <a :href="appConfig.apiBaseUrl + '/trade/order/' + orderStore.selectedOrder.order.id"
                class="btn btn-outline-info ">
                <IconBox size="16" stroke="1.5" class="me-1" />
                Ficha de Pedido
              </a>
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

. {
  padding: 0.125rem 0.375rem;
  font-size: 0.75rem;
}

.input-error {
  border-color: #dc3545 !important;
  background-color: #f8d7da !important;
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