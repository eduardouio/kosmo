<script setup>
import { computed, onMounted, onUnmounted, watch, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useBaseStore } from '@/stores/base';
import SingleOrderCustomer from '@/components/SingleOrderCustomer.vue';
import SingleOrderSuplier from '@/components/SingleOrderSuplier.vue';
import { usePurchaseStore } from  '@/stores/purcharses';
import { useOrdersStore } from '@/stores/orders';
import PurchaseOrdersList from '@/components/PurchaseOrdersList.vue';
import {  IconShoppingCartUp, IconShoppingCartDown, IconArrowLeft } from '@tabler/icons-vue';
import Loader from '@/components/Loader.vue';

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
  <div>
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
    <button class="nav-link border p-3 active bg-blue-100" id="nav-home-tab" data-bs-toggle="tab" data-bs-target="#nav-home" type="button" role="tab" aria-controls="nav-home" aria-selected="true">
        <IconShoppingCartUp  stroke ="1.5" size="20" />
        Orden de Venta
        <span class="badge bg-secondary">Pendiente</span>
    </button>
    <button class="nav-link border p-3 bg-orange-100" id="nav-profile-tab"  data-bs-toggle="tab" data-bs-target="#nav-profile" type="button" role="tab" aria-controls="nav-profile" aria-selected="false">
        <IconShoppingCartDown  stroke ="1.5" size="20" />
        Ordenes de Compra
        <span class="badge bg-secondary">
            0/2
        </span>
    </button>
  </div>
</nav>
<div class="tab-content" id="nav-tabContent">
  <div class="tab-pane fade show active" id="nav-home" role="tabpanel" aria-labelledby="nav-home-tab">
  <SingleOrderCustomer v-if="isAllLoaded" :key="route.params.id"/>
  </div>
  <div class="tab-pane fade" id="nav-profile" role="tabpanel" aria-labelledby="nav-profile-tab">
    <PurchaseOrdersList/>
    <SingleOrderSuplier v-if="isPurchOrderSelected" :key="purchaseStore.selectedPurchase"/>
  </div>
</div>
    </div>
    <div class="row">
      <div class="col d-flex justify-content-end">
        <button @click="$router.go(-1)" class="btn btn-default btn-sm">
          <IconArrowLeft stroke ="1.5" size="20" />
      Volver a Listado
    </button>
      </div>
    </div>
  </div>
</template>