<script setup>
import { computed, onMounted, onUnmounted, watch, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useOrdersStore } from '@/stores/ordersStore.js';
import { useBaseStore } from '@/stores/baseStore.js';
import { usePurchaseStore } from  '@/stores/purcharsesStore.js';
import SingleOrderCustomer from '@/components/Sotcks/SingleOrderCustomer.vue';
import SingleOrderSuplier from '@/components/Sotcks/SingleOrderSuplier.vue';
import PurchaseOrdersList from '@/components/Sotcks/PurchaseOrdersList.vue';
import { 
  IconShoppingCartUp,
  IconShoppingCartDown,
  IconArrowLeft 
} from '@tabler/icons-vue';
import Loader from '@/components/Sotcks/Loader.vue';
import SideBar from '@/components/Sotcks/SideBar.vue';

const baseStore = useBaseStore();
const orderStore = useOrdersStore();
const purchaseStore = usePurchaseStore();
const route = useRoute();

orderStore.selectOrder(route.params.id);
const selectedTab = ref('customer');

// Computed
const isAllLoaded = computed(() => {
    return baseStore.stagesLoaded === 2;
})


const isPurchOrderSelected = computed(() => {
    return Boolean(Object.keys(purchaseStore.purcharses_by_order).length);
});

const precentConfirmed = computed(() => {
    let total = purchaseStore.purcharses_by_order.length;
    if (total) {
        let confirmed = purchaseStore.purcharses_by_order.filter((item) => item.status === 'CONFIRMADO').length;
        return `${(confirmed * 100) / total}%`;
    }
    return '0%';
});

// Mounted
onMounted(()=>{
  baseStore.stagesLoaded = 0;
  orderStore.loadOrders(baseStore);
  purchaseStore.getOrdersByCustomerOrder(route.params.id, baseStore);
});

onUnmounted(()=>{
  purchaseStore.purcharses_by_order = [];
});

// Watch
watch(()=> baseStore.stagesLoaded, (newValue) => {
  if (newValue === 2) {
    console.log('Seleccionado Pedido Activo')
    orderStore.selectOrder(route.params.id);
  }
});

</script>
<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-2">
        <SideBar />
      </div>
      <div class="col">
  <div class="row" v-if="!isAllLoaded">
    <div class="col text-center">
      <Loader />
      <h6 class="text-blue-600">
        {{ baseStore.stagesLoaded }} / 2
      </h6>
    </div>
  </div>
<div class="row m-3 bg-gray-100" v-else>
<nav>
  <div class="nav nav-tabs" id="nav-tab" role="tablist">
    <button class="nav-link border p-2 active d-flex gap-3" id="nav-home-tab" data-bs-toggle="tab" data-bs-target="#nav-home" type="button" role="tab" aria-controls="nav-home" aria-selected="true">
        <IconShoppingCartUp  stroke ="1.5" size="20" />
        Orden de Venta
    </button>
    <button class="nav-link border p-2 d-flex gap-3" id="nav-profile-tab"  data-bs-toggle="tab" data-bs-target="#nav-profile" type="button" role="tab" aria-controls="nav-profile" aria-selected="false">
        <IconShoppingCartDown  stroke ="1.5" size="20" />
        Ordenes de Compra
    </button>
  </div>
</nav>
<div class="tab-content" id="nav-tabContent">
  <div class="tab-pane fade show active" id="nav-home" role="tabpanel" aria-labelledby="nav-home-tab">
    <SingleOrderCustomer v-if="isAllLoaded" :key="route.params.id"/>
  </div>
  <div class="tab-pane fade" id="nav-profile" role="tabpanel" aria-labelledby="nav-profile-tab">
    <div class="d-flex">
      <div class="bg-transparent pt-5 flex-shrink-0">
        <PurchaseOrdersList/>  
      </div>
      <div class="flex-grow-1 ps-2">
        <SingleOrderSuplier v-if="isPurchOrderSelected" :key="purchaseStore.selectedPurchase"/>
      </div>
    </div>
  </div>
</div>
    </div>
    <div class="row">
      <div class="col d-flex justify-content-end">
        <button @click="$router.go(-1)" class="btn btn-primary">
          <IconArrowLeft stroke ="1.5" size="20" />
      Volver a Compras
    </button>
      </div>
    </div>
  </div>
  </div>
  </div>
</template>