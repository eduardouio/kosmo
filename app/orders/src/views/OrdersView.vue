<script setup>
import { ref, onMounted } from 'vue';
import { useBaseStore } from '@/stores/base';
import { useOrdersStore } from '@/stores/orders';
import { appConfig } from '@/AppConfig';
import Loader from '@/components/Loader.vue';

const baseStore = useBaseStore();
const ordersStore = useOrdersStore();

onMounted( async () => {
    baseStore.isLoading = true;
    await ordersStore.loadCustomers();
    baseStore.isLoading = false;
});


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
                        <h1>Vamos por los pedidos de lo clientes</h1>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>