<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useOrdersStore } from '@/stores/orders';
import { useBaseStore } from '@/stores/base';
import { 
    IconTrash,
    IconCheckbox,
    IconSitemap,
    IconBan,
    IconLayersIntersect2, 
    IconAlertTriangle,
    IconArrowLeft,
} from '@tabler/icons-vue';

const orderStore = useOrdersStore();
const baseStore = useBaseStore();
const confirmDelete = ref(false);
const exceedLimit = ref(false);
const deleteMessage = ref('El item marcado será elimnado del pedido, click nuevamente para confirmar');
const exceedLimitMessage = ref();
const router = useRouter();

const calcTotalByItem = (item)=>{ 
  let total = 0;
  let items = item.box_items.map(item => item)
  total = items.reduce((acc, item) => {
    return acc + ((item.stem_cost_price + parseFloat(item.margin)) * parseFloat(item.qty_stem_flower));
  }, 0);
  return total.toFixed(2);
};

const cancelOrder = () => {
  orderStore.newOrder = [];
  orderStore.selectedCustomer = null;
  baseStore.stastagesLoaded = 0 ;
  router.push('/');
};  

const delimitedNumber = (event, item) => {
  exceedLimit.value = false;
  let value = parseInt(event.target.value);
  let maxValue = orderStore.limitsNewOrder.filter(i=>i.stock_detail_id === item.stock_detail_id).map(i=>i.quantity);
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
    orderStore.newOrder = orderStore.newOrder.filter(i => i.stock_detail_id !== item.stock_detail_id);
  } else {
    confirmDelete.value = true;
    item.confirm_delete = true;
  }
}

const createOrder = async() => {
  new_order = await orderStore.sendOrder(
    stockStore.stockDay
  );
  baseStore.stagesLoaded = 0;
  router.push('/');
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


// Methods for splitting and merging boxes
const splitHB = (item) => {
  const newOrder = orderStore.selectedOrder.order_details.filter(o => o.order_item_id !== item.order_item_id);
  const stem_flower = item.box_items.map(i => i.qty_stem_flower);
  const id = item.order_item_id;

  if ((item.tot_stem_flower % 2) === 0) {
    newOrder.push({
      ...item,
      tot_stem_flower: item.tot_stem_flower / 2,
      box_model: 'QB',
    });
    newOrder.push({
      ...item,
      tot_stem_flower: item.tot_stem_flower / 2,
      box_model: 'QB',
    });
  }
  newOrder.forEach((itm) => {
    if (itm.order_item_id === id) {
      itm.box_items.forEach((i, index) => {
        i.qty_stem_flower = stem_flower[index] / 2;
      });
    }
  });
  orderStore.selectedOrder.order_details = newOrder.map(i => ({ ...i }));

  // Actualizo el objeto
  orderStore.updateOrderItem();
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

  // Actualizamos en el server la accion
  orderStore.updateOrderItem();

  };

// computed Properties
const isTwoQBSelected = computed(() => {
  let qb = orderStore.selectedOrder.order_details.filter(i => i.box_model === 'QB' && i.is_selected);
  return qb.length === 2;
});

const totalMargin = computed(() => {
  if (orderStore.selectedOrder === null) return 0;
  let total = 0;
  orderStore.selectedOrder.order_details.forEach(order_detail => {
    total += order_detail.box_items.reduce((acc, item) => {
      return acc + parseFloat(item.margin * parseFloat(item.qty_stem_flower));
    }, 0);
  });
  return total.toFixed(2);
});

const totalCost = computed(() => {
  if (orderStore.selectedOrder === null) return 0;
  let total = 0;
  orderStore.selectedOrder.order_details.forEach(order_detail => {
    total += order_detail.box_items.reduce((acc, item) => {
      return acc + (item.stem_cost_price * parseFloat(item.qty_stem_flower));
    }, 0);
  });
  return total.toFixed(2);
});

const totalBoxesQB = computed(() => {
  let total = 0;
  orderStore.newOrder.forEach(item => {
    total += item.box_model === 'QB' ? parseInt(item.quantity) : 0;
  });
  return total;
});

const totalBoxesHB = computed(() => {
  let total = 0;
  orderStore.newOrder.forEach(item => {
    total += item.box_model === 'HB' ? parseInt(item.quantity) : 0;
  });
  return total;
});

const totalStems = computed(() => {
  let total = 0;
  orderStore.newOrder.forEach(item => {
    total += item.tot_stem_flower;
  });
  return total;
});

const orderHaveCeroItem = computed(() => {
  for (const order of orderStore.newOrder) {
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

    if (orderStore.selectedCustomer === null) {
      exceedLimitMessage.value = 'Debe seleccionar un cliente';
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

</script>

<template>
  <div class="container-fluid p-3">
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
      <div class="col-12 bg-gray-600 bg-gradient rounded-1 shadow-sm p-2 text-white">
        <div class="row">
          <div class="col text-center">
            <h5>
              {{ orderStore.selectedOrder.order.partner.name }}
            </h5>
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
    <div class="row pb-2 pt-2 text-end">
      <div class="col">
        <button class="btn btn-sm btn-default" v-if="isTwoQBSelected" @click="mergeQB">
          <IconLayersIntersect2 size="20" stroke="1.5" />
          Unificar a HB
        </button>
      </div>
    </div>
    <div class="row p-1 text-white ">
      <div class="col-1 fw-bold fs-6 border-end bg-kosmo-green text-center">Cant</div>
      <div class="col-1 fw-bold fs-6 border-end bg-kosmo-green text-center">Mdl</div>
      <div class="col-1 fw-bold fs-6 border-end bg-kosmo-green text-center">Tl/Cj</div>
      <div class="col-2 fw-bold fs-6 border-end bg-kosmo-green text-center">Proveedor</div>
      <div class="col-6 fw-bold fs-6 border-end bg-sky-500">
        <div class="d-flex">
          <div class="flex-grow-1" style="flex: 0 0 50%; border-right: 1px solid #ddd; text-align: center;">
            Variedad
          </div>
          <div class="flex-grow-1" style="flex: 0 0 16.666%; border-right: 1px solid #ddd; text-align: center;">
            Tallos
          </div>
          <div class="flex-grow-1" style="flex: 0 0 16.666%; border-right: 1px solid #ddd; text-align: center;">
            Costo
          </div>
          <div class="flex-grow-1" style="flex: 0 0 16.666%; text-align: center;">
            Margen
          </div>
        </div>
      </div>
      <div class="col-1 fw-bold fs-6 bg-kosmo-green">C/USD</div>
    </div>
    <div v-for="item, idx in orderStore.selectedOrder.order_details" :key="item.order_item_id" class="row mb-1 border my-hover-2"
      :class="{ 'bg-gray': idx % 2 === 0 }">
      <div class="col-1 border-end d-flex gap-1 justify-content-between align-items-center">
        <IconTrash size="30" stroke="1.5" :class="item.confirm_delete ? 'text-danger' : 'text-dark'"
          @click="deleteOrderItem(item)" />
        <input type="number" step="1" class="form-control form-control-sm text-end" v-model="item.quantity"
          @change="(event) => delimitedNumber(event, item)" @focus="selectText"
          @keydown="event => handleKeydown(event, '.form-control-sm')" />
      </div>
      <div class="col-1 text-end border-end d-flex align-items-end gap-2 ">
        {{ item.box_model }}
        <span>/</span>
        <IconSitemap size="20" stroke="1.5" @click="splitHB(item)" v-if="item.box_model === 'HB'" />
        <input type="checkbox" v-model="item.is_selected" v-if="item.box_model === 'QB'" />
      </div>
      <div class="col-1 text-end border-end d-flex align-items-end justify-content-end">{{ item.tot_stem_flower }}</div>
      <div class="col-2 d-flex align-items-end">
        <small>
          {{ item.partner.partner.name }}
        </small>
      </div>
      <div class="col-6">
        <div v-for="product in item.box_items" :key="product.id" class="d-flex justify-content-between">
          <span class="border-end text-end w-50 pe-2">
            {{ product.product_name }} {{ product.product_variety }}
          </span>
          <span class="border-end text-end w-10 pe-2">
            {{ product.length }} cm
          </span>
          <span class="border-end text-end w-20 pe-2">
            <input type="number" step="1" class="form-control form-control-sm text-end my-input"
              v-model="product.qty_stem_flower" @focus="selectText"
              @keydown="event => handleKeydown(event, '.my-input')" @change="formatInteger"
              :class="{ 'bg-red-200': parseInt(product.qty_stem_flower) <= 0 }" />
          </span>
          <span class="border-end text-end w-20 pe-2">
            <input type="number" step="0.01" class="form-control form-control-sm text-end my-input-2"
              v-model="product.stem_cost_price" @focus="selectText"
              @keydown="event => handleKeydown(event, '.my-input-2')" @change="formatNumber"
              :class="{ 'bg-red-200': parseFloat(product.stem_cost_price) <= 0.00 }" />
          </span>
          <span class="border-end text-end w-20 pe-2">
            <input type="number" step="0.01" class="form-control form-control-sm text-end my-input-3"
              v-model="product.margin" @focus="selectText" @keydown="event => handleKeydown(event, '.my-input-3')"
              @change="formatNumber" :class="{ 'bg-red-200': parseFloat(product.margin) <= 0.00 }" />
          </span>
        </div>
      </div>
      <div class="col-1 fw-semibold d-flex align-items-end justify-content-end">
        {{ calcTotalByItem(item) }}
      </div>
    </div>
    <div class="row">
      <div class="col-3">
        <div class="row shadow-sm p-2">
          <div class="col-9 fs-5 text-start text-end">{{ totalBoxesHB }}</div>
          <div class="col-3 fs-5 text-end">HB's:</div>
          <div class="col-9 fs-5 text-start text-end">{{ totalBoxesQB }}</div>
          <div class="col-3 fs-5 text-end">QB's:</div>
          <div class="col-9 fs-5 text-start text-end">{{ totalStems }}</div>
          <div class="col-3 fs-5 text-end">Tallos:</div>
        </div>
      </div>
      <div class="col-4 offset-5">
        <div class="row bg-gray-200 bg-gradient rounded-1 shadow-sm p-2">
          <div class="col-7 text-end border-end fs-5 text-lime-600">Costo:</div>
          <div class="col-5 fs-5 text-lime-600 text-end">{{ totalCost }}</div>
          <div class="col-7 text-end border-end fs-5 text-lime-600">Margen:</div>
          <div class="col-5 fs-5 text-lime-600 text-end">{{ totalMargin }}</div>
          <div class="col-7 text-end border-end fs-5 text-lime-600">Total Pedido:</div>
          <div class="col-5 fs-5 text-lime-600 text-end">
            {{  (parseFloat(totalMargin) + parseFloat(totalCost)).toFixed(2) }}
          </div>
        </div>
      </div>
    </div>
    <div class="row mt-3 border-top pt-3">
      <div class="col text-end d-flex gap-3 justify-content-between">
        .
        <button type="button" class="btn btn-sm btn-default text-danger" @click="cancelOrder">
          <IconBan size="20" stroke="1.5" />
          Cancelar Pedido
        </button>
        <span class="ps-4 pe-4"></span>
        <button type="button" class="btn btn-sm btn-default" @click="orderStore.showViews('listOrders')">
          <IconArrowLeft size="20" stroke="1.5" />
          Volver al Listado
        </button>
        <button type="button" class="btn btn-sm btn-default" @click="createOrder" :disabled="orderHaveCeroItem">
          <IconCheckbox size="20" stroke="1.5" />
          Generar Factura
        </button>
      </div>
    </div>
  </div>
</template>
<style scoped>
input[type="checkbox"] {
  width: 15px;
  height: 15px;
}

.my-input,
.my-input-2,
.my-input-3 {
  border: 1px solid #ccc;
  border-radius: 2px;
  text-align: right;
}

</style>