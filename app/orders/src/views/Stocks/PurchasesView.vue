<script setup>
import { ref, onMounted, onUnmounted, watchEffect, computed, nextTick } from 'vue';
import { usePurchaseStore } from '@/stores/purcharses';
import { useBaseStore } from '@/stores/base';
import { useStockStore } from '@/stores/stock';
import Loader from '@/components/Sotcks/Loader.vue';
import { IconHexagonMinus, IconClockHour9, IconCheckbox, IconFileCheck, IconFolderOpen } from '@tabler/icons-vue';
import DataTable from 'datatables.net-dt';
import router from '@/router';
import SideBar from '@/components/Sotcks/SideBar.vue';

const baseStore = useBaseStore();
const purchaseStore = usePurchaseStore();
const stockStore = useStockStore();
const tableRef = ref(null);
let dataTableInstance = null;

const isAllLoaded = computed(() => baseStore.stagesLoaded === 3);

const initDataTable = async () => {
    await nextTick();

    if (tableRef.value) {
        dataTableInstance = new DataTable(tableRef.value, {
            paging: true,
            searching: true,
            ordering: true,
            pageLength: 20,
            dom: '<"d-flex justify-content-between"lf>t<"d-flex justify-content-between"ip>',
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.13.1/i18n/es-ES.json'
            }
        });
    }
};

// Método para destruir DataTable
const destroyDataTable = () => {
    if (dataTableInstance) {
        dataTableInstance.destroy();
        dataTableInstance = null;
    }
};


// Método para seleccionar un pedido
const selectOrder = (id) => {
    purchaseStore.selectedPurchaseId(id);
    router.push({ name: 'supplierOrderDetail', params: { id: id } });
};

// Cargar datos en `onMounted`
onMounted(() => {
    baseStore.stagesLoaded = 0;
    baseStore.loadProducts(baseStore);
    purchaseStore.loadSales(baseStore);
    if (stockStore.stockDay === null) {
        stockStore.getStock(baseStore);
    }else{
        baseStore.stagesLoaded++;
    }
});

// Observar cambios en `purchaseStore.sales` para actualizar DataTable
watchEffect(() => {
    if (purchaseStore.sales.length) {
        destroyDataTable();
        initDataTable();
    }
});

// Destruir DataTable al desmontar
onUnmounted(() => {
    destroyDataTable();
});
</script>

<template>
    <div class="conainer-fluid">
        <div class="row">
            <div class="col-2">
                <SideBar />
            </div>
    <div class="col pe-3">
        <div class="row" v-if="!isAllLoaded">
            <div class="col text-center">
                <Loader />
                <h6 class="text-blue-600">
                    {{ baseStore.stagesLoaded }} / 2
                </h6>
            </div>
        </div>
        <div class="row" v-else>
            <div class="container-fluid">
                <div class="row pt-2">
                    <div class="col-12 text-center fs-5 text-orange-700 upper">
                        Órdenes de Compra a Proveedores
                    </div>
                    <div class="col-4 text-center">
                        <div class="d-flex align-items-center gap-2 border-orange-600 rounded-1">
                            <span class="text-white bg-orange-700 ps-1 pe-2">
                                Disponibilidad
                            </span>
                            <span class="text-orange-900 ps-1 pe-2">
                                {{ stockStore.stockDay.date }}
                            </span>
                        </div>
                    </div>
                    <div class="col-8 text-end d-flex justify-content-end gap-3">
                        <div class="d-flex align-items-center gap-2 border-orange-600 rounded-1">
                            <span class="text-white bg-orange-700 ps-1 pe-2">
                                Pendientes
                            </span>
                            <span class="text-orange-900 ps-1 pe-2">
                                1
                            </span>
                        </div>
                        <div class="d-flex align-items-center gap-2 border-orange-600 rounded-1">
                            <span class="text-white bg-orange-700 ps-1 pe-2">
                                Confirmados
                            </span>
                            <span class="text-orange-900 ps-1 pe-2">
                                100
                            </span>
                        </div>
                        <div class="d-flex align-items-center gap-2 border-orange-600 rounded-1">
                            <span class="text-white bg-orange-700 ps-1 pe-2">
                                Cancelados
                            </span>
                            <span class="text-orange-900 ps-1 pe-2">
                                1
                            </span>
                        </div>
                        <div class="d-flex align-items-center gap-2 border-orange-600 rounded-1">
                            <span class="text-white bg-orange-700 ps-1 pe-2">
                                Facturados
                            </span>
                            <span class="text-orange-900 ps-1 pe-2">
                                1
                            </span>
                        </div>
                    </div>
                </div>
                <div class="row pt-4">
                    <div class="col-12">
                        <table ref="tableRef" class="table table-bordered table-striped table-hover">
                            <thead>
                                <tr class="text-center">
                                    <th class="p-1 bg-orange-700 text-white">Nro</th>
                                    <th class="p-1 bg-orange-700 text-white">Fecha</th>
                                    <th class="p-1 bg-orange-700 text-white">Cliente</th>
                                    <th class="p-1 bg-orange-700 text-white">Tipo</th>
                                    <th class="p-1 bg-orange-700 text-white">Estado</th>
                                    <th class="p-1 bg-orange-700 text-white">QB</th>
                                    <th class="p-1 bg-orange-700 text-white">HB</th>
                                    <th class="p-1 bg-orange-700 text-white">Tallos</th>
                                    <th class="p-1 bg-orange-700 text-white">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="item in purchaseStore.sales" :key="item.order.id">
                                    <td class="p-1 text-center">
                                        {{ item.order.id }}
                                        <span class="text-gray-200 ps-1 pe-1"> | </span>
                                        <IconFolderOpen size="20" stroke="1.5" class="text-orange-700"
                                            @click="selectOrder(item.order.id)" />
                                    </td>
                                    <td class="p-1">{{ baseStore.formatDate(item.order.date) }}</td>
                                    <td class="p-1">{{ item.order.partner.name }}</td>
                                    <td class="p-1">{{ item.order.type_document.replace('_', ' ') }}</td>
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
                                    <td class="p-1 text-end">{{ baseStore.formatCurrency(item.order.total_price) }}</td>
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
