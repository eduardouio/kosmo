<script setup>
import { ref, onMounted, onUnmounted, watchEffect, computed, nextTick, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useBaseStore } from '@/stores/baseStore.js';
import { useOrdersStore } from '@/stores/ordersStore.js';
import { useStockStore } from '@/stores/stockStore.js';
import Loader from '@/components/Sotcks/Loader.vue';
import OrderPreview from '@/components/Sotcks/OrderPreview.vue';
import { appConfig } from '@/AppConfig';
import SideBar from '@/components/Sotcks/SideBar.vue';
import { 
    IconAlertCircle,
    IconClockHour9,
    IconCheckbox,
    IconFileCheck,
    IconHexagonMinus,
    IconFolderOpen,
    IconPrinter,
    IconAlertTriangle,
} from '@tabler/icons-vue';


const baseStore = useBaseStore();
const stockStore = useStockStore();
const ordersStore = useOrdersStore();
const router = useRouter();

const selectOrder = (id) => {
    router.push({ name: 'customerOrderDetail', params: { id: id } });
}

// COMPUTED
const isAllLoaded = computed(() => {
    return baseStore.stagesLoaded === 4;
})


const getUrlReportCusOrder = (id) => {
    let urlReportOrder = appConfig.urlReportCustOrder.replace('{id_order}', id);
    return urlReportOrder;
};

// ON MOUNTED
onMounted(() => {
    baseStore.stagesLoaded = 0;
    baseStore.loadProducts(baseStore);
    ordersStore.loadCustomers(baseStore);
    ordersStore.loadOrders(baseStore);
    if (stockStore.stockDay === null) {
        stockStore.getStock(baseStore);
    }else{
        baseStore.stagesLoaded++;
    }
    
    // Para inicializar el mensaje por defecto
    if (ordersStore.newOrder && ordersStore.newOrder.length > 0) {
        baseStore.updateGlobalAlertStatus(ordersStore);
    }
});

// Vigilar cambios en el pedido para actualizar alertas
watch(() => ordersStore.newOrder, () => {
    if (ordersStore.newOrder && ordersStore.newOrder.length > 0) {
        baseStore.updateGlobalAlertStatus(ordersStore);
    }
}, { deep: true });

// Vigilar cambios en el cliente seleccionado
watch(() => ordersStore.selectedCustomer, () => {
    if (ordersStore.newOrder && ordersStore.newOrder.length > 0) {
        baseStore.updateGlobalAlertStatus(ordersStore);
    }
});
</script>

<template>
    <div class="cotainer-fluid">
        <div class="row">
        <div class="col-2">
            <SideBar />
        </div>
    <div class="col pe-3">
        <!-- Barra de alertas centralizada -->
        <div class="row mb-2" v-if="baseStore.alertMessage && ordersStore.newOrder.length > 0">
            <div class="col-11 fs-6 p-2 mx-auto rounded-1"
                :class="{
                    'bg-cyan-600 text-light': baseStore.alertType === 'info',
                    'bg-warning text-dark': baseStore.alertType === 'warning',
                    'bg-danger text-white': baseStore.alertType === 'error'
                }">
                <IconAlertTriangle size="20" stroke="1.5" v-if="baseStore.alertType === 'error' || baseStore.alertType === 'warning'" />
                <IconAlertCircle size="25" stroke="1.5" v-else />
                <span class="fw-semibold ms-2">
                    {{ baseStore.alertMessage }}
                </span>
            </div>
        </div>
        
        <div class="row" v-if="!isAllLoaded">
            <div class="col text-center">
                <Loader />
                <h6 class="text-blue-600">
                    {{ baseStore.stagesLoaded }} / 3
                </h6>
            </div>
        </div>
        <div class="row" v-else>
            <div class="container-fluid" v-if="ordersStore.showViews.listOrders">
                <div class="row pt-2">
                    <div class="col-12 text-center fs-5 text-teal-700 upper">
                        Pedidos de Clientes
                    </div>
                    <div class="col-4 text-center">
                        <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                            <span class="text-white bg-cyan-600 ps-1 pe-2">
                                Disponibilidad
                            </span>
                            <span class="text-cyan-900 ps-1 pe-2">
                                {{ stockStore.stockDay.date }}
                            </span>
                        </div>
                    </div>
                    <div class="col-8 text-end d-flex justify-content-end gap-3">
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
                <div class="row pt-4" v-if="ordersStore.newOrder.length">
                    <div class="col-12">
                        <OrderPreview />
                    </div>
                </div>
                <div class="row pt-4" v-if="ordersStore.showViews.listOrders && !ordersStore.newOrder.length">
                    <div class="col-12">
                        <table ref="tableRef" class="table table-bordered table-striped table-hover">
                            <thead>
                                <tr class="text-center">
                                    <th class="p-1 bg-teal-500 text-white">Nro</th>
                                    <th class="p-1 bg-teal-500 text-white">Fecha</th>
                                    <th class="p-1 bg-teal-500 text-white">Cliente</th>
                                    <th class="p-1 bg-teal-500 text-white">Tipo</th>
                                    <th class="p-1 bg-teal-500 text-white">Estado</th>
                                    <th class="p-1 bg-teal-500 text-white">QB</th>
                                    <th class="p-1 bg-teal-500 text-white">HB</th>
                                    <th class="p-1 bg-teal-500 text-white">Tallos</th>
                                    <th class="p-1 bg-teal-500 text-white">Reporte</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="item in ordersStore.orders" :key="item" v-if="ordersStore.orders.length">
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
                                    <td class="p-1 text-center">
                                        <a :href="getUrlReportCusOrder(item.order.id)">
                                            <IconPrinter size="20" stroke="1.5" class="text-blue-600" />
                                        </a>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
        
</div>
    </div>
</template>