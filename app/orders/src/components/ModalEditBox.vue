<script setup>
import { ref, computed, onMounted } from 'vue';
import { useBaseStore } from '@/stores/base';
import { useStockStore } from '@/stores/stock';
import { appConfig } from '@/AppConfig';
import Autocomplete from '@/components/Autocomplete.vue';
import ProductImage from '@/components/ProductImage.vue';
import { 
    IconX,
    IconPlus,
    IconTrash,
    IconSettings,
    IconEdit,
} from '@tabler/icons-vue';

const props = defineProps(['stockItem']);
const baseStore = useBaseStore();
const stockStore = useStockStore();
const tabShowIdx = ref({
    tabEditBox: true,
    tabAddProduct: false,
});
const confirmDelete = ref(false);
const newBoxItem = ref({});

const setDefaultBoxItem = () => {
    newBoxItem.value = {
        "id": 0,
        "stock_detail_id": null,
        "product_id": null,
        "product_name": "ELEGIR",
        "product_variety": "EJELIR",
        "product_image": null,
        "product_colors": [],
        "product_notes": null,
        "length": null,
        "qty_stem_flower": 0,
        "stem_cost_price": 0,
        "margin": 0.06,
        "is_active": true
    };
}


const isValidData = computed(() => {
    const { length, qty_stem_flower, stem_cost_price, margin } = newBoxItem.value;
    return length > 0 &&
           qty_stem_flower > 0 &&
           stem_cost_price > 0 &&
           margin > 0 &&
           baseStore.selectedProduct !== null;
});

const createBoxItem = async() => {
    if (!isValidData.value) {
        alert('Debe seleccionar un producto');
        return;
    }
    newBoxItem.value.stock_detail_id = props.stockItem.stock_detail_id;
    newBoxItem.value.product_id = baseStore.selectedProduct.id;
    newBoxItem.value.product_name = baseStore.selectedProduct.name;
    newBoxItem.value.product_variety = baseStore.selectedProduct.variety;
    newBoxItem.value.product_colors = baseStore.selectedProduct.colors;
    newBoxItem.value.product_notes = baseStore.selectedProduct.notes;
    newBoxItem.value.product_image = baseStore.selectedProduct.image;
    const data =  await stockStore.addBoxItem(newBoxItem.value);
    setDefaultBoxItem();
}

const changeTab = (tab) => {
    Object.keys(tabShowIdx.value).forEach((key) => {
        tabShowIdx.value[key] = false;
    });
    tabShowIdx.value[tab] = true;
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

const formatInteger = (event) => {
    let value = event.target.value;
    value = value.replace(',', '.');
    if (value === '' || value === '.' || value === ',' || isNaN(value) || value === ' ' || value === '0') {
        event.target.value = '0';
        return;
    }
    event.target.value = parseInt(value);
}

const updateBoxItem = (boxItem, deleteBox=false) => {
    if (deleteBox) {
        confirmDelete.value = true;
        if (confirmDelete.value) {
            boxItem.is_active = false;
            stockStore.updateStockDetail([boxItem], true);
        }
        return;
    } 
    stockStore.updateStockDetail([boxItem]);
}

onMounted(() => {
    setDefaultBoxItem();
});

</script>
<template>
    <div class="modal fade modal-xl" id="editBoxModal" tabindex="-1" aria-labelledby="editBoxModal" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-kosmo-primary p-1 text-white">
                    <span class="modal-title fs-6 ps-3" id="editBoxModal" v-if="!baseStore.isLoading && stockItem">
                        Editar Disponibilidad de Stock {{ stockItem.partner.name }}
                    </span>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                   <div class="container-fluid" v-if="!baseStore.isLoading && stockItem">
                    <div class="row border p-1">
                        <div class="col-2">
                            <span class="text-secondary">ID:</span>
                            {{ stockItem.stock_detail_id }}
                        </div>
                        <div class="col-4">
                            <span class="text-secondary">Proveedor:</span>
                            {{ stockItem.partner.name }}
                        </div>
                        <div class="col-3">
                            <span class="text-secondary">Cajas:</span>
                            {{ stockItem.quantity }} {{ stockItem.box_model }}
                        </div>
                        <div class="col-3">
                            <span class="text-secondary">Tallos:</span>
                            {{ stockItem.tot_stem_flower }}
                        </div>
                    </div>
                    <div class="row">
                    <div class="col-12 pt-4 pb-2 d-flex justify-content-between">
                        <ul class="nav nav-tabs">
                        <li class="nav-item">
                            <a class="nav-link" aria-current="page" href="#" @click="changeTab('tabEditBox')" :class="{'active': tabShowIdx.tabEditBox}">
                                <IconEdit size="20" stroke="1.5" />
                                Modificar Contenido por C/{{ stockItem.box_model }}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" @click="changeTab('tabAddProduct')" :class="{'active': tabShowIdx.tabAddProduct}">
                                <IconPlus size="20" stroke="1.5" />
                                Agregar Producto
                            </a>
                        </li>
                        </ul>
                    </div>
                    <div class="col-12" v-if="tabShowIdx.tabEditBox">
                        <table class="table table-bordered table-striped">
                            <thead>
                                <tr class="text-center">
                                    <th class="bg-gray-200">Producto</th>
                                    <th class="w-15 bg-gray-200">Largo</th>
                                    <th class="w-15 bg-gray-200">Cantidad</th>
                                    <th class="w-15 bg-gray-200">Costo</th>
                                    <th class="w-15 bg-gray-200">Margen</th>
                                    <th class="w-10 bg-gray-200">
                                    <IconSettings size="20" stroke="1.5" />
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="box in stockItem.box_items">
                                    <td class="p-1">
                                        <ProductImage :product="box" style="height: 30px;"/>
                                        {{ box.product_name }} {{ box.product_variety }}
                                    </td>
                                    <td class="p-1">
                                        <input 
                                            type="number"
                                            v-model="box.length"
                                            @change="(event) => {formatInteger(event);updateBoxItem(box)}"
                                            step="1" 
                                            class="form-control text-end"
                                            :class="{'text-danger border-danger': box.length <= 0}" 
                                        />
                                    </td>
                                    <td class="p-1">
                                        <input 
                                            type="number"
                                            v-model="box.qty_stem_flower"
                                            @change="(event) => {formatInteger(event);updateBoxItem(box)}"
                                            step="1" 
                                            class="form-control text-end"
                                            :class="{'text-danger border-danger': box.qty_stem_flower <= 0}" 
                                        />
                                    </td>
                                    <td class="p-1">
                                        <input 
                                            type="number"
                                            v-model="box.stem_cost_price"
                                            @change="(event) => {formatNumber(event);updateBoxItem(box)}"
                                            step="0.01" 
                                            class="form-control text-end"
                                            :class="{'text-danger border-danger': box.stem_cost_price <= 0}" 
                                        />
                                    </td>
                                    <td class="p-1">
                                        <input 
                                            type="number"
                                            v-model="box.margin"
                                            @change="(event) => {formatNumber(event);updateBoxItem(box)}"
                                            step="0.01" 
                                            class="form-control text-end"
                                            :class="{'text-danger border-danger': box.margin <= 0}" 
                                        />
                                    </td>
                                    <td class="text-center p-1">
                                        <button class="btn btn-sm btn-default">
                                            <IconTrash size="20" stroke="1.5" :class="{'text-danger':confirmDelete}" @click="updateBoxItem(box,true)"/>
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="col-12" v-if="tabShowIdx.tabAddProduct">
                        <div class="row">
                            <div class="d-flex justify-content-between  pt-2 pb-5 gap-2 h-40">
                                <div class="w-50">
                                    <Autocomplete/>
                                    <div v-if="baseStore.selectedProduct">
                                        <img v-if="baseStore.selectedProduct.image" :src="appConfig.apiBaseUrl + baseStore.selectedProduct.image" :alt="baseStore.selectedProduct.name" class="img-thumbnail" style="height: 200px; width: auto;">
                                        <img v-else :src="appConfig.imgPlaceholder" alt="En Espera" class="img-thumbnail" style="height: 200px; width: auto;">
                                    </div>
                                    <div v-else>
                                        <img :src="appConfig.imgPlaceholder" alt="En Espera" class="img-thumbnail" style="height: 200px; width: auto;">
                                    </div>
                            </div>
                        </div>
                            <div class="col-2">
                                <div class="input-group mb-3">
                                    <span class="input-group-text">Tallos</span>
                                    <input
                                        type="number"
                                        v-model="newBoxItem.qty_stem_flower"
                                        @change="formatInteger" 
                                        step="1" 
                                        class="form-control text-end"
                                        :class="{'text-danger border-danger': newBoxItem.qty_stem_flower <= 0}"
                                        />
                                </div>
                            </div>
                            <div class="col-2">
                                <div class="input-group mb-3">
                                    <span class="input-group-text">Largo</span>
                                    <input
                                        type="number"
                                        v-model="newBoxItem.length"
                                        @change="formatInteger" 
                                        step="1" 
                                        class="form-control text-end"
                                        :class="{'text-danger border-danger': newBoxItem.length <= 0}"
                                        />
                                </div>
                            </div>
                            <div class="col-3">
                                <div class="input-group mb-3">
                                    <span class="input-group-text">Costo Tallo</span>
                                    <input
                                        type="number"
                                        v-model="newBoxItem.stem_cost_price"
                                        @change="formatNumber" 
                                        step="0.01" 
                                        class="form-control text-end"
                                        :class="{'text-danger border-danger': newBoxItem.stem_cost_price <= 0}"
                                        />
                                </div>
                            </div>
                            <div class="col-2">
                                <div class="input-group mb-3">
                                    <span class="input-group-text">Margen</span>
                                    <input
                                        type="number"
                                        v-model="newBoxItem.margin"
                                        @change="formatNumber" 
                                        step="0.01" 
                                        class="form-control text-end"
                                        :class="{'text-danger border-danger': newBoxItem.margin <= 0}"
                                        />
                                </div>
                            </div>
                            <div class="col-2">
                                <div class="input-group mb-3">
                                    <span class="input-group-text">Precio</span>
                                    <input
                                        type="number"
                                        :value="(newBoxItem.stem_cost_price + newBoxItem.margin)" 
                                        class="form-control text-end"
                                        :class="{'text-danger border-danger': newBoxItem.margin + newBoxItem.stem_cost_price <= 0}"
                                        />
                                </div>
                            </div>
                            <div class="col-12 mt-2">
                                <button class="btn btn-sm btn-default" :disabled="!isValidData" @click="createBoxItem">
                                    <IconPlus size="20" stroke="1.5" />
                                    Agregar Producto
                                </button>
                            </div>
                        </div>

                    </div>
                </div>
                   </div>
                </div>
                <div class="modal-footer bg-secondary bg-gradient p-1">
                    <button type="button" class="btn btn-default btn-sm" data-bs-dismiss="modal">
                        <IconX size="20" stroke="1.5" />
                        Cerrar Ventana
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
