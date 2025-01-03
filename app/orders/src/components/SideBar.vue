<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router';
import { IconCheckbox, IconSquare, IconChevronCompactRight } from '@tabler/icons-vue';
import { useStockStore } from '@/stores/stock';
import { useBaseStore } from '@/stores/base';

const stockStore = useStockStore();
const baseStore = useBaseStore();
const isLoading = ref(true);
const route = useRoute();

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
        <router-link to="/import" class="list-group-item hover-opacity" :class="{'bg-gray-500 text-gray-100': route.path === '/import'}">
            <div class="b rounded-1 p-0 fw-semibold ">
                Importar Disponibilidad
                <IconChevronCompactRight size="20" stroke="1.5" class="float-end" />
            </div>
        </router-link>
        <router-link to="/" class="list-group-item hover-opacity" :class="{'bg-gray-500 text-gray-100': route.path === '/'}">
            <div class="b rounded-1 p-0 fw-semibold">
                Disponibilidad Actual
                <IconChevronCompactRight size="20" stroke="1.5" class="float-end" />
            </div>
        </router-link>

        <router-link to="/" class="list-group-item hover-opacity">
            <div class="rounded-1 p-0 fw-semibold">
                Pedidos de Clientes
                <IconChevronCompactRight size="20" stroke="1.5" class="float-end" />
            </div>
        </router-link>
        <router-link to="/" class="list-group-item hover-opacity">
            <div class="rounded-1 p-0 fw-semibold">
                Compras a Proveedor
                <IconChevronCompactRight size="20" stroke="1.5" class="float-end" />
            </div>
        </router-link>
    </div>
    <div v-if="!isLoading">
    <div class="text-center ms-1 me-1 fw-semibold p-1 bg-gray-200 mb-1">
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
        <ul class="list-group rounded-0">
            <li v-for="supplier in stockStore.suppliers" :key="supplier.id" class="list-group-item" :class="{'bg-lime-200': supplier.is_selected}" @click="supplier.is_selected = !supplier.is_selected;stockStore.filterBySupplier()">
                <IconCheckbox size="20" stroke="1.5" class="float-start" v-if="supplier.is_selected"/>
                <span class="ps-3" :class="{'fw-semibold': supplier.is_selected}">
                    {{ supplier.name }}
                </span>
            </li>
        </ul>
    </div>
    <div v-if="!isLoading">
    <div class="text-center ms-1 me-1 fw-semibold text-slate-600 p-1 bg-gray-200 mb-1 mt-2">
        <div class="d-flex gap-3 justify-content-between">
            <span class="text-success" @click="stockStore.selectAllSuppliers(true);stockStore.filterBySupplier()">
                <IconCheckbox size="20" stroke="1.5" />
            </span>
            <span>
                COLORES
            </span>
            <span class="text-danger" @click="stockStore.selectAllSuppliers(false);stockStore.filterBySupplier()">
                <IconSquare size="20" stroke="1.5" />
            </span>
        </div>
    </div>
    <hr />
        <section class="d-flex flex-wrap gap-2">
            <span class="badge bg-yellow-300 text-dark border-gray-400">
                <IconCheckbox size="15" stroke="1.5" />
                Amarillo
            </span>
            <span class="badge bg-blue-300 text-dark border-gray-400">
                <IconCheckbox size="15" stroke="1.5" />
                Azul
            </span>
            <span class="badge bg-red-300 text-dark border-gray-400">
                <IconCheckbox size="15" stroke="1.5" />
                Rojo
            </span>
            <span class="badge bg-green-300 text-dark border-gray-400">
                <IconCheckbox size="15" stroke="1.5" />
                Verde
            </span>
            <span class="badge bg-gray-300 text-dark border-gray-400">
                <IconCheckbox size="15" stroke="1.5" />
                Gris
            </span>
            <span class="badge bg-purple-300 text-dark border-gray-400">
                <IconCheckbox size="15" stroke="1.5" />
                Morado
            </span>
            <span class="badge bg-orange-300 text-dark border-gray-400">
                <IconCheckbox size="15" stroke="1.5" />
                Naranja
            </span>
        
        </section>
    </div>

</template>

<style scoped>
.hover-opacity:hover {
  opacity: 0.8;
  background-color: rgba(0, 0, 0, 0.1);
}
</style>
