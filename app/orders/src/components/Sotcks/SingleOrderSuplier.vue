<script setup>
import { computed, ref, watch } from 'vue';
import { usePurchaseStore } from '@/stores/purcharsesStore.js';
import { appConfig } from '@/AppConfig';
import SideBar from '@/components/Sotcks/SideBar.vue';
import {
  IconTrash,
  IconCheckbox,
  IconCheck,
  IconSitemap,
  IconBan,
  IconLayersIntersect2,
  IconAlertTriangle,
  IconRefresh,
  IconPrinter,
  IconFileDollar,
} from '@tabler/icons-vue';

const purchaseStore = usePurchaseStore();

const confirmDelete = ref(false);
const exceedLimit = ref(false);
const deleteMessage = ref(
  'El item marcado será eliminado del pedido, haga clic nuevamente para confirmar'
);
const exceedLimitMessage = ref('');
const isModified = ref(false);

// Métodos

const calcAndGetProductQtyStemFlower = (product) => {
  const bunches = parseInt(product.total_bunches) || 0;
  const stemsPerBunch = parseInt(product.stems_bunch) || 25; // Default 25 si no está definido o es 0
  return bunches * stemsPerBunch;
};

const calcTotalByItem = (item) => {
  let totalValue = 0;
  if (item.box_items) {
    totalValue = item.box_items.reduce((acc, boxItem) => {
      const qty_stem_flower = calcAndGetProductQtyStemFlower(boxItem);
      const cost_price = parseFloat(boxItem.stem_cost_price) || 0;
      const margin = parseFloat(boxItem.margin) || 0;
      return acc + (cost_price + margin) * qty_stem_flower;
    }, 0);
  }
  const total = totalValue * (parseInt(item.quantity) || 0);
  item.line_total = parseFloat(total.toFixed(2));
  return total.toFixed(2);
};

const calcTotalStemFlower = (item) => {
  let totalStemsInItem = 0;
  if (item.box_items) {
    item.box_items.forEach(product => {
      totalStemsInItem += calcAndGetProductQtyStemFlower(product);
    });
  }
  const total = totalStemsInItem * (parseInt(item.quantity) || 0);
  item.tot_stem_flower = total;
  return total;
};

const delimitedNumber = (event, item) => {
  exceedLimit.value = false;
  let value = parseInt(event.target.value);
  // Ajustar si en tu store tienes "purchaseStore.limitsNewOrder" con la misma lógica
  let maxValue = purchaseStore.limitsNewOrder
    ? purchaseStore.limitsNewOrder.filter((i) => i.order_item_id === item.order_item_id).map((i) => i.quantity)
    : [];

  if (maxValue.length > 0) {
    if (value > maxValue[0] || value === 0) {
      item.quantity = maxValue[0];
      exceedLimitMessage.value = `La cantidad máxima permitida para este item es de ${maxValue[0]}`;
      exceedLimit.value = true;
    }
  }
  
  // Recalcular totales cuando cambia la cantidad
  calcTotalStemFlower(item);
  calcTotalByItem(item);
};

const selectText = (event) => {
  event.target.select();
};

const deleteOrderItem = (item) => {
  if (item.confirm_delete) {
    // Eliminamos el item del array order_details de la orden seleccionada
    purchaseStore.selectedPurchase.order_details = purchaseStore.selectedPurchase.order_details.filter(
      (i) => i.order_item_id !== item.order_item_id
    );
  } else {
    confirmDelete.value = true;
    item.confirm_delete = true;
  }
};

const handleKeydown = (event, cssClass) => {
  const inputs = document.querySelectorAll(cssClass);
  const currentIndex = Array.prototype.indexOf.call(inputs, event.target);

  if (event.key === 'Enter' && !event.shiftKey && currentIndex < inputs.length - 1) {
    inputs[currentIndex + 1].focus();
  }
  if (event.key === 'Enter' && event.shiftKey && currentIndex > 0) {
    inputs[currentIndex - 1].focus();
  }
};

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
};

const handleBunchOrStemChange = (event, item, product, fieldName) => { // item es order_detail
  formatInteger(event); // Formatea el input actual (product[fieldName])

  if (fieldName === 'total_bunches') {
    const bunches = parseInt(product.total_bunches) || 0;
    const stemsValue = product.stems_bunch; // Puede ser string, number, null, undefined
    // Si bunches > 0 y stems_bunch es undefined, null, vacío o 0, autocompletar a 25.
    if (bunches > 0 && (stemsValue === undefined || stemsValue === null || stemsValue === '' || parseInt(stemsValue) === 0)) {
      product.stems_bunch = 25;
    }
  }
  // Si fieldName es 'stems_bunch', formatInteger ya lo manejó.
  // Si el usuario ingresa 0 explícitamente en stems_bunch, se mantendrá 0 (después de formatInteger).

  // Recalcular los totales del item.
  calcTotalStemFlower(item); // Actualiza item.tot_stem_flower
  calcTotalByItem(item);   // Actualiza item.line_total
};

// Métodos para dividir y unificar
const splitHB = (item) => {
  const newDetails = purchaseStore.selectedPurchase.order_details.filter(
    (i) => i.order_item_id !== item.order_item_id
  );
  const stem_flower = item.box_items.map((i) => i.qty_stem_flower);
  const id = item.order_item_id;

  if (item.tot_stem_flower % 2 === 0) {
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
      itm.box_items.forEach((bItem, index) => {
        bItem.qty_stem_flower = stem_flower[index] / 2;
      });
    }
  });

  purchaseStore.selectedPurchase.order_details = newDetails.map((i) => ({ ...i }));
};

const mergeQB = () => {
  const selectedQBs = purchaseStore.selectedPurchase.order_details.filter(
    (i) => i.box_model === 'QB' && i.is_selected
  );
  if (selectedQBs.length < 2) return;

  const newOrderItem = {
    ...selectedQBs[0],
    box_model: 'HB',
    is_selected: false,
  };

  let totalStems = 0;
  selectedQBs.forEach((oitm) => {
    totalStems += oitm.tot_stem_flower;
  });
  newOrderItem.tot_stem_flower = totalStems;
  newOrderItem.box_items = selectedQBs.reduce((acc, item) => {
    return acc.concat(item.box_items);
  }, []);

  const groupedBoxItems = Object.values(
    newOrderItem.box_items.reduce((acc, bItem) => {
      const key = `${bItem.product_name}-${bItem.product_variety}-${bItem.length}`;
      if (!acc[key]) {
        acc[key] = { ...bItem };
      } else {
        acc[key].qty_stem_flower += bItem.qty_stem_flower;
      }
      return acc;
    }, {})
  );

  purchaseStore.selectedPurchase.order_details = purchaseStore.selectedPurchase.order_details
    .filter((i) => !i.is_selected)
    .map((i) => ({ ...i }));

  purchaseStore.selectedPurchase.order_details.push({
    ...newOrderItem,
    box_items: groupedBoxItems,
  });
};

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
    case 'update':
      console.log('update Order');
      if (purchaseStore.selectedPurchase.is_modified) {
        const response = await purchaseStore.updateSupplierOrder();
        if (response) {
          purchaseStore.selectedPurchase.is_confirmed = false;
          location.reload();
        }
      } else {
        purchaseStore.selectedPurchase.is_modified = true;
      }
      break;
    case 'cancell':
      console.log('Cancelar la orden de compra');
      if (purchaseStore.selectedPurchase.is_cancelled) {
        const response = await purchaseStore.cancellOrder();
        if (response) {
          console.log('Cancelar los items de la orden Venta');
          purchaseStore.selectedPurchase.order.status = 'CANCELADO';
          location.reload();
        }
      } else {
        purchaseStore.selectedPurchase.is_cancelled = true;
      }
      break;
  }
};

const getUrlReportSupOrder = (id) => {
  let urlReportSupOrder = appConfig.urlReportSupOrder.replace('{id_order}', id);
  return urlReportSupOrder;
};

const getUrlReportinvoice = (id) => {
  let urlInvoiceReport = appConfig.urlInvoiceReport.replace('{id_invoice}', id);
  return urlInvoiceReport;
};
// Propiedades computadas
const isTwoQBSelected = computed(() => {
  let qb = purchaseStore.selectedPurchase.order_details.filter(
    (i) => i.box_model === 'QB' && i.is_selected
  );
  return qb.length === 2;
});

const totalMargin = computed(() => {
  if (!purchaseStore.selectedPurchase.order_details) return 0;
  let total = 0;
  purchaseStore.selectedPurchase.order_details.forEach((detail) => {
    total += detail.box_items.reduce((acc, bItem) => {
      return acc + parseFloat(bItem.margin) * parseFloat(bItem.qty_stem_flower);
    }, 0) * detail.quantity;
  });
  return total.toFixed(2);
});

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

const totalStems = computed(() => {
  if (!purchaseStore.selectedPurchase.order_details) return 0;
  let total = 0;
  purchaseStore.selectedPurchase.order_details.forEach((item) => {
    total += item.tot_stem_flower || 0;
  });
  return total;
});

const orderHaveCeroItem = computed(() => {
  if (!purchaseStore.selectedPurchase.order_details) {
    return false;
  }

  for (const item of purchaseStore.selectedPurchase.order_details) {
    let ceroBoxesStem = item.box_items.filter((bItem) => bItem.qty_stem_flower === 0);
    let ceroBoxesCost = item.box_items.filter((bItem) => bItem.stem_cost_price === 0);

    if (ceroBoxesStem.length > 0 || ceroBoxesCost.length > 0) {
      exceedLimitMessage.value = 'No se permiten items con cantidad 0 o costo 0';
      exceedLimit.value = true;
      return true;
    }
  }

  exceedLimitMessage.value = '';
  exceedLimit.value = false;
  return false;
});

// watchers
watch(() => purchaseStore.selectedPurchase,
  (newValue) => {
    console.log('selectedPurchase', newValue);
    isModified.value = true;
    // Inicializar/recalcular totales al cargar una nueva orden
    if (newValue && newValue.order_details) {
      newValue.order_details.forEach(item_detail => {
        // Inicializar stems_bunch si es undefined o null
        if (item_detail.box_items) {
          item_detail.box_items.forEach(product => {
            if (product.stems_bunch === undefined || product.stems_bunch === null) {
              product.stems_bunch = 25;
            }
          });
        }
        calcTotalStemFlower(item_detail);
        calcTotalByItem(item_detail);
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
                        <span class="badge badge-soft-warning text-center fs-6">PEDIDO A PROVEEDOR</span>
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

          <!-- Status Message & Actions -->
          <div class="row mb-2">
            <div class="col-md-8">
              <div class="alert alert-soft-info mb-0" v-if="purchaseStore.selectedPurchase.is_modified">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Orden de Compra Modificada, si actualiza el pedido se actualizarán la o las ordenes de compra
              </div>
            </div>
            <div class="col-md-4 text-end">
              <button class="btn btn-outline-primary" v-if="isTwoQBSelected" @click="mergeQB">
                <IconLayersIntersect2 size="16" stroke="1.5" class="me-1" />
                Unificar a HB
              </button>
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
                          <div class="col" style="flex: 0 0 22%;">
                            <small class="fw-bold">VARIEDAD</small>
                          </div>
                          <div class="col border-start" style="flex: 0 0 10%;">
                            <small class="fw-bold">LARGO</small>
                          </div>
                          <div class="col border-start" style="flex: 0 0 11%;">
                            <small class="fw-bold">BUNCHES</small>
                          </div>
                          <div class="col border-start" style="flex: 0 0 11%;">
                            <small class="fw-bold">T/BUNCH</small>
                          </div>
                          <div class="col border-start" style="flex: 0 0 11%;">
                            <small class="fw-bold">COSTO</small>
                          </div>
                          <div class="col border-start" style="flex: 0 0 11%;">
                            <small class="fw-bold">MARGEN</small>
                          </div>
                          <div class="col border-start" style="flex: 0 0 11%;">
                            <small class="fw-bold">PVP</small>
                          </div>
                          <div class="col border-start" style="flex: 0 0 13%;">
                            <small class="fw-bold">TOTAL</small>
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
                        <!-- Quantity & Delete -->
                        <div class="col-1 border-end p-1">
                          <div class="d-flex align-items-center gap-1">
                            <button class="btn btn-outline-danger border-0"
                                    @click="deleteOrderItem(item)"
                                    :class="{ 'text-danger': item.confirm_delete }"
                                    v-if="!purchaseStore.selectedPurchase.is_confirmed && !purchaseStore.selectedPurchase.is_invoiced">
                              <IconTrash size="14" stroke="1.5" />
                            </button>
                            <input type="number" 
                                   step="1" 
                                   class="form-control form-control-sm text-end input-soft" 
                                   v-model="item.quantity"
                                   @change="(event) => delimitedNumber(event, item)" 
                                   @focus="selectText"
                                   @keydown="(event) => handleKeydown(event, '.form-control-sm')"
                                   :disabled="purchaseStore.selectedPurchase.is_confirmed || purchaseStore.selectedPurchase.is_invoiced" />
                          </div>
                        </div>

                        <!-- Model -->
                        <div class="col-1 border-end p-1 text-center">
                          <div class="d-flex align-items-center justify-content-center gap-1">
                            <span class="badge badge-soft-secondary">{{ item.box_model }}</span>
                            <div v-if="!purchaseStore.selectedPurchase.is_confirmed && !purchaseStore.selectedPurchase.is_invoiced" 
                                 class="d-flex align-items-center gap-1">
                              <IconSitemap size="14" stroke="1.5" 
                                         class="text-primary cursor-pointer"
                                         @click="splitHB(item)"
                                         v-if="item.box_model === 'HB'" />
                              <input type="checkbox" 
                                     class="form-check-input"
                                     v-model="item.is_selected"
                                     v-if="item.box_model === 'QB'" />
                            </div>
                          </div>
                        </div>

                        <!-- Stems -->
                        <div class="col-1 border-end p-1 text-center">
                          <span class="fw-bold text-primary">{{ calcTotalStemFlower(item) }}</span>
                        </div>

                        <!-- Products -->
                        <div class="col-8 border-end p-1">
                          <div v-for="product in item.box_items" :key="product.id" class="product-row mb-1">
                            <div class="row g-1 align-items-center">
                              <div class="col" style="flex: 0 0 22%;">
                                <small class="fw-medium">{{ product.product_name }} {{ product.product_variety }}</small>
                              </div>
                              <div class="col text-center" style="flex: 0 0 10%;">
                                <span class="badge badge-soft-info">{{ product.length }}</span>
                              </div>
                              <div class="col" style="flex: 0 0 11%;">
                                <input type="number" 
                                       step="1" 
                                       class="form-control form-control-sm text-end input-soft"
                                       v-model="product.total_bunches" 
                                       @focus="selectText"
                                       @keydown="event => handleKeydown(event, '.my-input-4')" 
                                       @change="handleBunchOrStemChange($event, item, product, 'total_bunches')"
                                       :class="{ 
                                         'input-error': !product.total_bunches || parseInt(product.total_bunches) <= 0,
                                         'border-danger': !product.total_bunches || parseInt(product.total_bunches) <= 0
                                       }"
                                       :disabled="purchaseStore.selectedPurchase.is_confirmed || purchaseStore.selectedPurchase.is_invoiced" />
                              </div>
                              <div class="col" style="flex: 0 0 11%;">
                                <input type="number" 
                                       step="1" 
                                       class="form-control form-control-sm text-end input-soft"
                                       v-model="product.stems_bunch" 
                                       @focus="selectText"
                                       @keydown="event => handleKeydown(event, '.my-input-5')" 
                                       @change="handleBunchOrStemChange($event, item, product, 'stems_bunch')"
                                       :class="{ 
                                         'input-error': !product.stems_bunch || parseInt(product.stems_bunch) <= 0,
                                         'border-danger': !product.stems_bunch || parseInt(product.stems_bunch) <= 0
                                       }"
                                       :disabled="purchaseStore.selectedPurchase.is_confirmed || purchaseStore.selectedPurchase.is_invoiced" />
                              </div>
                              <div class="col" style="flex: 0 0 11%;">
                                <input type="number" 
                                       step="0.01" 
                                       class="form-control form-control-sm text-end input-soft"
                                       v-model="product.stem_cost_price" 
                                       @focus="selectText"
                                       @keydown="event => handleKeydown(event, '.my-input-2')" 
                                       @change="(event) => { formatNumber(event); }"
                                       :class="{ 
                                         'input-error': !product.stem_cost_price || parseFloat(product.stem_cost_price) <= 0.0,
                                         'border-danger': !product.stem_cost_price || parseFloat(product.stem_cost_price) <= 0.0
                                       }"
                                       :disabled="purchaseStore.selectedPurchase.is_confirmed || purchaseStore.selectedPurchase.is_invoiced" />
                              </div>
                              <div class="col" style="flex: 0 0 11%;">
                                <input type="number" 
                                       step="0.01" 
                                       class="form-control form-control-sm text-end input-soft"
                                       v-model="product.margin" 
                                       @focus="selectText"
                                       @keydown="event => handleKeydown(event, '.my-input-3')" 
                                       @change="(event) => { formatNumber(event); }"
                                       :class="{ 
                                         'input-error': !product.margin || parseFloat(product.margin) <= 0.0,
                                         'border-danger': !product.margin || parseFloat(product.margin) <= 0.0
                                       }"
                                       :disabled="purchaseStore.selectedPurchase.is_confirmed || purchaseStore.selectedPurchase.is_invoiced" />
                              </div>
                              <div class="col text-center" style="flex: 0 0 11%;">
                                <span class="badge badge-soft-success">
                                  {{ (parseFloat(product.stem_cost_price) + parseFloat(product.margin)).toFixed(2) }}
                                </span>
                              </div>
                              <div class="col text-center" style="flex: 0 0 13%;">
                                <span class="fw-bold text-success">
                                  {{ calcTotalByItem(item) }}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>

                        <!-- Total Purchase -->
                        <div class="col-1 p-1">
                          <div v-for="product in item.box_items" :key="product.id" class="mb-1 text-center">
                            <span class="fw-bold text-warning">
                              {{ purchaseStore.formatNumber(product.stem_cost_price * calcAndGetProductQtyStemFlower(product)) }}
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
                    <div class="col-md-3">
                      <div class="p-2 bg-soft-secondary rounded text-center">
                        <div class="h6 mb-1 text-warning">${{ purchaseStore.formatNumber(totalCost) }}</div>
                        <small class="text-muted">Costo</small>
                      </div>
                    </div>
                    <div class="col-md-3">
                      <div class="p-2 bg-soft-secondary rounded text-center">
                        <div class="h6 mb-1 text-info">${{ totalMargin }}</div>
                        <small class="text-muted">Margen</small>
                      </div>
                    </div>
                    <div class="col-md-3">
                      <div class="p-2 bg-soft-secondary rounded text-center">
                        <div class="h6 mb-1 text-success">${{ purchaseStore.formatNumber(parseFloat(totalMargin) + parseFloat(totalCost)) }}</div>
                        <small class="text-muted">Total Venta</small>
                      </div>
                    </div>
                    <div class="col-md-3">
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

          <!-- Action Buttons -->
          <div class="row mt-3">
            <div class="col-12">
              <div class="card card-soft border-0">
                <div class="card-body p-reduced">
                  <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
                    <div>
                      <button type="button" 
                              class="btn btn-outline-danger" 
                              @click="updateOrder('cancell')"
                              v-if="!purchaseStore.selectedPurchase.is_invoiced && purchaseStore.selectedPurchase.order.status === 'CANCELADO'">
                        <IconBan size="16" stroke="1.5" class="me-1" />
                        <span v-if="purchaseStore.selectedPurchase.is_cancelled">Confirmar Cancelación</span>
                        <span v-else>Cancelar</span>
                      </button>
                    </div>
                    
                    <div class="d-flex gap-2 flex-wrap">
                      <button type="button" 
                              class="btn btn-default btn-sm" 
                              @click="updateOrder('update')"
                              :disabled="orderHaveCeroItem" 
                              v-if="isModified && !purchaseStore.selectedPurchase.is_confirmed">
                        <IconRefresh size="16" stroke="1.5" class="me-1" />
                        <span v-if="purchaseStore.selectedPurchase.is_modified">Confirmar</span>
                        <span v-else>Actualizar</span>
                      </button>
                      
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
                              v-if="purchaseStore.selectedPurchase.order.status === 'CONFIRMADO'"
                              @click="purchaseStore.createInvoice()">
                        <IconFileDollar size="16" stroke="1.5" class="me-1" />
                        Registrar Factura
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
}

input[type="checkbox"] {
  width: 14px;
  height: 14px;
}

.alert {
  border-radius: 6px;
  padding: 0.75rem;
}

.input-error {
  background-color: #fff3f3;
  color: #dc3545;
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