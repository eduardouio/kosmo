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
} from '@tabler/icons-vue';

const orderStore = useOrdersStore();
const confirmDelete = ref(false);
const exceedLimit = ref(false);
const deleteMessage = ref('El item marcado será elimnado del pedido, click nuevamente para confirmar');
const exceedLimitMessage = ref();
const isModified = ref(false);

// Methods

const calcAndGetProductQtyStemFlower = (product) => {
  const bunches = parseInt(product.total_bunches) || 0;
  const stemsPerBunch = parseInt(product.stems_bunch) || 25; // Default 25 si no está definido o es 0
  return bunches * stemsPerBunch;
};

const calcTotalByItem = (item)=>{ 
  let total = 0;
  if (item.box_items) {
    total = item.box_items.reduce((acc, boxItem) => {
      const qty_stem_flower = calcAndGetProductQtyStemFlower(boxItem);
      boxItem.qty_stem_flower = qty_stem_flower; // Actualizar la propiedad qty_stem_flower
      const cost_price = parseFloat(boxItem.stem_cost_price) || 0;
      const margin = parseFloat(boxItem.margin) || 0;
      return acc + ((cost_price + margin) * qty_stem_flower);
    }, 0) * item.quantity;
  }
  item.line_total = total.toFixed(2);

  item.line_price = item.box_items.reduce((acc, boxItem) => {
    return acc + (boxItem.stem_cost_price * parseFloat(boxItem.qty_stem_flower));
  }, 0);
  return total.toFixed(2);
};

const delimitedNumber = (event, item) => {
  exceedLimit.value = false;
  let value = parseInt(event.target.value);
  let maxValue = orderStore.limitsNewOrder.filter(i=>i.order_item_id === item.order_item_id).map(i=>i.quantity);
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

const formatInteger = (event, box = null) => {
    let value = event.target.value;
    value = value.replace(',', '.');
    if (value === '' || value === '.' || value === ',' || isNaN(value) || value === ' ' || value === '0') {
        event.target.value = '0';
        return;
    }
    event.target.value = parseInt(value);
}

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

  // Recalcular los totales del item.
  totalStemFlowerOrderItem(item); // Actualiza item.tot_stem_flower y product.qty_stem_flower
  calcTotalByItem(item);   // Actualiza item.line_total
};

// Methods for splitting and merging boxes
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
  }else{
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
      if (orderStore.selectedOrder.is_confirmed){
        orderStore.selectedOrder.is_modified = false;
        orderStore.selectedOrder.order.status = 'CONFIRMADO';
        orderStore.updateOrder()
      }else{
        orderStore.selectedOrder.is_confirmed = true;
      }
      break;
    case 'update':
      if(orderStore.selectedOrder.is_modified){
        const response = await orderStore.updateOrder()        
        if (response){
          orderStore.selectedOrder.is_modified = false;
          location.reload();
        }
      }else{
       orderStore.selectedOrder.is_modified = true;
      }
      break;
    case 'cancell':
      if(orderStore.selectedOrder.is_cancelled){
        orderStore.selectedOrder.order.status = 'CANCELADO';
        const response = await orderStore.cancellOrder();
        if (response){
          orderStore.selectedOrder.is_cancelled = true;
          orderStore.selectedOrder.is_modified = false;
          location.reload();
        }
      }else{
        orderStore.selectedOrder.is_cancelled = true;
      }
      break;
  }
}


// computed Properties
const isTwoQBSelected = computed(() => {
  let qb = orderStore.selectedOrder.order_details.filter(i => i.box_model === 'QB' && i.is_selected);
  return qb.length === 2;
});


const totalStemFlowerOrderItem = (order_item)=>{
  // Calcula los tallos igual que en OrderPreview
  let total_stems = order_item.box_items.reduce((acc, item) => {
    const bunches = parseInt(item.total_bunches) || 0;
    const stemsPerBunch = parseInt(item.stems_bunch) || 25;
    const stems = bunches * stemsPerBunch;
    item.qty_stem_flower = stems; // Actualizar la propiedad qty_stem_flower
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

//watchers
watch(() => orderStore.selectedOrder, 
  (newValue) => {
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
        totalStemFlowerOrderItem(item_detail);
        calcTotalByItem(item_detail);
      });
    }
  },
  { deep: true, immediate: true }
);


</script>

<template>
  <div class="container-fluid bg-transparent">
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
      <div class="row pt-2">  
      <div class="col-12 rounded-1 shadow-sm p-2 bordered bg-teal-600 border-gray-300 text-white">
        <div class="row">
          <div class="col-4 fs-4">
            {{ orderStore.selectedOrder.order.partner.name }}
          </div>
          <div class="col-4 text-center fs-5">
          <span>PEDIDO DE CLIENTE</span>  
          </div>
          <div class="col-4 text-end fs-6">
              <strong class="border-gray-500 rounded-1 bg-white text-dark ps-2 pe-2">
                Pedido {{ orderStore.selectedOrder.order.serie }}-{{ orderStore.selectedOrder.order.consecutive ? String(orderStore.selectedOrder.order.consecutive).padStart(6, '0') : 'N/A' }}
              </strong>
              <span class="pe-1 ps-1"></span>
              <strong class="border-gray-500 rounded-1 bg-white text-dark ps-2 pe-2" 
              :class="{
                'bg-green-600 text-white': orderStore.selectedOrder.order.status === 'CONFIRMADO',
                'bg-yellow-300': orderStore.selectedOrder.order.status === 'PENDIENTE',
                'bg-red-600 text-white': orderStore.selectedOrder.order.status === 'CANCELADO',
                'bg-orange-600 text-white': orderStore.selectedOrder.order.status === 'MODIFICADO'
              }"
              >{{ orderStore.selectedOrder.order.status }} </strong>
          </div>
        </div>
        <div class="row">
          <div class="col-1 text-end">ID:</div>
          <div class="col-1">{{ orderStore.selectedOrder.order.partner.business_tax_id }}</div>
          <div class="col-1 text-end">Dir:</div>
          <div class="col-6">
            {{ orderStore.selectedOrder.order.partner.address }}
            {{ orderStore.selectedOrder.order.partner.city }}
          </div>
          <div class="col-1 text-end">Skype:</div>
          <div class="col-2">{{ orderStore.selectedOrder.order.partner.skype }}</div>
        </div>
        <div class="row pt-1">
          <div class="col-1 text-end">Contacto:</div>
          <div class="col-8 d-flex gap-2" v-if="orderStore.selectedOrder.order.partner.contact">
            <span>{{ orderStore.selectedOrder.order.partner.contact.name }}</span>
            <span>{{ orderStore.selectedOrder.order.partner.contact.email }}</span>
            <span>{{ orderStore.selectedOrder.order.partner.contact.phone }}</span>
            <span class="badge bg-green-600">{{ orderStore.selectedOrder.order.partner.contact.contact_type }}</span>
          </div>
          <div class="col-1 text-end fw-semibold">
            Consolida:
          </div>
          <div class="col-2">
            {{ orderStore.selectedOrder.order.partner.consolidate ? 'Si' : 'No' }}
          </div>
        </div>
      </div>
    </div>
    <div class="row pb-2 pt-2">
      <div class="col-8">
        <span class="text-danger" v-if="orderStore.selectedOrder.is_modified">
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
    <div class="row p-1 text-white border-teal-500">
      <div class="col-1 col-narrow-custom border-end bg-gray-400 text-center">Cant</div>
      <div class="col-1 col-narrow-custom border-end bg-gray-400 text-center">Mdl</div>
      <div class="col-1 col-narrow-custom border-end bg-gray-400 text-center">Tallos</div>
      <div class="col-3 col-wide-custom border-end bg-gray-400 text-center">Proveedor</div>
      <div class="col-5 border-end bg-sky-500">
        <div class="d-flex">
          <div class="flex-grow-1" style="flex: 0 0 30%; border-right: 1px solid #ddd; text-align: center;">
            Variedad
          </div>
          <div class="flex-grow-1" style="flex: 0 0 14%; border-right: 1px solid #ddd; text-align: center;">
            Bunches
          </div>
          <div class="flex-grow-1" style="flex: 0 0 14%; border-right: 1px solid #ddd; text-align: center;">
            Tallos/Bunch
          </div>
          <div class="flex-grow-1" style="flex: 0 0 14%; border-right: 1px solid #ddd; text-align: center;">
            Costo
          </div>
          <div class="flex-grow-1" style="flex: 0 0 14%; border-right: 1px solid #ddd; text-align: center;">
            Margen
          </div>
          <div class="flex-grow-1" style="flex: 0 0 14%; text-align: center;">
            PVP
          </div>
        </div>
      </div>
      <div class="col-1 bg-kosmo-green text-center">C/USD</div>
    </div>

    <div v-for="item, idx in orderStore.selectedOrder.order_details" :key="item" class="row mb-1 border my-hover-2 d-flex align-items-center"
      :class="{ 'bg-gray': idx % 2 === 0 }">
      <div class="col-1 col-narrow-custom border-end d-flex gap-1 justify-content-between align-items-center">
        <IconTrash 
          size="24"
          stroke="1.5"
          :class="item.confirm_delete ? 'text-danger' : 'text-dark'"
          @click="deleteOrderItem(item)"
          v-if="!orderStore.selectedOrder.is_confirmed && !orderStore.selectedOrder.is_invoiced"
        />
        <input type="number" step="1" class="form-control form-control-sm text-end" v-model="item.quantity"
          @change="(event) => delimitedNumber(event, item)" @focus="selectText"
          @keydown="event => handleKeydown(event, '.form-control-sm')"
          :disabled="orderStore.selectedOrder.is_confirmed || orderStore.selectedOrder.is_invoiced"
           />
      </div>
      <div class="col-1 col-narrow-custom text-end border-end d-flex align-items-center gap-1">
        {{ item.box_model }}
        <span v-if="!orderStore.selectedOrder.is_invoiced">/</span>
        <IconSitemap size="18" stroke="1.5" @click="splitHB(item)" v-if="item.box_model === 'HB' && !orderStore.selectedOrder.is_invoiced" />
        <input type="checkbox" v-model="item.is_selected" v-if="item.box_model === 'QB' && !orderStore.selectedOrder.is_invoiced" />
      </div>
      <div class="col-1 col-narrow-custom text-end border-end d-flex align-items-center justify-content-end px-1">
        {{ totalStemFlowerOrderItem(item) }}
      </div>
      <div class="col-3 col-wide-custom d-flex align-items-center text-truncate px-2">
        <span class="text-truncate">
          {{ item.partner.partner.name }}
        </span>
      </div>
      <div class="col-5">
        <div v-for="product in item.box_items" :key="product.id" class="d-flex justify-content-between">
          <span class="border-end text-end w-30 pe-2">
            {{ product.product_name }} {{ product.product_variety }}
          </span>
          <span class="border-end text-end w-14 pe-2">
            <input type="number" step="1" class="form-control form-control-sm text-end my-input-4"
              v-model="product.total_bunches" @focus="selectText"
              @keydown="event => handleKeydown(event, '.my-input-4')" 
              @change="handleBunchOrStemChange($event, item, product, 'total_bunches')"
              :disabled="orderStore.selectedOrder.is_confirmed || orderStore.selectedOrder.is_invoiced"
            />
          </span>
          <span class="border-end text-end w-14 pe-2">
            <input type="number" step="1" class="form-control form-control-sm text-end my-input-5"
              v-model="product.stems_bunch" @focus="selectText"
              @keydown="event => handleKeydown(event, '.my-input-5')" 
              @change="handleBunchOrStemChange($event, item, product, 'stems_bunch')"
              :disabled="orderStore.selectedOrder.is_confirmed || orderStore.selectedOrder.is_invoiced"
            />
          </span>
          <span class="border-end text-end w-14 pe-2">
            <input type="number" step="0.01" class="form-control form-control-sm text-end my-input-2"
              v-model="product.stem_cost_price" @focus="selectText"
              @keydown="event => handleKeydown(event, '.my-input-2')" @change="formatNumber"
              :class="{ 'bg-red-200': parseFloat(product.stem_cost_price) <= 0.00 }"
              :disabled="orderStore.selectedOrder.is_confirmed || orderStore.selectedOrder.is_invoiced"
            />
          </span>
          <span class="border-end text-end w-14 pe-2">
            <input type="number" step="0.01" class="form-control form-control-sm text-end my-input-3"
              v-model="product.margin" @focus="selectText" @keydown="event => handleKeydown(event, '.my-input-3')"
              @change="formatNumber" :class="{ 'bg-red-200': parseFloat(product.margin) <= 0.00 }"
              :disabled="orderStore.selectedOrder.is_confirmed || orderStore.selectedOrder.is_invoiced"
            />
          </span>
          <span class="text-end w-14 pe-2 form-control form-control-sm">
            {{ (parseFloat(product.stem_cost_price) + parseFloat(product.margin)).toFixed(2) }}
          </span>
        </div>
      </div>
      <div class="col-1 d-flex align-items-end justify-content-end">
        <span class="form-control form-control-sm text-end my-input-6">
          {{ calcTotalByItem(item) }}
        </span>
      </div>
    </div>
    <div class="row">
      <div class="col-3">
        <div class="row shadow-sm p-2 border-teal-500 rounded-1 bg-transparent">
          <div class="col-9 text-teal-700 fs-5 text-start text-end">{{ totalBoxesHB }}</div>
          <div class="col-3 text-teal-700 fs-5 text-end">HB's:</div>
          <div class="col-9 text-teal-700 fs-5 text-start text-end">{{ totalBoxesQB }}</div>
          <div class="col-3 text-teal-700 fs-5 text-end">QB's:</div>
          <div class="col-9 text-teal-700 fs-5 text-start text-end">{{ totalStems }}</div>
          <div class="col-3 text-teal-700 fs-5 text-end">Tallos:</div>
        </div>
      </div>
      <div class="col-4 offset-5">
        <div class="row bg-transparent-200 border-teal-500 rounded-1 shadow-sm p-2">
          <div class="col-7 fs-5 text-end border-end text-teal-700">Costo:</div>
          <div class="col-5 fs-5 text-teal-700 text-end">{{orderStore.formatNumber(totalCost) }}</div>
          <div class="col-7 fs-5 text-end border-end text-teal-700">Margen:</div>
          <div class="col-5 fs-5 text-teal-700 text-end">{{ orderStore.formatNumber(totalMargin) }}</div>
          <div class="col-7 fs-5 text-end border-end text-teal-700">Total Pedido:</div>
          <div class="col-5 fs-5 text-teal-700 text-end">
            {{  orderStore.formatNumber(parseFloat(totalMargin) + parseFloat(totalCost)) }}
          </div>
        </div>
      </div>
    </div>
    <div class="row mt-3 border-top pt-3">
      <div class="col-4">
        <button 
          type="button" class="btn btn-sm btn-default text-danger d-flex align-items-center gap-1" @click="updateOrder('cancell')" v-if="orderStore.selectedOrder.is_confirmed && !orderStore.selectedOrder.is_invoiced">
          
          <IconBan size="20" stroke="1.5" />
          <span v-if="orderStore.selectedOrder.is_cancelled">Confirmar Cancelación</span>
          <span v-else=""> Cancelar Pedido </span>
        </button>
      </div>
      <div class="col-8 text-end d-flex gap-3 justify-content-end">
        <span class="ps-4 pe-4"></span>
        <button 
          type="button"
          class="btn btn-sm btn-default"
          @click="updateOrder('update')" 
          :disabled="orderHaveCeroItem" 
          v-if="isModified && (!orderStore.selectedOrder.is_confirmed && !orderStore.selectedOrder.is_invoiced)"
        >
          <IconRefresh size="20" stroke="1.5" />
          <span v-if="orderStore.selectedOrder.is_modified">Confirmar Actualización</span>
          <span v-else>Actualizar </span>
        </button>
        <button class="btn btn-default btn-sm">
          <a :href="getUrlReportCusOrder(orderStore.selectedOrder.order.id)">
            <IconPrinter size="20" stroke="1.5" />
            Imprimir Ord Venta
          </a>
        </button>
        <button class="btn btn-default btn-sm" v-if="orderStore.selectedOrder.is_invoiced">
          <a :href="getUrlReportinvoice(orderStore.selectedOrder.id_invoice)">
          <IconPrinter size="20" stroke="1.5" />
          Imprimir Factura
          </a>
        </button>
        <button 
          class="btn btn-default btn-sm"
          v-if="orderStore.selectedOrder.is_confirmed &&  !orderStore.selectedOrder.is_invoiced"
          @click="careteOrderInvoice"
          >
          <IconSettingsDollar size="20" stroke="1.5" />
          Generar Factura
        </button>
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

/* Estilos predeterminados para el checkbox */
input[type="checkbox"] {
  appearance: auto;
  -webkit-appearance: auto;
  -moz-appearance: auto;
  margin: 0;
  padding: 0;
  background: none;
  border: none;
  box-shadow: none;
}

</style>