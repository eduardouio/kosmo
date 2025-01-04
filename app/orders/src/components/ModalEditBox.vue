<script setup>
import { useBaseStore } from '@/stores/base';
import { IconX, IconCheck, IconPlus } from '@tabler/icons-vue';

const props = defineProps(['stockItem']);
const baseStore = useBaseStore();
</script>
<template>
    <div class="modal fade modal-lg" id="editBoxModal" tabindex="-1" aria-labelledby="editBoxModal" aria-hidden="true" v-if="!baseStore.isLoading && stockItem">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-kosmo-primary p-1 text-white">
                    <span class="modal-title fs-6 ps-3" id="editBoxModal">
                        Editar Disponibilidad de Stock {{ stockItem.partner.name }}
                    </span>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                   <div class="container">
                    <div class="row">
                        <div class="col-2">
                            <span class="text-secondary">ID:</span>
                            {{ stockItem.stock_detail_id }}
                        </div>
                        <div class="col-4">
                            <span class="text-secondary">Proveedor:</span>
                            {{ stockItem.partner.name }}
                        </div>
                        <div class="col-3">
                            <span class="text-secondary">Margen:</span>
                            {{ stockItem.partner.default_profit_margin }}
                        </div>
                        <div class="col-3">
                            <span class="text-secondary">Costo Caja:</span>
                            {{ stockItem.tot_cost_price_box }}
                        </div>
                    </div>
                    <div class="col-12 pt-4 pb-2 d-flex justify-content-between">
                        <span class="text-secondary">Contenido de Caja:</span>
                        <button class="btn btn-sm btn-default">
                            <IconPlus size="20" stroke="1.5" />
                            Agregar Producto
                        </button>
                    </div>
                    <div class="col-12">
                        <table class="table table-bordered table-striped">
                            <thead>
                                <tr>
                                    <th>Producto</th>
                                    <th>Largo</th>
                                    <th>Cantidad</th>
                                    <th>Costo</th>
                                    <th>Margen</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="box in stockItem.box_items">
                                    <td>{{ box.product_name }} {{ box.product_variety }}</td>
                                    <td>{{ box.length }}</td>
                                    <td>{{ box.qty_stem_flower }}</td>
                                    <td>{{ box.stem_cost_price }}</td>
                                    <td>{{ box.margin }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                   </div>
                </div>
                <div class="modal-footer bg-secondary bg-gradient p-1">
                    <button type="button" class="btn btn-default btn-sm" data-bs-dismiss="modal">
                        <IconX size="20" stroke="1.5" />
                        Cancelar
                    </button>
                    <button type="button" class="btn btn-default btn-sm" @click="copyToClipboard()">
                        <IconCheck size="20" stroke="1.5" />
                        Modificar
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
