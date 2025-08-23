<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useBaseStore } from '@/stores/baseStore.js';
import { appConfig } from '@/AppConfig';
import Loader from '@/components/Sotcks/Loader.vue';
import axios from 'axios';
import {
    IconCheckbox,
    IconAlertTriangle,
    IconChevronCompactRight,
    IconSparkles,
} from '@tabler/icons-vue';


const baseStore = useBaseStore();
const selectedSupplier = ref(false);
const stockText = ref('');
const profitMargin = ref(0.06);
const appendStock = ref(true);
const route = useRouter();

// Seteamos el valor del contador a cero
baseStore.stagesLoaded = 0;

const analyzeStock = async () => {
    baseStore.stagesLoaded = 0;
    try {
        const payload = {
            idStock: baseStore.idStock,
            stockText: stockText.value,
            profitMargin: profitMargin.value,
            appendStock: appendStock.value,
            supplier: selectedSupplier.value,
        };

        const response = await axios.post(appConfig.urlAnalyce, payload, {
            headers: appConfig.headers,
        });

        const data = response.data;
        console.dir(data);

    } catch (error) {
        baseStore.stagesLoaded = 2;
        console.error("Error en analyzeStock:", error);
        alert(`Ocurrió un error: ${error.message}`);
    } finally {
        baseStore.isLoading = false;
        route.push('/');
    }
};

// COMPUTED
const isAllLoaded = computed(() => {
    return baseStore.stagesLoaded === 2;
})
onMounted(() => {
    baseStore.stagesLoaded = 0;
    baseStore.loadSuppliers();
    baseStore.loadProducts();
});

</script>
<template>
    <div class="container border">
        <div class="row p-2"></div>
        <div class="row" v-if="!isAllLoaded">
            <div class="col text-center">
                <Loader />
                <h6 class="text-center text-blue-600">
                    {{ baseStore.stagesLoaded }} /  2
                </h6>
            </div>
        </div>
        <div class="row" v-else>
            <div class="col-12 text-center pt-2 pb-2">
                <span class="fs-6 upper text-primary">
                    Asistente de Carga de Stocks
                </span>
            </div>
            <div class="col pb-5 shadow">
                <div class="row pt-1 pb-2 pe-2 ps-3 d-flex align-items-center">
                    <div class="col-3 ">
                        <div class="d-flex justify-content-end align-items-center gap-2 border-gray-600 rounded-1 bg-secondary">
                            <span class="text-white ps-1 pe-1">
                                Seleccione un Proveedor:
                            </span>
                            <span class="bg-gray ps-3 pe-3">
                                <IconChevronCompactRight size="20" stroke="1.5" class="text-gray-500" />
                            </span>
                        </div>
                    </div>
                    <div class="col-7">
                        <select class="form-select form-select-sm border-gray-500" v-model="selectedSupplier" @change="profitMargin = selectedSupplier.default_profit_margin">
                            <option>Seleccionar Proveedor</option>
                            <option v-for="supplier in baseStore.suppliers" :key="supplier" :value="supplier">
                                {{ supplier.name }}
                            </option>
                        </select>
                    </div>
                    <div class="col-2">
                        <router-link to="/">
                            <button class="btn btn-default text-danger">
                                <IconAlertTriangle size="20" stroke="1.5" />
                                Cancelar
                            </button>
                        </router-link>
                    </div>
                    <div class="col-12 p-2 m-1 " v-if="selectedSupplier">
                        <div class="row">
                            <div class="col-1 bg-gray-500 text-white border text-end">
                                <span class="p-1">
                                    Finca:
                                </span>
                            </div>
                            <div class="col-3 border-bottom">
                                <span>
                                    {{ selectedSupplier.business_tax_id }} /
                                    {{ selectedSupplier.name }}
                                </span>
                            </div>
                            <div class="col-1 bg-gray-500 text-white border text-end">
                                <span class="p-1">
                                    Dirección:
                                </span>
                            </div>
                            <div class="col-7 border-bottom">
                                <span>
                                    {{ selectedSupplier.city }},
                                    {{ selectedSupplier.address }}
                                </span>
                            </div>
                            <div class="col-1 bg-gray-500 text-white border text-end">
                                <span class="p-1">
                                    Correo:
                                </span>
                            </div>
                            <div class="col-3 border-bottom">
                                <span>
                                    {{ selectedSupplier.email }}
                                </span>
                            </div>
                            <div class="col-1 bg-gray-500 text-white border text-end">
                                <span class="p-1">
                                    Crédito:
                                </span>

                            </div>
                            <div class="col-3 border-bottom">
                                <span>
                                    {{ selectedSupplier.credit_term }} días
                                </span>
                            </div>
                            <div class="col-1 bg-gray-500 text-white border text-end">
                                <span class="p-1">
                                    Margen:
                                </span>
                            </div>
                            <div class="col-3 border-bottom">
                                {{ selectedSupplier.default_profit_margin }} USD,
                                <span class="text-success" v-if="selectedSupplier.is_profit_margin_included">
                                    Incluido
                                </span>
                                <span v-else="" class="text-warning">
                                    No Incluido
                                </span>
                            </div>
                            <div class="col-1 bg-gray-500 text-white border text-end">
                                <span class="p-1">
                                    Skype:
                                </span>
                            </div>
                            <div class="col-2 border-bottom">
                                <span>
                                    {{ selectedSupplier.skype }}
                                </span>
                            </div>
                            <div class="col-1 bg-gray-500 text-white border text-end">
                                <span class="p-1">
                                    Telef:
                                </span>
                            </div>
                            <div class="col-2 border-bottom">
                                <span>
                                    {{ selectedSupplier.phone }}
                                </span>
                            </div>
                            <div class="col-1 bg-gray-500 text-white border text-end">
                                <span class="p-1">
                                    Contacto:
                                </span>
                            </div>
                            <div class="col-2 border-bottom">
                                <span>
                                    {{ selectedSupplier.contact.name }}
                                </span>
                            </div>
                            <div class="col-1 bg-gray-500 text-white border text-end">
                                <span class="p-1">
                                    Tel:
                                </span>
                            </div>
                            <div class="col-2 border-bottom">
                                <span>
                                    {{ selectedSupplier.phone }}
                                </span>
                            </div>
                            <div class="col-6 pt-2">
                                <textarea v-model="stockText" class="form-control  border-gray-400"
                                    rows="10"></textarea>
                            </div>
                            <div class="col-6 pt-2 d-flex flex-column gap-2 align-items-start">
                                <div class="pt-2 mt-2">
                                    <div class="alert alert-primary p-1" v-if="selectedSupplier.have_stock">
                                        <IconAlertTriangle size="20" stroke="1.5" />
                                        <span>
                                            Esta Disponibilidad será <strong> anexado al existente</strong>
                                        </span>
                                    </div>
                                </div>
                                <div class="form-check d-flex align-items-center">
                                    <input type="checkbox" class="form-check-input" id="exampleCheck1"
                                        v-model="appendStock">
                                    <label class="form-check">
                                        Anexar Disponibilidad
                                    </label>
                                </div>
                                <div class="d-flex align-items-center gap-3">
                                    <input type="number" v-model="profitMargin" step="0.01"
                                        class="form-control w-30 border-gray-600 text-end" id="exampleCheck1">
                                    Margen Disponibilidad
                                    <span v-if="selectedSupplier.is_profit_margin_included"
                                        class="badge bg-success p-1">
                                        <IconCheckbox size="20" stroke="1.5" />
                                        Ya incluido
                                    </span>
                                    <span v-else="" class="badge bg-danger p-1">
                                        <IconAlertTriangle size="20" stroke="1.5" />
                                        No incluido
                                    </span>
                                </div>
                                <br/>
                                <button class="btn btn-default" @click="analyzeStock">
                                    <IconSparkles size="20" stroke="1.5" />
                                    Analizar Stock
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>