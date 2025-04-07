<script setup>
import { ref, onMounted, onUnmounted, watchEffect, computed, nextTick } from 'vue';
import { usePurchaseStore } from '@/stores/purcharses';
import { useBaseStore } from '@/stores/base';
import Loader from '@/components/Sotcks/Loader.vue';
import { useRoute } from 'vue-router';
import { IconHexagonMinus, IconClockHour9, IconCheckbox, IconFileCheck, IconFolderOpen } from '@tabler/icons-vue';

// Importación de DataTables.net y su CSS
import DataTable from 'datatables.net-dt';
import router from '@/router';

const baseStore = useBaseStore();
const purchaseStore = usePurchaseStore();

// Referencia a la tabla
const tableRef = ref(null);
let dataTableInstance = null;

// Computed para verificar si los datos están cargados
const isAllLoaded = computed(() => baseStore.stagesLoaded === 2);

// Método para inicializar DataTable
const initDataTable = async () => {
    await nextTick(); // Asegura que la tabla está renderizada antes de inicializar DataTables

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
            <div class="container-fluid">
                <div class="row pt-4">
                    <div class="col-12 fs-6 text-center text-orange-800 p-1 fw-semibold">
                        Listado de Pedidos de Clientes según este Stock
                    </div>
                    <div class="col-12">
                        <table ref="tableRef" class="table table-bordered table-striped table-hover">
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
                                <tr v-for="item in purchaseStore.sales" :key="item.order.id">
                                    <td class="p-1 text-center">
                                        {{ item.order.id }}
                                        <span class="text-gray-200 ps-1 pe-1"> | </span>
                                        <IconFolderOpen size="20" stroke="1.5" class="text-teal-600"
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
</template>
