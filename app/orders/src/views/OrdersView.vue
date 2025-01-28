<script setup>
import { computed, onMounted } from 'vue';
import { useBaseStore } from '@/stores/base';
import { useOrdersStore } from '@/stores/orders';
import { useStockStore } from '@/stores/stock';
import Loader from '@/components/Loader.vue';
import OrderPreview from '@/components/OrderPreview.vue';
import { IconAlertCircle } from '@tabler/icons-vue';

const baseStore = useBaseStore();
const stockStore = useStockStore();
const ordersStore = useOrdersStore();


// COMPUTED
const isAllLoaded = computed(() => {
    return baseStore.stagesLoaded === 3;
})


onMounted(() => {
    baseStore.loadProducts(baseStore);
    ordersStore.loadCustomers(baseStore);
    
    if (stockStore.stockDay === null) {
        stockStore.getStock(baseStore);
    }else{
        baseStore.stagesLoaded++;
    }
});
</script>

<template>
    <div class="container-fluid p-0">
        <div class="row" v-if="!isAllLoaded">
            <div class="col text-center">
                <Loader />
            <h6 class="text-blue-600">
                {{ baseStore.stagesLoaded }} / 3 
            </h6>
            </div>
        </div>
        <div class="row ps-1" v-else>
            <div class="container">
                <div class="row">
                    <div class="col-2 text-center">
                        <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                            <span class="text-white bg-cyan-600 ps-1 pe-2">
                                Disponibilidad
                            </span>
                            <span class="text-cyan-900 ps-1 pe-2">
                                {{ stockStore.stockDay.date }}
                            </span>
                        </div>
                    </div>
                    <div class="col-3">
                        <span class="text-gray-600">Listado de pedidos de Stock {{ stockStore.stockDay.date }}</span>
                    </div>
                    <div class="col-7 text-end d-flex justify-content-end gap-3">
                        <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                            <span class="text-white bg-cyan-600 ps-1 pe-2">
                                Pendientes
                            </span>
                            <span class="text-cyan-900 ps-1 pe-2">
                                1
                            </span>
                        </div>
                        <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                            <span class="text-white bg-cyan-600 ps-1 pe-2">
                                Confirmados
                            </span>
                            <span class="text-cyan-900 ps-1 pe-2">
                                100
                            </span>
                        </div>
                        <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                            <span class="text-white bg-cyan-600 ps-1 pe-2">
                                Cancelados
                            </span>
                            <span class="text-cyan-900 ps-1 pe-2">
                                1
                            </span>
                        </div>
                        <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                            <span class="text-white bg-cyan-600 ps-1 pe-2">
                                Facturados
                            </span>
                            <span class="text-cyan-900 ps-1 pe-2">
                                1
                            </span>
                        </div>
                    </div>
                </div>
                <div class="row pt-4">
                    <div class="col-11 fs-6 p-2 bg-cyan-600 text-light mx-auto rounded-1">
                        <IconAlertCircle size="25" stroke="1.5" />
                        <span class="fw-semibold">
                            Vista previa de pedido
                        </span>
                        <span>
                            confirme detalles y proceda a guardar para generar las ordenes de compra a los proveedores
                        </span>
                            </div>
                    <div class="col-12">
                        <OrderPreview />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>