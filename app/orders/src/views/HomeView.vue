<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useStockStore } from '@/stores/stock';
import { useBaseStore } from '@/stores/base';
import ModalProduct from '@/components/ModalProduct.vue';
import ModalSuplier from '@/components/ModalSuplier.vue';
import ModalShareStock from '@/components/ModalShareStock.vue';
import Loader from '@/components/Loader.vue';
import {
    IconCheckbox,
    IconSquare,
    IconEye,
    IconShare,
    IconLockOpen2,
    IconLock,
    IconCurrencyDollar,
    IconShoppingCart,
    IconSettings,
    IconTrash,
} from '@tabler/icons-vue';

// VARIABLES
const stockStore = useStockStore();
const baseStore = useBaseStore();
const colors = ref(null);
const generalIndicators = ref({});                        
const productSelected = ref(null);
const suplierSelected = ref(null);
const querySearch = ref('');
const buttonsVisibility = ref({
    share: false,
    all: true,
    none: false,
    cost: false,
    margin: false,
    order: false,
    delete: false,
});
const confirmDelete = ref(false);


// METHODS

const deleteSelected = () => {
    if (!confirmDelete.value) {
        confirmDelete.value = true;
        return;
    }
    stockStore.deleteSelected();
    setVibilityButtons();
    calcIndicators();
    confirmDelete.value = false;
}

const setVibilityButtons = () => {
    let haveSelected = stockStore.stock.some(item => item.is_selected);
    stockStore.stockToText();
    if (haveSelected) {
        buttonsVisibility.value = {
            share: true,
            all: false,
            none: true,
            cost: true,
            margin: true,
            order: true,
            delete: true,
        }
        return;
    }
    buttonsVisibility.value = {
        share: false,
        all: true,
        none: false,
        cost: false,
        margin: false,
        order: false,
        delete: false,
    }
    confirmDelete.value = false;
}


const selectText = (event) => {
    event.target.select();
}

const calcIndicators = () => {
    generalIndicators.value = {
        total_QB: 0,
        total_HB: 0,
        total_stems: 0,
        total_suppliers: [],
    }

    if (!stockStore.stock || stockStore.stock.length === 0) {
        return;
    }

    stockStore.stock.forEach(item => {
        console.log(typeof(item.quantity));
        generalIndicators.value.total_HB += item.box_model === 'HB' ? item.quantity : 0;
        generalIndicators.value.total_QB += item.box_model === 'QB' ? item.quantity : 0;
        generalIndicators.value.total_stems += item.box_items.reduce((acc, box) => acc + box.qty_stem_flower, 0);
        if (!generalIndicators.value.total_suppliers.includes(item.partner.name)) {
                generalIndicators.value.total_suppliers.push(item.partner.name);
        }
    });
}

const handleKeydown = (event, cssClass) => {
    const inputs = document.querySelectorAll(cssClass);
    const currentIndex = Array.prototype.indexOf.call(inputs, event.target);
    if (event.key === 'Enter' && currentIndex < inputs.length - 1) {
        inputs[currentIndex + 1].focus();
    }
    if (event.key === 'Enter' && event.shiftKey   && currentIndex > 0) {
        inputs[currentIndex - 1].focus();
    }
}

const loadData = ()=> {
    baseStore.isLoading = true;
    stockStore.getStock(baseStore);
    setTimeout(() => {
        calcIndicators();
    }, 1000);
};

const formatNumber = (event) => {
    let value = event.target.value;
    value = value.replace(',', '.');
    if (value === '' || value === '.' || value === ',' || isNaN(value) || value === ' ' || value === '0') {
        event.target.value = '0.00';
        return;
    }
    event.target.value = parseFloat(value).toFixed(2);
}

const formatInteger = (event) => {
    let value = event.target.value;
    value = value.replace(',', '.');
    if (value === '' || value === '.' || value === ',' || isNaN(value) || value === ' ' || value === '0') {
        event.target.value = '0';
        return;
    }
    event.target.value = parseInt(value);
}

const calcTotalStems = (box_items) => {
    let total = 0;
    box_items.forEach(item => {
        total += item.qty_stem_flower;
    });
    return total;
}

// Computed
const filterData = computed(() => {
    return stockStore.stock.filter(item => item.is_visible);
})

// Watchers
watch(() => querySearch.value,(newValue) => {
        stockStore.filterStock(newValue);
        confirmDelete.value = false;
    },
    { immediate: true }
);

loadData();
</script>
<template>
    <div class="container-fluid p-0">
        <div class="row" v-if="baseStore.isLoading">
            <Loader/>
        </div>
        <div class="row ps-2" v-else="">
        <div class="row pt-1 pb-3">
            <div class="col d-flex gap-1 justify-content-start align-items-center">
                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        Disponibilidad
                    </span>
                    <span class="text-secondary ps-1 pe-2">
                        {{ stockStore.stockDay.date }}
                    </span>
                </div>
                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        Estado
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        <span class="text-success" v-if="stockStore.stockDay.is_active">
                            <IconLockOpen2 size="20" stroke="1.5"/>
                            Activa
                        </span>
                        <span class="text-danger" v-else>
                            <IconLock size="20" stroke="1.5"/>
                            Inactiva
                        </span>
                    </span>
                </div>
            </div>
            <div class="col d-flex gap-1 justify-content-end align-items-center">
                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        Proveedores
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        <span v-if="generalIndicators.total_suppliers">
                            {{ generalIndicators.total_suppliers.length }}
                        </span>
                    </span>
                </div>
                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        Pedidos
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        8
                    </span>
                </div>
                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        QB's
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        {{ generalIndicators.total_QB }}
                    </span>
                </div><div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        HB's
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        {{ generalIndicators.total_HB }}
                    </span>
                </div><div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        Tallos
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        {{ generalIndicators.total_stems }}
                    </span>
                </div>
            </div>
        </div>
        <div class="row d-flex justify-content-start p-1 rounded-1">
            <div class="col-3">
                <input type="text"
                class="form-control form-control-sm rounded-1 border-slate-500" 
                placeholder="Buscar"
                v-model="querySearch"
                >
            </div>
            <div class="col-9 d-flex gap-3 justify-content-end">
                    <button class="btn btn-sm btn-default text-danger" v-if="buttonsVisibility.delete" @click="deleteSelected">
                        <IconTrash size="15" stroke="1.5"/>
                        <span v-if="!confirmDelete">
                            Eliminar
                        </span>
                        <span v-else="">
                            Confirmar Borrado
                        </span>
                    </button>
                    <button class="btn btn-sm btn-default" v-if="buttonsVisibility.share" data-bs-toggle="modal" data-bs-target="#shareModal">
                        <IconShare size="15" stroke="1.5"/>
                        Compartir
                    </button>
                    <button class="btn btn-sm btn-default" v-if="buttonsVisibility.cost">
                        <IconCurrencyDollar size="15" stroke="1.5"/>
                        Costo
                    </button>
                    <button class="btn btn-sm btn-default" v-if="buttonsVisibility.margin">
                        <IconCurrencyDollar size="15" stroke="1.5"/>
                        Margen
                    </button>
                    <button class="btn btn-sm btn-default" v-if="buttonsVisibility.order">
                        <IconShoppingCart size="15" stroke="1.5"/>
                        Pedido
                    </button>
                    <button class="btn btn-sm btn-default" v-if="buttonsVisibility.all" @click="stockStore.selectAll(true);setVibilityButtons()">
                        <IconCheckbox size="15" stroke="1.5"/>
                        Todos
                    </button>
                    <button class="btn btn-sm btn-default" v-if="buttonsVisibility.none" @click="stockStore.selectAll(false);setVibilityButtons()">
                        <IconSquare size="15" stroke="1.5"/>
                        Ninguno
                    </button>
            </div>
        </div>
        <div class="row">
            <div class="col">
            <div class="table-responsive">
            <table class="table table-bordered table-hover">
                <thead>
                    <tr class="text-center">
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">Cant</th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">Tallos</th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">Proveedor</th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">Colores</th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50 d-flex justify-content-between gap-3">
                            <section class="pl-5">
                            </section>
                            <section class="d-flex gap-3 justify-content-between w-50">
                                <span>Productos</span>
                                <span>Tallos</span>
                                <span>Costo</span>
                                <span>Margen</span>
                                <span>Total</span>
                            </section>
                        </th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">
                            <IconSettings size="20" stroke="1.5"/>
                        </th>
                    </tr>
                </thead>
                <tbody>
                        <tr v-for="item in filterData" :key="item">
                            <td class="p-1 text-start ps-3">
                                {{ item.quantity }} {{ item.box_model }}
                            </td>
                            <td class="p-1 text-end">
                                {{ calcTotalStems(item.box_items) }}
                            </td>
                            <td class="p-1 text-start">
                                <span @click="suplierSelected=item.partner">
                                    <i class="text-primary" data-bs-toggle="modal" data-bs-target="#suplierModal">
                                        <IconEye size="15" stroke="1.5"/>
                                    </i>
                                    {{ item.partner.name }}
                                </span>
                            </td>
                            <td class="p-1">
                                <section v-for="box in item.box_items" :key="box" class="d-flex gap-1">
                                <div  class="d-flex gap-1">
                                        <small v-for="color in box.product_colors" :key="color" class="badge text-slate-500 border-sky-500" :class="colors[color]">
                                            {{ color }}
                                        </small>
                                    </div>
                                    </section>
                            </td>
                            <td class="p-1">
                                <section v-for="box in item.box_items" :key="box" class="text-end d-flex justify-content-end gap-2">
                                    <span @click="productSelected=box">
                                        <small data-bs-toggle="modal" data-bs-target="#productModal">
                                            <i class="text-primary">
                                                <IconEye size="15" stroke="1.5"/>
                                            </i>
                                        </small>
                                        {{ box.product_name }}
                                    </span>
                                    <span> {{ box.product_variety }} </span>
                                    <span class="text-slate-300">|</span>
                                    <input type="number" step="1" class="my-input w-15 text-end" @keydown="event => handleKeydown(event, '.my-input')" @focus="selectText" @change="formatInteger" @input="calcIndicators" v-model="box.qty_stem_flower">
                                    <input type="number" step="0.01" class="my-input-2 w-15 text-end" @keydown="event => handleKeydown(event, '.my-input-2')" @focus="selectText" @change="formatNumber"  v-model="box.stem_cost_price">
                                    <input type="number" step="0.01" class="my-input-3 w-15 text-end" @keydown="event => handleKeydown(event, '.my-input-3')" @focus="selectText" @change="formatNumber" v-model="box.margin" :class="{'bg-danger': parseFloat(box.margin) <= 0.00 }">
                                    <span class="text-gray-600 fw-semibold border-gray-300 w-15 text-end">
                                        {{ (parseFloat(box.margin) +  parseFloat(box.stem_cost_price)).toFixed(2) }}
                                    </span>
                                </section>
                            </td>
                            <td class="p-1 text-center">
                                <input type="checkbox" v-model="item.is_selected" @change="setVibilityButtons()">
                            </td>
                        </tr>
                    </tbody>
            </table>
        </div>
        </div>
        </div>
            <ModalProduct :product="productSelected"/>
            <ModalSuplier :suplier="suplierSelected"/>
            <ModalShareStock/>
        </div>
        </div>
</template>
<style scoped>
    input[type="checkbox"] {
        width: 15px;
        height: 15px;
    }
    .my-input, .my-input-2, .my-input-3 {
        border: 1px solid #ccc;
        border-radius: 2px;
        text-align: right;
    }
</style>