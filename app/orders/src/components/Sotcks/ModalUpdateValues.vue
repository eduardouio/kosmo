<script setup>
import { ref, onMounted } from 'vue';
import { IconX, IconCheck } from '@tabler/icons-vue';
import { useStockStore } from '@/stores/stockStore.js';

const confirmUpdate = ref(false);
const profitMargin = ref(0.00);
const cost = ref(0.00);
const stems = ref(0);
const stockStore = useStockStore();

const updateValues = () => {
    if (!confirmUpdate.value) {
        confirmUpdate.value = true;
        return;
    }
    
    if (cost.value != 0) {
        stockStore.updateValues(cost.value, 'stem_cost_price');
    }

    if (profitMargin.value != 0) {
        stockStore.updateValues(profitMargin.value, 'margin');
    }

    if (stems.value != 0) {
        stockStore.updateValues(stems.value, 'qty_stem_flower');
    }

    confirmUpdate.value = false;
    cost.value = 0.00;
    profitMargin.value = 0.00;
    stems.value = 0;

    document.querySelector('#updateValuesModal .btn-close').click();
}

const formatNumber = (event) => {
    let value = event.target.value;
    value = value.replace(',', '.');
    if (value === '' || value === '.' || value === ',' || isNaN(value) || value === ' ' || value === '0') {
        event.target.value = '0.00';
        return;
    }
    event.target.value = parseFloat(value).toFixed(2);
}


</script>

<template>
    <div class="modal fade modal-sm" id="updateValuesModal" tabindex="-1" aria-labelledby="updateValuesModal"
        aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-kosmo-primary p-1 text-white">
                    <span class="modal-title fs-6 ps-3" id="updateValuesModal">
                        Actualizar Valores Por Lote
                    </span>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="container-fluid">
                        <div class="row">
                            <div class="col-12">
                                <div class="alert alert-warning" role="alert">
                                    <strong>Atención!</strong> Solo se actualizará los valores diferentes de cero.
                                </div>
                            </div>
                            <div class="col-12">
                                <div class="input-group mb-3">
                                    <span class="input-group-text">$</span>
                                    <input type="number" step="0.01" class="form-control text-end"
                                        aria-label="Dollar amount (with dot and two decimal places)"
                                        v-model="cost" @change="formatNumber">
                                    <span class="input-group-text"> Costo &nbsp;&nbsp;</span>
                                </div>
                                <div class="input-group mb-3">
                                    <span class="input-group-text">$</span>
                                    <input type="number" step="0.01" class="form-control text-end"
                                        aria-label="Dollar amount (with dot and two decimal places)"
                                        v-model="profitMargin" @change="formatNumber">
                                    <span class="input-group-text">Margen</span>
                                </div>
                                <div class="input-group mb-3">
                                    <span class="input-group-text">Tallos</span>
                                    <input type="number" step="1" class="form-control text-end"
                                        aria-label="Cantidad de tallos"
                                        v-model="stems">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer bg-secondary bg-gradient p-1">
                    <button type="button" class="btn btn-default btn-sm" data-bs-dismiss="modal">
                        <IconX size="20" stroke="1.5" />
                        Cancelar
                    </button>
                    <button type="button" class="btn btn-default btn-sm" @click="updateValues()">
                        <IconCheck size="20" stroke="1.5" />
                        <span v-if="confirmUpdate">Confirmar</span>
                        <span v-else="">Actualizar</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>@/stores/stockStore