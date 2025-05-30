<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useOrdersStore } from '@/stores/ordersStore.js';
import { useBaseStore } from '@/stores/baseStore.js';
import { 
  IconCheckbox,
  IconX,
} from '@tabler/icons-vue';

const ordersStore = useOrdersStore();
const baseStore = useBaseStore();
const confirmDelete = ref(false);
const exceedLimit = ref(false);
const deleteMessage = ref('El item marcado será elimnado del pedido, click nuevamente para confirmar');
const exceedLimitMessage = ref();
const router = useRouter();

// Methods
const calcTotalByItem = (item)=>{ 
  let total = 0;
  let items = item.box_items.map(item => item)
  total = items.reduce((acc, item) => {
    return acc + ((item.stem_cost_price + parseFloat(item.margin)) * parseFloat(item.qty_stem_flower));
  }, 0) * parseFloat(item.quantity);
  return total.toFixed(2);
};

const delimitedNumber = (event, item) => {
  exceedLimit.value = false;
  let value = parseInt(event.target.value);
  let maxValue = ordersStore.limitsNewOrder.filter(i=>i.stock_detail_id === item.stock_detail_id).map(i=>i.quantity);
  if (value > maxValue) {
    item.quantity = maxValue;
    exceedLimitMessage.value = `La cantidad máxima permitida para este item es de ${maxValue}`;
    exceedLimit.value = true;
  }
};

const selectText = (event) => {
    event.target.select();
}

const createOrder = () => {
  baseStore.stagesLoaded = 0;
  router.push('/customer-orders/');

} 

const totalOrder = computed(() => {
  let total = 0;
  ordersStore.newOrder.forEach(item => {
    let items = item.box_items.map(item => item)
    total += items.reduce((acc, item) => {
      return acc + ((item.stem_cost_price + parseFloat(item.margin)) * parseFloat(item.qty_stem_flower));
    }, 0) * parseFloat(item.quantity);
  });
  return total.toFixed(2);
});

const totalMargin = computed(() => {
  let total = 0;
  ordersStore.newOrder.forEach(item => {
    let items = item.box_items.map(item => item)
    total += items.reduce((acc, itm) => {
      return acc + parseFloat(itm.margin * parseFloat(itm.qty_stem_flower));
    }, 0) * parseFloat(item.quantity);
  });
  return total.toFixed(2);
});


const totalCost = computed(() => {
  let total = 0;
  ordersStore.newOrder.forEach(item => {
    let items = item.box_items.map(item => item)
    total += items.reduce((acc, item) => {
      return acc + (item.stem_cost_price * parseFloat(item.qty_stem_flower));
    }, 0) * parseFloat(item.quantity);
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

const totalStems = computed(() => {
  let total = 0;
  ordersStore.newOrder.forEach(item => {
    total += (item.tot_stem_flower * item.quantity);
  });
  return total;
});


</script>
<template>
  <div class="modal fade modal-xl" id="orderPreviewModal" tabindex="-1" aria-labelledby="orderPreviewModal" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content" v-if="ordersStore.newOrder.length">
        <div class="modal-header bg-kosmo-primary p-1 text-white">
          <span class="modal-title fs-6 ps-3" id="orderPreviewModal">
            Vista Preeliminar de Pedido
          </span>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="row p-1 mb-1">
            <div class="col-12 bg-gray-200 bg-gradient rounded-1 shadow-sm p-2" v-if="ordersStore.selectedCustomer">
              <div class="row">
                <div class="col-1 text-end">ID:</div>
                <div class="col-1">{{ ordersStore.selectedCustomer.business_tax_id }}</div>
                <div class="col-1 text-end">Dir:</div>
                <div class="col-6">
                  {{ ordersStore.selectedCustomer.address }}
                  {{ ordersStore.selectedCustomer.country }}/{{ ordersStore.selectedCustomer.city  }}
                </div>
                <div class="col-1 text-end">Skype:</div>
                <div class="col-2">{{ ordersStore.selectedCustomer.skype }}</div>
              </div>
              <div class="row pt-1">
                <div class="col-1 text-end">Contacto:</div>
                <div class="col-8 d-flex gap-2">
                  <span>{{ ordersStore.selectedCustomer.contact.name }}</span> 
                  <span >{{  ordersStore.selectedCustomer.contact.email  }}</span>
                  <span >{{ ordersStore.selectedCustomer.contact.phone }}</span>
                  <span class="badge bg-green-600">{{  ordersStore.selectedCustomer.contact.contact_type }}</span>
                </div>
                <div class="col-1 text-end fw-semibold">
                  Consolida:
                </div>
                <div class="col-2">
                     {{ ordersStore.selectedCustomer.consolidate ? 'Si' : 'No' }}
                </div>
              </div>
            </div>
          </div>
          <div class="row bg-light text-center py-2 rounded-1 bg-gray-300 border-gray-400">
            <div class="col-1 fw-bold fs-6 border-end bg-kosmo-green text-white">Cant</div>
            <div class="col-1 fw-bold fs-6 border-end bg-kosmo-green text-white">Mdl</div>
            <div class="col-1 fw-bold fs-6 border-end bg-kosmo-green text-white">Tl</div>
            <div class="col-2 fw-bold fs-6 border-end bg-kosmo-green text-white">Proveedor</div>
            <div class="col-6 fw-bold fs-6 border-end bg-sky-500 text-white">
              <span class="d-flex justify-content-between">
                <span class="w-50 border-end text-center">Variedad</span>
                <span class="w-10 border-end text-center">CM</span>
                <span class="w-10 border-end text-center">Tall/C</span>
                <span class="w-10 border-end text-center">Cos</span>
                <span class="w-10">Margen</span>
              </span>
            </div>
            <div class="col-1 fw-bold fs-6 bg-kosmo-green text-white">C/USD</div>
          </div>
          <div class="row">
            <div class="col-12 text-center fs-6 fw-semibold text-warning" v-if="exceedLimit || confirmDelete">
              <span v-if="confirmDelete">
                {{  deleteMessage }}
              </span>
              <span v-if="exceedLimit">
                {{ exceedLimitMessage }}
              </span>
            </div>
          </div>
          <div v-for="item,idx in ordersStore.newOrder" :key="item.id" class="row mb-1 border my-hover-2" :class="{'bg-gray': idx % 2 === 0}">
            <div class="col-1 border-end d-flex gap-1 justify-content-between align-items-center">
              <input 
                type="number"
                step="1"
                class="form-control form-control-sm text-end"
                v-model="item.quantity"
                @change="(event) => delimitedNumber(event, item)"
                @focus="selectText"
                />
            </div>
            <div class="col-1 text-center border-end d-flex align-items-center">
              {{ item.box_model }}
            </div>
            <div class="col-1 text-end border-end d-flex align-items-center justify-content-end">{{ item.tot_stem_flower * item.quantity}}</div>
            <div class="col-2 d-flex align-items-end">
              <small>
                {{ item.partner.name }}
              </small>
            </div>
            <div class="col-6">
              <div v-for="product in item.box_items" :key="product.id" class="d-flex justify-content-between">
                <span class="border-end text-end w-50 pe-2 d-flex align-items-center">
                  {{ product.product_name }} {{ product.product_variety }}
                </span>
                <span class="border-end text-end w-10 pe-2 d-flex align-items-center">
                  {{ product.length }} cm
                </span>
                <span class="border-end text-end w-10 pe-2 d-flex align-items-center">
                  {{ product.qty_stem_flower }}
                </span>
                <span class="border-end text-end w-10 pe-2">
                  {{ product.stem_cost_price.toFixed(2) }}
                </span>
                <span class="border-end text-end w-10 pe-2">
                  {{ product.margin }}
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
              <div class="col-5 fs-5 text-lime-600 text-end">{{ totalOrder }}</div>
        </div>
            </div>
          </div>
        </div>
        <div class="modal-footer bg-secondary bg-gradient p-1">
          <button type="button" class="btn btn-sm btn-default" data-bs-dismiss="modal">
            <IconX size="20" stroke="1.5"/>
            Cancelar  
          </button>
          <button type="button" class="btn btn-sm btn-default" data-bs-dismiss="modal" @click="createOrder">
            <IconCheckbox size="20" stroke="1.5"/>
            Crear Pedido
          </button>
        </div>
      </div>
    </div>
  </div>
</template>