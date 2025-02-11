<script setup>
import {computed, onMounted} from 'vue';
import { usePurchaseStore } from '@/stores/purcharses';
import { useBaseStore } from '@/stores/base';
import Loader from '@/components/Loader.vue';

const baseStore = useBaseStore();
const purchaceStore = usePurchaseStore();

// COMPUTED
const isAllLoaded = computed(() => {
    return baseStore.stagesLoaded === 2;
})

// ON MOUNTED
onMounted(() => {
    baseStore.stagesLoaded = 0;
    baseStore.loadProducts(baseStore);
    purchaceStore.loadSales(baseStore)
});


</script>
<template>
    <div class="container-fluid p-0">
        <div class="row" v-if="!isAllLoaded">
            <div class="col text-center">
                <Loader />
                <h6 class="text-blue-600">
                    {{ baseStore.stagesLoaded }} / 2
                </h6>
            </div>
        </div>
        <div class="row ps-1" v-else>
            <div class="container-fluid" v-if="purchaceStore.showViews.listOrders">
                <div class="row pt-4" v-if="purchaceStore.showViews.listOrders">
                    <div class="col-12 fs-6 text-center text-orange-800 p-1 fw-semibold">
                        Listado de Pedidos de Clientes segun este Stock
                    </div>
                    <div class="col-12">
                        <table class="table table-bordered table-striped table-hover">
                            <thead>
                                <tr class="text-center">
                                    <th class="p-1 bg-orange-500">Nro</th>
                                    <th class="p-1 bg-orange-500">Fecha</th>
                                    <th class="p-1 bg-orange-500">Cliente</th>
                                    <th class="p-1 bg-orange-500">Tipo</th>
                                    <th class="p-1 bg-orange-500">Estado</th>
                                    <th class="p-1 bg-orange-500">QB</th>
                                    <th class="p-1 bg-orange-500">HB</th>
                                    <th class="p-1 bg-orange-500">Tallos</th>
                                    <th class="p-1 bg-orange-500">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="item in purchaceStore.sales" :key="item">
                                    <td class="p-1 text-center">
                                        {{ item.order.id }}
                                        <span class="text-gray-200 ps-1 pe-1"> | </span>
                                        <IconFolderOpen size="20" stroke="1.5" class="text-teal-600"
                                            @click="selectOrder(item.order.id)" />
                                    </td>
                                    <td class="p-1">
                                        {{ baseStore.formatDate(item.order.date) }}
                                    </td>
                                    <td class="p-1">
                                        {{ item.order.partner.name }}
                                    </td>
                                    <td class="p-1">
                                        {{ item.order.type_document.replace('_', ' ') }}
                                    </td>
                                    <td class="p-1">
                                        <IconClockHour9 v-if="item.order.status === 'PENDIENTE'" size="20" stroke="1.5"
                                            class="text-cyan-600" />
                                        <IconCheckbox v-if="item.order.status === 'CONFIRMADO'" size="20" stroke="1.5"
                                            class="text-blue-600" />
                                        <IconFileCheck v-if="item.order.status === 'FACTURADO'" size="20" stroke="1.5"
                                            class="text-green-600" />
                                        <IconHexagonMinus v-if="item.order.status === 'CANCELADO'" size="20" stroke="1.5"
                                            class="text-red-600" />
                                        <span class="text-gray-200 ps-1 pe-1">|</span>
                                        <span class="fw-semibold">
                                            {{ item.order.status }}
                                        </span>
                                    </td>
                                    <td class="p-1 text-end">{{ item.order.qb_total }}</td>
                                    <td class="p-1 text-end">{{ item.order.hb_total }}</td>
                                    <td class="p-1 text-end">{{ item.order.total_stem_flower }}</td>
                                    <td class="p-1 text-end">{{
                                        baseStore.formatCurrency(item.order.total_price)
                                        }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>