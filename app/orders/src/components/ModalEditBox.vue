<script setup>
import { ref, watch } from 'vue';
import { useBaseStore } from '@/stores/base';
import { useStockStore } from '@/stores/stock';
import { 
    IconX,
    IconCheck,
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

</script>
<template>
    <div class="modal fade modal-xl" id="editBoxModal" tabindex="-1" aria-labelledby="editBoxModal" aria-hidden="true" v-if="!baseStore.isLoading && stockItem">
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
                        <ul class="nav nav-tabs">
                        <li class="nav-item">
                            <a class="nav-link" aria-current="page" href="#" @click="changeTab('tabEditBox')" :class="{'active': tabShowIdx.tabEditBox}">
                                <IconEdit size="20" stroke="1.5" />
                                Modificar Contenido de Caja
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
                                    <th>Producto</th>
                                    <th class="w-15">Largo</th>
                                    <th class="w-15">Cantidad</th>
                                    <th class="w-15">Costo</th>
                                    <th class="w-15">Margen</th>
                                    <th class="w-10">
                                    <IconSettings size="20" stroke="1.5" />
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="box in stockItem.box_items">
                                    <td>
                                        {{ box.product_name }} {{ box.product_variety }}
                                    </td>
                                    <td>
                                        <input 
                                            type="number"
                                            v-model="box.length"
                                            @change="(event) => {formatInteger(event);updateBoxItem(box)}"
                                            step="1" 
                                            class="form-control text-end"
                                            :class="{'text-danger border-danger': box.length <= 0}" 
                                        />
                                    </td>
                                    <td>
                                        <input 
                                            type="number"
                                            v-model="box.qty_stem_flower"
                                            @change="(event) => {formatInteger(event);updateBoxItem(box)}"
                                            step="1" 
                                            class="form-control text-end"
                                            :class="{'text-danger border-danger': box.qty_stem_flower <= 0}" 
                                        />
                                    </td>
                                    <td>
                                        <input 
                                            type="number"
                                            v-model="box.stem_cost_price"
                                            @change="(event) => {formatNumber(event);updateBoxItem(box)}"
                                            step="0.01" 
                                            class="form-control text-end"
                                            :class="{'text-danger border-danger': box.stem_cost_price <= 0}" 
                                        />
                                    </td>
                                    <td>
                                        <input 
                                            type="number"
                                            v-model="box.margin"
                                            @change="(event) => {formatNumber(event);updateBoxItem(box)}"
                                            step="0.01" 
                                            class="form-control text-end"
                                            :class="{'text-danger border-danger': box.margin <= 0}" 
                                        />
                                    </td>
                                    <td class="text-center">
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
                            <div class="col-6">
                                <div class="input-group mb-3">
                                    <span class="input-group-text">Producto</span>
                                    <select class="form-select" v-model="newProduct">
                                        <option v-for="product in products" :value="product.id">
                                            {{ product.name }} {{ product.variety }}
                                        </option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-3">
                                <div class="input-group mb-3">
                                    <span class="input-group-text">Largo</span>
                                    <input type="number" v-model="newLength" @change="formatInteger" step="1" class="form-control text-end" />
                                </div>
                            </div>
                            <div class="col-3">
                                <div class="input-group mb-3">
                                    <span class="input-group-text">Cantidad</span>
                                    <input type="number" v-model="newQtyStemFlower" @change="formatInteger" step="1" class="form-control text-end" />
                                </div>
                            </div>
                            <div class="col-3">
                                <div class="input-group mb-3">
                                    <span class="input-group-text">Costo</span>
                                    <input type="number" v-model="newStemCostPrice" @change="formatNumber" step="0.01" class="form-control text-end" />
                                </div>
                            </div>
                            <div class="col-3">
                                <div class="input-group mb-3">
                                    <span class="input-group-text">Margen</span>
                                    <input type="number" v-model="newMargin" @change="formatNumber" step="0.01" class="form-control text-end" />
                                </div>
                            </div>
                            <div class="col-3">
                                <button class="btn btn-sm btn-default">
                                    <IconPlus size="20" stroke="1.5" />
                                    Agregar Producto
                                </button>
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
