<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useBaseStore } from '@/stores/base';
import { appConfig } from '@/AppConfig';
import Loader from '@/components/Loader.vue';
import {
    IconCheckbox,
    IconAlertTriangle,
    IconChevronCompactRight,
    IconSparkles,
} from '@tabler/icons-vue';


const storeBase = useBaseStore();
const selectedSupplier = ref(false);
const stockText = ref('');
const profitMargin = ref(0.06);
const appendStock = ref(true);
const route = useRouter();

const analyzeStock = async () => {
    storeBase.isLoading = true;
    try {
        const payload = {
            idStock: storeBase.idStock,
            stockText: stockText.value,
            profitMargin: profitMargin.value,
            appendStock: appendStock.value,
            supplier: selectedSupplier.value,
        };

        const response = await fetch(appConfig.urlAnalyce, {
            method: 'POST',
            headers: appConfig.headers,
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.dir(data);

    } catch (error) {
        console.error("Error en analyzeStock:", error);
        alert(`Ocurrió un error: ${error.message}`);
    } finally {
        storeBase.isLoading = false;
        route.push('/');
    }
};

onMounted(() => {
    storeBase.loadSuppliers();
    storeBase.loadProducts();
});
</script>
<template>
    <div class="container-fluid p-0">
        <div class="row">
        <div class="col">
            <Loader v-if="storeBase.isLoading" />
            <div v-else="">
                <div class="row pt-1 pb-2 pe-2 ps-3">
                    <div class="col-3 ">
                        <div class="d-flex justify-content-end align-items-center gap-2 border-gray-400 rounded-1">
                            <span>
                                <IconChevronCompactRight size="20" stroke="1.5" class="text-gray-500" />
                            </span>
                            <span class="text-white bg-gray-400 ps-1 pe-1">
                                Seleccione un Proveedor:
                            </span>
                        </div>
                    </div>
                    <div class="col-9">
                        <select class="form-select form-select-sm border-gray-500" v-model="selectedSupplier" @change="profitMargin = selectedSupplier.default_profit_margin">
                            <option>Seleccionar Proveedor</option>
                            <option v-for="supplier in storeBase.suppliers" :key="supplier" :value="supplier">
                                {{ supplier.name }}
                            </option>
                        </select>
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
    </div>
</template>