<script setup>
import { useBaseStore } from '@/stores/base';
import { useOrdersStore } from '@/stores/orders';
import { useStockStore } from '@/stores/stock';
import Loader from '@/components/Loader.vue';
import OrderPreview from '@/components/OrderPreview.vue';
import AutocompleteCustomer from '@/components/AutocompleteCustomer.vue';
import { IconAlertCircle } from '@tabler/icons-vue';

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
        <div class="row" v-if="baseStore.isLoading && !stockStore.stockDay">
            <Loader />
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
                    <div class="col-12">
                        <div class="row p-1">
                            <div class="col-12">
                                <AutocompleteCustomer/>
                            </div>
                            <div class="col-12 bg-gray-200 bg-gradient rounded-1 shadow-sm" v-if="ordersStore.selectedCustomer">
                                <div class="row">
                                    <div class="col-1 text-end">ID:</div>
                                    <div class="col-1">{{ ordersStore.selectedCustomer.business_tax_id }}</div>
                                    <div class="col-1 text-end">Dir:</div>
                                    <div class="col-6">
                                        {{ ordersStore.selectedCustomer.address }}
                                        {{ ordersStore.selectedCustomer.country }}/{{ ordersStore.selectedCustomer.city  }}
                                    </div>
                                    <div class="col-1 text-end">Skype:</div>
                                    <div class="col-2">{{ ordersStore.selectedCustomer.skype }}</div>
                                </div>
                                <div class="row pt-1">
                                    <div class="col-1 text-end">Contacto:</div>
                                    <div class="col-8 d-flex gap-2">
                                        <span>{{ ordersStore.selectedCustomer.contact.name }}</span> 
                                        <span >{{  ordersStore.selectedCustomer.contact.email  }}</span>
                                        <span >{{ ordersStore.selectedCustomer.contact.phone }}</span>
                                        <span class="badge bg-green-600">{{  ordersStore.selectedCustomer.contact.contact_type }}</span>
                                    </div>
                                    <div class="col-1 text-end fw-semibold">
                                        Consolida:
                                    </div>
                                    <div class="col-2">
                                        {{ ordersStore.selectedCustomer.consolidate ? 'Si' : 'No' }}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <table class="table table-striped table-hover table-bordered">
                            <thead>
                                <tr class=" text-center">
                                    <th class="p-1 bg-cyan-900 text-light">#</th>
                                    <th class="p-1 bg-cyan-900 text-light">Fecha</th>
                                    <th class="p-1 bg-cyan-900 text-light">Cliente</th>
                                    <th class="p-1 bg-cyan-900 text-light">Estado</th>
                                    <th class="p-1 bg-cyan-900 text-light">T QBs</th>
                                    <th class="p-1 bg-cyan-900 text-light">T HBs</th>
                                    <th class="p-1 bg-cyan-900 text-light">Valor</th>
                                    <th class="p-1 bg-cyan-900 text-light">Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Aquí puedes agregar las filas de la tabla -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>