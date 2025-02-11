<script setup>
import { defineEmits, ref, computed, onMounted } from 'vue';
import DataTable from 'datatables.net-vue3';
import DataTablesCore from 'datatables.net';
import { usePurchaseStore } from '@/stores/purcharses';

// Variables
const purchasesStore = usePurchaseStore();
DataTable.use(DataTablesCore);

// Datos computados para extraer solo las órdenes
const my_order = computed(() => {
  return purchasesStore.purcharses_by_order.filter(i => i.is_selected)
});

</script>

<template>
<div>
  {{ my_order }}
</div>
</template>

<style>
.dt-search {
  float: right;
  padding-top: 1rem;
  padding-bottom: 0.5rem;
}
</style>
