<script setup>
import {ref, watch ,onMounted } from 'vue';
import SingleOrderCustomer from './SingleOrderCustomer.vue';
import SingleOrderSuplier from './SingleOrderSuplier.vue';
import { 
    IconShoppingCartUp,
    IconShoppingCartDown,
} from '@tabler/icons-vue';

const tabSelected = ref({
    orders: true,
    purchases: false,
});


</script>
<template>
    <div class="row m-3 bg-gray-100">
<nav>
  <div class="nav nav-tabs" id="nav-tab" role="tablist">
    <button class="nav-link active" id="nav-home-tab" data-bs-toggle="tab" data-bs-target="#nav-home" type="button" role="tab" aria-controls="nav-home" aria-selected="true">
        <IconShoppingCartUp  stroke ="1.5" size="20" />
        Orden de Venta
        <span class="badge bg-secondary">Pendiente</span>
    </button>
    <button class="nav-link" id="nav-profile-tab" data-bs-toggle="tab" data-bs-target="#nav-profile" type="button" role="tab" aria-controls="nav-profile" aria-selected="false">
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
    <SingleOrderCustomer/>
  </div>
  <div class="tab-pane fade" id="nav-profile" role="tabpanel" aria-labelledby="nav-profile-tab">
    <SingleOrderSuplier/>
  </div>
</div>
    </div>
</template>