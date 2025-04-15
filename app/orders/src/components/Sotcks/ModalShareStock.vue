<script setup>
import { watch } from 'vue';
import { useBaseStore } from '@/stores/baseStore.js';
import { useOrdersStore } from '@/stores/ordersStore.js';
import { useStockStore } from '@/stores/stockStore.js';
import { IconClipboard, IconX  } from '@tabler/icons-vue';
import AutocompleteCustomer from './AutocompleteCustomer.vue';

const baseStore = useBaseStore();
const orderStore = useOrdersStore();
const stockStore = useStockStore();

const copyToClipboard = () => {
    const textArea = document.querySelector('textarea');
    textArea.select();
    navigator.clipboard.writeText(stockStore.stockText);
}

watch(() => orderStore.selectedCustomer, (newValue) => {
    if (newValue) {
        stockStore.selectedCustomer = newValue;
        stockStore.stockToText();
    }
});
</script>
<template>
    <div class="modal fade modal-lg" id="shareModal" tabindex="-1" aria-labelledby="shareModal" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-kosmo-primary p-1 text-white">
                    <span class="modal-title fs-6 ps-3" id="shareModal">
                        Compartir Disponibilidad
                    </span>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="row d-flex align-items-center">
                        <div class="col">
                            <AutocompleteCustomer />
                        </div>
                    </div>
                    <div class="row pb-3" v-if="stockStore.selectedCustomer">
                        <div class="col-12 text-cyan-500">
                            Proveedores Relacionados
                        </div>
                        <div class="col-12 p-1 bg-yellow-100" v-if="stockStore.selectedCustomer.related_partners">
                            <section v-for="supplier in stockStore.selectedCustomer.related_partners" class="d-flex gap-2" :key="supplier">
                                <span class="border p-1 rounded-1 shadow bg-gray-100 bg-gradient">
                                    <strong>
                                        #{{ supplier.id }} 
                                    </strong>
                                    {{ supplier.name }}
                                </span>
                            </section>
                        </div>
                        <div class="col-12 p-1 bg-red-100" v-else="">
                            <span class="text-red-500">No tiene Proveedores Relacionados</span>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col">
                            <textarea class="form-control" v-model="stockStore.stockText" readonly rows="20"></textarea>
                        </div>
                    </div>
                </div>
                <div class="modal-footer bg-secondary bg-gradient p-1">
                    <button type="button" class="btn btn-default btn-sm" data-bs-dismiss="modal">
                        <IconX size="20" stroke="1.5" />
                        Cerrar
                    </button>
                    <button type="button" class="btn btn-default btn-sm" @click="copyToClipboard()">
                        <IconClipboard size="20" stroke="1.5" />
                        Copiar
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
@/stores/baseStore@/stores/ordersStore@/stores/stockStore