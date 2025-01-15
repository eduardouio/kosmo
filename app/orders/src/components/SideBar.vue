<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router';
import { 
    IconCheckbox, IconSquare, IconChevronCompactRight, IconFilterOff
} from '@tabler/icons-vue';
import { useStockStore } from '@/stores/stock';
import { useBaseStore } from '@/stores/base';
import { IconEye } from '@tabler/icons-vue';

const stockStore = useStockStore();
const baseStore = useBaseStore();
const isLoading = ref(true);
const route = useRoute();


const showAllSuppliers = ref(true);
const showAllColors = ref(true);
const showAllStock = ref(true);

const showAllStockSwitch = () => {
    showAllStock.value = !showAllStock.value;
    stockStore.selectAllSuppliers(showAllStock.value);
    stockStore.selectAllColors(showAllStock.value);
    stockStore.filterCategories();
    showAllSuppliers.value = showAllStock.value;
    showAllColors.value = showAllStock.value; 
};

const getClass = (item) => {
    let color = item.name;
    if(color === null | color === undefined | color === '' | color === ' ') {
        return baseStore.bgColor.OTRO;
    }
    
    if (item.is_selected) {
        if(color in baseStore.bgColor) {
            return baseStore.bgColor[color];
        } else {
            return baseStore.bgColor.OTRO;
        }    
    }
    return 'bg-gray-200 text-gray-500';    
};


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
        <router-link to="/import/" class="list-group-item hover-opacity" :class="{'bg-gray-500 text-gray-100': route.path === '/import'}">
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
        <router-link to="/customer-orders/" class="list-group-item hover-opacity">
            <div class="rounded-1 p-0 fw-semibold">
                Pedidos de Clientes
                <IconChevronCompactRight size="20" stroke="1.5" class="float-end" />
            </div>
        </router-link>
        <!--
        <router-link to="/" class="list-group-item hover-opacity">
            <div class="rounded-1 p-0 fw-semibold">
                Compras a Proveedor
                <IconChevronCompactRight size="20" stroke="1.5" class="float-end" />
            </div>
        </router-link>
        -->
    </div>
    <div v-if="route.path === '/'" class="mt-4">
    <div v-if="!isLoading">
        <div class="text-center mt-2 mb-2">
            <button @click="showAllStockSwitch" class="btn btn-sm btn-default">
                <span v-if="showAllStock">
                    <IconFilterOff size="20" stroke="1.5"/> Quitar Filtros
                </span>
                <span v-else>
                    <IconEye size="20" stroke="1.5" /> Ver Todo El Stock
                </span>
            </button>
        </div>
    <div class="text-center ms-1 me-1 fw-semibold p-1 bg-gray-100 mb-1">
        <div class="d-flex gap-3 justify-content-between">
            <span>
                PROVEEDORES
            </span>
            <section class="d-flex justify-content-between gap-3">
            <span class="text-danger" @click="stockStore.selectAllSuppliers(false);showAllSuppliers=!showAllSuppliers" v-if="showAllSuppliers">
                <small>Desmarcar</small>
                <IconSquare size="20" stroke="1.5" />
            </span>
            <span class="text-success" @click="stockStore.selectAllSuppliers(true);showAllSuppliers=!showAllSuppliers" v-else>
                <small>Marcar</small>
                <IconCheckbox size="20" stroke="1.5" />
            </span>
        </section>
        </div>
    </div>
        <ul class="list-group rounded-0">
            <li v-for="supplier in stockStore.suppliers" :key="supplier.id" class="list-group-item p-1" :class="{'bg-gray-100': supplier.is_selected}" @click="supplier.is_selected = !supplier.is_selected;stockStore.filterCategories()">
                <IconCheckbox size="20" stroke="1.5" class="float-start" v-if="supplier.is_selected"/>
                <span class="ps-3" :class="{'fw-semibold': supplier.is_selected}">
                    {{ supplier.name }}
                </span>
            </li>
        </ul>
    </div>
    <div v-if="!isLoading" class="mt-4">
    <div class="text-center ms-1 me-1 fw-semibold text-slate-600 p-1 bg-gray-100 mb-1 mt-2">
        <div class="d-flex justify-content-between  gap-3">
            <span>
                COLORES
            </span>
            <section class="d-flex justify-content-between gap-3">
            <span class="text-danger" @click="stockStore.selectAllColors(false);showAllColors=!showAllColors" v-if="showAllColors">
                <small>Desmarcar</small>
                <IconSquare size="20" stroke="1.5" />
            </span>
            <span class="text-success" @click="stockStore.selectAllColors(true)" v-else>
                <small>Marcar</small>
                <IconCheckbox size="20" stroke="1.5" />
            </span>
        </section>
        </div>
    </div>
    <hr />
        <section class="d-flex flex-wrap gap-2">
            <span v-for="item in stockStore.colors" :class="getClass(item)" class="rounded-1 p-1" @click="item.is_selected = !item.is_selected;stockStore.filterCategories()">
                <IconCheckbox size="15" stroke="1.5" v-if="item.is_selected"/>
                {{ item.name }}
            </span>
        </section>
    </div>
    
</div>
</template>

<style scoped>
.hover-opacity:hover {
  opacity: 0.8;
  background-color: rgba(0, 0, 0, 0.1);
}
</style>
