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
  <div class="container-fluid">
    <div class="row pt-2">
      <div class="col">
        <div class="container-fluid" v-if="purchaseStore.selectedPurchase.order">
          <div class="row">
            <div class="col-12 text-center fs-4 fw-semibold text-danger" v-if="exceedLimit || confirmDelete">
              <IconAlertTriangle size="20" stroke="1.5" /> &nbsp;
              <span v-if="confirmDelete">
                {{ deleteMessage }}
              </span>
              <span v-if="exceedLimit">
                {{ exceedLimitMessage }}
              </span>
            </div>
          </div>
          <div class="row">
            <div class="col-12 rounded-1 shadow-sm p-2 bg-orange-700 border-gray-300 text-white">
              <div class="row">
                <div class="col-5 fs-4">
                  {{ purchaseStore.selectedPurchase.order.partner.name }}
                </div>
                <div class="col-2 text-center fs-5 upper">
                  <span>Orden De Compra</span>
                </div>
                <div class="col-5 text-end fs-6">
                  <strong class="border-gray-500 rounded-1 bg-white text-dark ps-2 pe-2">
                    Pedido {{ purchaseStore.selectedPurchase.order.serie }}-{{ String(purchaseStore.selectedPurchase.order.consecutive).padStart(6, '0') }}
                  </strong>
                  <span class="pe-1 ps-1"></span>
                  <strong class="border-gray-500 rounded-1 bg-white text-dark ps-2 pe-2" :class="{
                    'bg-green-600 text-white': purchaseStore.selectedPurchase.order.status === 'CONFIRMADO',
                    'bg-yellow-300': purchaseStore.selectedPurchase.order.status === 'PENDIENTE',
                    'bg-red-600 text-white': purchaseStore.selectedPurchase.order.status === 'CANCELADO',
                    'bg-orange-600 text-white': purchaseStore.selectedPurchase.order.status === 'MODIFICADO'
                  }">
                    {{ purchaseStore.selectedPurchase.order.status }}
                  </strong>
                </div>
              </div>
              <div class="row">
                <div class="col-1 text-end">ID:</div>
                <div class="col-1">{{ purchaseStore.selectedPurchase.order.partner.business_tax_id }}</div>
                <div class="col-1 text-end">Dir:</div>
                <div class="col-6">
                  {{ purchaseStore.selectedPurchase.order.partner.address }}
                  {{ purchaseStore.selectedPurchase.order.partner.city }}
                </div>
                <div class="col-1 text-end">Skype:</div>
                <div class="col-2">{{ purchaseStore.selectedPurchase.order.partner.skype }}</div>
              </div>
              <div class="row pt-1">
                <div class="col-1 text-end">Contacto:</div>
                <div class="col-8 d-flex gap-2" v-if="purchaseStore.selectedPurchase.order.partner.contact">
                  <span>{{ purchaseStore.selectedPurchase.order.partner.contact.name }}</span>
                  <span>{{ purchaseStore.selectedPurchase.order.partner.contact.email }}</span>
                  <span>{{ purchaseStore.selectedPurchase.order.partner.contact.phone }}</span>
                  <span class="badge bg-green-600">
                    {{ purchaseStore.selectedPurchase.order.partner.contact.contact_type }}
                  </span>
                </div>
                <div class="col-1 text-end fw-semibold">
                  Consolida:
                </div>
                <div class="col-2">
                  {{ purchaseStore.selectedPurchase.order.partner.consolidate ? 'Si' : 'No' }}
                </div>
              </div>
            </div>
          </div>
          <div class="row pb-2 pt-2">
            <div class="col-8">
              <span class="text-danger" v-if="purchaseStore.selectedPurchase.is_modified">
                Orden de Compra Modificada, si actualiza el pedido se actualizarán la o las ordenes de compra
              </span>
            </div>
            <div class="col-4 text-end">
              <button class="btn btn-sm btn-default" v-if="isTwoQBSelected" @click="mergeQB">
                <IconLayersIntersect2 size="20" stroke="1.5" />
                Unificar a HB
              </button>
            </div>
          </div>
          <div class="row p-1 text-white border-orange-700">
            <div class="col-1 border-end bg-gray-400 text-center">Cant</div>
            <div class="col-1 border-end bg-gray-400 text-center">Mdl</div>
            <div class="col-1 border-end bg-gray-400 text-center">Tallos</div>
            <div class="col-8 border-end bg-sky-500">
              <div class="d-flex">
                <div class="flex-grow-1" style="flex: 0 0 26%; border-right: 1px solid #ddd; text-align: center;">
                  Variedad
                </div>
                <div class="flex-grow-1" style="flex: 0 0 12%; border-right: 1px solid #ddd; text-align: center;">
                  Bunches
                </div>
                <div class="flex-grow-1" style="flex: 0 0 12%; border-right: 1px solid #ddd; text-align: center;">
                  Tallos/Bunch
                </div>
                <div class="flex-grow-1" style="flex: 0 0 12%; border-right: 1px solid #ddd; text-align: center;">
                  Costo
                </div>
                <div class="flex-grow-1" style="flex: 0 0 12%; border-right: 1px solid #ddd; text-align: center;">
                  Margen
                </div>
                <div class="flex-grow-1" style="flex: 0 0 12%; text-align: center;">
                  PVP
                </div>
                <div class="flex-grow-1" style="flex: 0 0 14%; text-align: center;">
                  Total
                </div>
              </div>
            </div>
            <div class="col-1 border-end bg-gray-400 text-center">T Compra</div>
          </div>
          <div v-for="(item, idx) in purchaseStore.selectedPurchase.order_details" :key="item.order_item_id"
            class="row mb-1 border my-hover-2" :class="{ 'bg-gray': idx % 2 === 0 }">
            <div class="col-1 border-end d-flex gap-1 justify-content-between align-items-center">
              <IconTrash size="30" stroke="1.5" :class="item.confirm_delete ? 'text-danger' : 'text-dark'"
                @click="deleteOrderItem(item)"
                v-if="!purchaseStore.selectedPurchase.is_confirmed && !purchaseStore.selectedPurchase.is_invoiced" />
              <input type="number" step="1" class="form-control form-control-sm text-end" v-model="item.quantity"
                @change="(event) => delimitedNumber(event, item)" @focus="selectText"
                @keydown="(event) => handleKeydown(event, '.form-control-sm')"
                :disabled="purchaseStore.selectedPurchase.is_confirmed || purchaseStore.selectedPurchase.is_invoiced" />
            </div>
            <div class="col-1 text-end border-end d-flex align-items-center gap-2">
              {{ item.box_model }}
              <span
                v-if="!purchaseStore.selectedPurchase.is_confirmed && !purchaseStore.selectedPurchase.is_invoiced">/</span>
              <IconSitemap size="20" stroke="1.5" @click="splitHB(item)"
                v-if="item.box_model === 'HB' && (!purchaseStore.selectedPurchase.is_confirmed && !purchaseStore.selectedPurchase.is_invoiced)" />
              <input type="checkbox" v-model="item.is_selected"
                v-if="item.box_model === 'QB' && (!purchaseStore.selectedPurchase.is_confirmed && !purchaseStore.selectedPurchase.is_invoiced)" />
            </div>
            <div class="col-1 text-end border-end d-flex align-items-center justify-content-end">
              {{ calcTotalStemFlower(item) }}
            </div>
            <div class="col-8">
              <div v-for="product in item.box_items" :key="product.id" class="d-flex justify-content-between">
                <span class="border-end text-end" style="width: 26%; padding-right: 0.5rem;">
                  {{ product.product_name }} {{ product.product_variety }}
                </span>
                <span class="border-end text-end" style="width: 12%; padding-right: 0.5rem;">
                  <input type="number" step="1" class="form-control form-control-sm text-end my-input-4"
                    v-model="product.total_bunches" @focus="selectText"
                    @keydown="event => handleKeydown(event, '.my-input-4')" 
                    @change="handleBunchOrStemChange($event, item, product, 'total_bunches')"
                    :disabled="purchaseStore.selectedPurchase.is_confirmed || purchaseStore.selectedPurchase.is_invoiced"
                  />
                </span>
                <span class="border-end text-end" style="width: 12%; padding-right: 0.5rem;">
                  <input type="number" step="1" class="form-control form-control-sm text-end my-input-5"
                    v-model="product.stems_bunch" @focus="selectText"
                    @keydown="event => handleKeydown(event, '.my-input-5')" 
                    @change="handleBunchOrStemChange($event, item, product, 'stems_bunch')"
                    :disabled="purchaseStore.selectedPurchase.is_confirmed || purchaseStore.selectedPurchase.is_invoiced"
                  />
                </span>
                <span class="border-end text-end" style="width: 12%; padding-right: 0.5rem;">
                  <input type="number" step="0.01" class="form-control form-control-sm text-end my-input-2"
                    v-model="product.stem_cost_price" @focus="selectText"
                    @keydown="event => handleKeydown(event, '.my-input-2')" 
                    @change="(event) => { formatNumber(event); handlePriceOrMarginChange(event, item); }"
                    :class="{ 'bg-red-200': parseFloat(product.stem_cost_price) <= 0.0 }"
                    :disabled="purchaseStore.selectedPurchase.is_confirmed || purchaseStore.selectedPurchase.is_invoiced"
                  />
                </span>
                <span class="border-end text-end" style="width: 12%; padding-right: 0.5rem;">
                  <input type="number" step="0.01" class="form-control form-control-sm text-end my-input-3"
                    v-model="product.margin" @focus="selectText"
                    @keydown="event => handleKeydown(event, '.my-input-3')" 
                    @change="(event) => { formatNumber(event); handlePriceOrMarginChange(event, item); }"
                    :class="{ 'bg-red-200': parseFloat(product.margin) <= 0.0 }"
                    :disabled="purchaseStore.selectedPurchase.is_confirmed || purchaseStore.selectedPurchase.is_invoiced"
                  />
                </span>
                <span class="text-end" style="width: 12%; padding-right: 0.5rem;">
                  <span class="form-control form-control-sm">
                    {{ (parseFloat(product.stem_cost_price) + parseFloat(product.margin)).toFixed(2) }}
                  </span>
                </span>
                <span class="text-end" style="width: 14%; padding-right: 0.5rem;">
                  <span class="form-control form-control-sm text-end my-input-6">
                    {{ calcTotalByItem(item) }}
                  </span>
                </span>
              </div>
            </div>
            <div class="col-1">
              <div v-for="product in item.box_items" :key="product.id" class="d-flex justify-content-between">
                <input type="text" readonly class="form-control form-control-sm text-end"
                  :value="purchaseStore.formatNumber(product.stem_cost_price * calcAndGetProductQtyStemFlower(product))" />
              </div>
            </div>
          </div>
          <div class="row">
            <div class="col-3">
              <div class="row shadow-sm p-2 border-orange-700 bg-transparent rounded-1">
                <div class="col-9 fs-5 text-start text-end">{{ totalBoxesHB }}</div>
                <div class="col-3 fs-5 text-end">HB's:</div>
                <div class="col-9 fs-5 text-start text-end">{{ totalBoxesQB }}</div>
                <div class="col-3 fs-5 text-end">QB's:</div>
                <div class="col-9 fs-5 text-start text-end">{{ totalStems }}</div>
                <div class="col-3 fs-5 text-end">Tallos:</div>
              </div>
            </div>
            <div class="col-4 offset-5">
              <div class="row bg-trasparent border-orange-700 rounded-1 shadow-sm px-2" style="padding-top: 2.375rem; padding-bottom: 2.375rem;">
                <div class="col-7 text-end border-end fs-5 text-lime-600 align-self-center">Total Pedido:</div>
                <div class="col-5 fs-5 text-lime-600 text-end align-self-center">
                  {{ purchaseStore.formatNumber(totalCost) }}
                </div>
              </div>
            </div>
          </div>
          <div class="row mt-3 border-top pt-3">
            <div class="col-4">
              <button type="button" class="btn btn-sm btn-default text-danger" @click="updateOrder('cancell')"
                v-if="!purchaseStore.selectedPurchase.is_invoiced && purchaseStore.selectedPurchase.order.status === 'CANCELADO'">
                <IconBan size="20" stroke="1.5" />
                <span v-if="purchaseStore.selectedPurchase.is_cancelled">
                  Confirmar Cancelación
                </span>
                <span v-else> Cancelar </span>
              </button>
            </div>
            <div class="col-8 text-end d-flex gap-3 justify-content-end">
              <span class="ps-4 pe-4"></span>
              <button type="button" class="btn btn-sm btn-default" @click="updateOrder('update')"
                :disabled="orderHaveCeroItem" v-if="isModified && !purchaseStore.selectedPurchase.is_confirmed">
                <IconRefresh size="20" stroke="1.5" />
                <span v-if="purchaseStore.selectedPurchase.is_modified">
                  Confirmar
                </span>
                <span v-else>Actualizar</span>
              </button>
              <button class="btn btn-default btn-sm" @click="updateOrder('confirm')">
                <IconCheck size="20" stroke="1.5" v-if="!purchaseStore.selectedPurchase.is_confirmed" />
                <span v-if="!purchaseStore.selectedPurchase.is_confirmed">Confirmar OC</span>
                <IconCheckbox size="20" stroke="1.5" v-if="purchaseStore.selectedPurchase.is_confirmed" />
                <span v-if="purchaseStore.selectedPurchase.is_confirmed">Si Confirmar OC</span>
              </button>
              <button class="btn btn-sm btn-default">
                <a :href="getUrlReportSupOrder(purchaseStore.selectedPurchase.order.id)">
                  <IconPrinter size="20" stroke="1.5" />
                  Imprimir Ord Compra
                </a>
              </button>
              <button class="btn btn-sm btn-default" v-if="purchaseStore.selectedPurchase.order.status === 'CONFIRMADO'"
                @click="purchaseStore.createInvoice()">
                <IconFileDollar size="20" stroke="1.5" />
                Registrar Factura
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.my-input,
.my-input-2,
.my-input-3,
.my-input-4,
.my-input-5,
.my-input-6 {
  border: 1px solid #ccc;
  border-radius: 2px;
  text-align: right;
}
.w-30 {
  width: 30% !important;
}
.w-14 {
  width: 14% !important;
}
</style>