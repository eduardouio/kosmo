<script setup>
import { useBaseStore } from '@/stores/base';
import { useOrdersStore } from '@/stores/orders';
import { useStockStore } from '@/stores/stock';
import Loader from '@/components/Loader.vue';

const baseStore = useBaseStore();
const stockStore = useStockStore();
const ordersStore = useOrdersStore();

const loadData = () => {
    setTimeout(() => {
        baseStore.loadProducts();
        ordersStore.loadCustomers();
        baseStore.loadSuppliers();
    }, 100);
};
loadData();
</script>

<template>
    <div class="container-fluid p-0">
        <div class="row" v-if="baseStore.isLoading">
            <Loader />
        </div>
        <div class="row ps-2" v-else>
            <div class="container">
                <div class="row">
                    <div class="col-12">
                        <strong>Listado de pedidos de Stock {{ stockStore.stockDay }}</strong>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>