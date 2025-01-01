<script setup>
import { useStockStore } from '@/stores/stock';
import { useBaseStore } from '@/stores/base';
import { ref, onMounted, watch } from 'vue'
import { IconCheckbox, IconSquare } from '@tabler/icons-vue';

const stockStore = useStockStore();
const baseStore = useBaseStore();
const isLoading = ref(true);

watch(
    () => baseStore.isLoading,
    (newValue) => {
        if (!newValue) {
            isLoading.value = false;
        }
    },
    { immediate: true }
);


</script>

<template>
    <div class="p-2 list-group rounded-0">
        <router-link to="/import" class="list-group-item hover-opacity">
            <div class="b rounded-1 p-1 text-end text-slate-600 fw-semibold ">
                Importar Disponibilidad
            </div>
        </router-link>
        <router-link to="/" class="list-group-item hover-opacity">
            <div class="b rounded-1 p-1 text-end text-slate-600 fw-semibold">
                Disponibilidad Actual
            </div>
        </router-link>

        <router-link to="/" class="list-group-item hover-opacity">
            <div class="rounded-1 p-1 text-end text-slate-600 fw-semibold">
                Pedidos de Clientes
            </div>
        </router-link>
        <router-link to="/" class="list-group-item hover-opacity">
            <div class="rounded-1 p-1 text-end text-slate-600 fw-semibold">
                Compras a Proveedor
            </div>
        </router-link>
    </div>
    <div v-if="!isLoading">
    <hr />
    <div class="text-center ms-1 me-1 fw-semibold text-slate-600">
        <div class="d-flex gap-3 justify-content-between">
            <span class="text-success" @click="stockStore.selectAllSuppliers(true);stockStore.filterBySupplier()">
                <IconCheckbox size="20" stroke="1.5" />
            </span>
            <span>
                PROVEEDORES
            </span>
            <span class="text-danger" @click="stockStore.selectAllSuppliers(false);stockStore.filterBySupplier()">
                <IconSquare size="20" stroke="1.5" />
            </span>
        </div>
    </div>
    <hr />
        <ul class="list-group rounded-0">
            <li v-for="supplier in stockStore.suppliers" :key="supplier.id" class="list-group-item" :class="{'bg-lime-200': supplier.is_selected}" @click="supplier.is_selected = !supplier.is_selected;stockStore.filterBySupplier()">
                <IconCheckbox size="20" stroke="1.5" class="float-start" v-if="supplier.is_selected"/>
                <span class="ps-3" :class="{'fw-semibold': supplier.is_selected}">
                    {{ supplier.name }}
                </span>
            </li>
        </ul>
    </div>


</template>

<style scoped>
.hover-opacity:hover {
  opacity: 0.8;
  background-color: rgba(0, 0, 0, 0.1);
}
</style>
