<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router';
import { useStockStore } from '@/stores/stock';
import { useBaseStore } from '@/stores/base';
import { 
    IconCheckbox,
    IconSquare,
    IconChevronCompactRight,
    IconFilterOff,
    IconFilter
} from '@tabler/icons-vue';

const stockStore = useStockStore();
const baseStore = useBaseStore();
const route = useRoute();


const showAllSuppliers = ref(true);
const showAllColors = ref(true);
const showAllStock = ref(true);
const showAllLengths = ref(true);


// METHODS

const showAllStockSwitch = () => {
    showAllStock.value = !showAllStock.value;
    stockStore.selectAllSuppliers(showAllStock.value);
    stockStore.selectAllColors(showAllStock.value);
    stockStore.selectAllLengths(showAllStock.value);
    stockStore.filterCategories();
    showAllSuppliers.value = showAllStock.value;
    showAllColors.value = showAllStock.value;
    showAllLengths.value = showAllStock.value;
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

const resetStagesLoaded = () => {
    baseStore.stagesLoaded = 0;
};


</script>
<template>
    <div class="p-2 list-group rounded-0">
        <router-link to="/import/" class="list-group-item hover-opacity" :class="{'bg-gray-500 text-gray-100': route.path === '/import'}" @click="resetStagesLoaded()">
            <div class="b rounded-1 p-0 fw-semibold ">
                Importar Disponibilidad
                <IconChevronCompactRight size="20" stroke="1.5" class="float-end" />
            </div>
        </router-link>
        <router-link to="/" class="list-group-item hover-opacity" :class="{'bg-gray-500 text-gray-100': route.path === '/'}" @click="resetStagesLoaded()">
            <div class="b rounded-1 p-0 fw-semibold">
                Disponibilidad Actual
                <IconChevronCompactRight size="20" stroke="1.5" class="float-end" />
            </div>
        </router-link>
        <router-link to="/customer-orders/" class="list-group-item hover-opacity" @click="resetStagesLoaded()">
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
    <div v-if="route.path === '/' && baseStore.isLoading" class="mt-4">
    <div class="text-center border-bottom">
        <small class="text-muted">
            Filtros de Stock
        </small>
    </div>
    <div>
        <div class="text-center mt-4 mb-4">
            <button @click="showAllStockSwitch" class="btn btn-sm bg-gray-200 btn-block w-100 border shadow">
                <span v-if="showAllStock">
                    <IconFilterOff size="20" stroke="1.5"/> Desmarcar Todos
                </span>
                <span v-else>
                    <IconFilter size="20" stroke="1.5" /> Marcar Todos
                </span>
            </button>
        </div>
    <div class="text-center ms-1 me-1 fw-semibold p-1 mb-3 bg-yellow-200 mb-1">
        <div class="d-flex gap-3 justify-content-between">
            <span>
                <IconFilter size="20" stroke="1.5" /> PROVEEDORES
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
                <IconSquare size="15" stroke="1.5" v-else class="text-danger"/>
                <span class="ps-3" :class="{'fw-semibold': supplier.is_selected}">
                    {{ supplier.name }}
                </span>
            </li>
        </ul>
    </div>
    <div class="mt-4">
    <div class="text-center ms-1 me-1 fw-semibold text-slate-600 p-1 bg-lime-200 mb-1 mt-2">
        <div class="d-flex justify-content-between  gap-3">
            <span>
                <IconFilter size="20" stroke="1.5" /> COLORES
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
                <IconSquare size="15" stroke="1.5" v-else class="text-danger"/>
                {{ item.name }}
            </span>
        </section>
    </div>
    <div class="mt-4">
    <div class="text-center ms-1 me-1 fw-semibold text-slate-600 p-1 bg-cyan-200 mb-1 mt-2">
        <div class="d-flex justify-content-between  gap-3">
            <span>
                <IconFilter size="20" stroke="1.5" /> LONGITUD DE TALLO
            </span>
            <section class="d-flex justify-content-between gap-3">
            <span class="text-danger" @click="stockStore.selectAllLengths(false);showAllLengths=!showAllLengths" v-if="showAllLengths">
                <small>Desmarcar</small>
                <IconSquare size="20" stroke="1.5" />
            </span>
            <span class="text-success" @click="stockStore.selectAllLengths(true)" v-else>
                <small>Marcar</small>
                <IconCheckbox size="20" stroke="1.5" />
            </span>
        </section>
        </div>
    </div>
    <hr />
        <section class="d-flex flex-wrap gap-2">
            <span v-for="item in stockStore.lengths" :class="getClass(item)" class="rounded-1 p-1" @click="item.is_selected = !item.is_selected;stockStore.filterCategories()">
                <IconCheckbox size="15" stroke="1.5" v-if="item.is_selected"/>
                <IconSquare size="15" stroke="1.5" v-else class="text-danger"/>
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
