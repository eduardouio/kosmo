<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useStockStore } from '@/stores/stockStore.js';
import { useBaseStore } from '@/stores/baseStore.js';
import { useOrdersStore } from '@/stores/ordersStore.js';
import ModalProduct from '@/components/Sotcks/ModalProduct.vue';
import ModalSuplier from '@/components/Sotcks/ModalSuplier.vue';
import ModalShareStock from '@/components/Sotcks/ModalShareStock.vue';
import ModalUpdateValues from '@/components/Sotcks/ModalUpdateValues.vue';
import ModalEditBox from '@/components/Sotcks/ModalEditBox.vue';
import ModalOrderPreview from '@/components/Sotcks/ModalOrderPreview.vue';
import Loader from '@/components/Sotcks/Loader.vue';
import SideBar from '@/components/Sotcks/SideBar.vue';
import {
    IconCheckbox, IconSquare, IconEye, IconShare, IconLockOpen2, IconLock,
    IconCurrencyDollar, IconShoppingCart, IconSettings, IconTrash, IconEdit,
    IconPointFilled, IconPoint, IconLayersIntersect2, IconSitemap,
} from '@tabler/icons-vue';
import { 
    BOX_SIZES, 
    canSplit, 
    canMerge, 
    getMergeTarget, 
    getSplitTarget, 
    splitStems,
    getSplitQuantity,
    getMergeQuantity,
    getRemainingAfterMerge
} from '@/utils/boxUtils';

const stockStore = useStockStore();
const baseStore = useBaseStore();
const router = useRouter();
const ordersStore = useOrdersStore();
const generalIndicators = ref({});
const productSelected = ref(null);
const suplierSelected = ref(null);
const stockItemSeletec = ref(null);
const querySearch = ref('');
const buttonsVisibility = ref({
    share: false,
    all: true,
    none: false,
    cost: false,
    margin: false,
    order: false,
    delete: false,
});
const confirmDelete = ref(false);
const totalStages = 4;

// METHODS
const deleteSelected = () => {
    if (!confirmDelete.value) {
        confirmDelete.value = true;
        return;
    }
    stockStore.deleteSelected();
    setVibilityButtons();
    calcIndicators();
    confirmDelete.value = false;
}

const setVibilityButtons = () => {
    let haveSelected = stockStore.stock.some(item => item.is_selected);
    stockStore.stockToText();
    if (haveSelected) {
        buttonsVisibility.value = {
            share: true,
            all: false,
            none: true,
            cost: true,
            margin: true,
            order: true,
            delete: true,
        }
        return;
    }
    buttonsVisibility.value = {
        share: false,
        all: true,
        none: false,
        cost: false,
        margin: false,
        order: false,
        delete: false,
    }
    confirmDelete.value = false;
}

const selectText = (event) => {
    event.target.select();
}

const addToOrder = () => {
    ordersStore.newOrder = stockStore.getSelection();
    ordersStore.setLimits(stockStore.getSelection().map((i)=>{
         return {stock_detail_id:i.stock_detail_id, quantity:i.quantity}
    }));
}

const calcIndicators = () => {
    generalIndicators.value = {
        total_QB: 0,
        total_HB: 0,
        total_EB: 0,
        total_FB: 0,
        total_stems: 0,
        total_suppliers: [],
    }

    if (!stockStore.stock || stockStore.stock.length === 0) {
        return;
    }

    stockStore.stock.forEach(item => {
        generalIndicators.value.total_HB += item.box_model === 'HB' ? item.quantity : 0;
        generalIndicators.value.total_QB += item.box_model === 'QB' ? item.quantity : 0;
        generalIndicators.value.total_EB += item.box_model === 'EB' ? item.quantity : 0;
        generalIndicators.value.total_stems += item.box_items.reduce(
            (acc, box) => acc + (parseInt(box.qty_stem_flower) || 0), 0
        );
        if (!generalIndicators.value.total_suppliers.includes(item.partner.name)) {
            generalIndicators.value.total_suppliers.push(item.partner.name);
        }
    });
    
    // Calcular FB total basado en conversiones
    generalIndicators.value.total_FB = parseFloat(
        ((generalIndicators.value.total_HB / 2) + 
         (generalIndicators.value.total_QB / 4) + 
         (generalIndicators.value.total_EB / 8)).toFixed(2)
    );
}

const handleKeydown = (event, cssClass) => {
    const inputs = document.querySelectorAll(cssClass);
    const currentIndex = Array.prototype.indexOf.call(inputs, event.target);
    if (event.key === 'Enter' && currentIndex < inputs.length - 1) {
        inputs[currentIndex + 1].focus();
    }
    if (event.key === 'Enter' && event.shiftKey && currentIndex > 0) {
        inputs[currentIndex - 1].focus();
    }
}


const formatNumber = (event, box = null) => {
    let value = event.target.value;
    value = value.replace(',', '.');
    if (value === '' || value === '.' || value === ',' || isNaN(value) || value === ' ' || value === '0') {
        event.target.value = '0.00';
        return;
    }
    event.target.value = parseFloat(value).toFixed(2);
    stockStore.updateStockDetail([box]);
}

const formatInteger = (event, box = null) => {
    let value = event.target.value;
    value = value.replace(',', '.');
    if (value === '' || value === '.' || value === ',' || isNaN(value) || value === ' ' || value === '0') {
        event.target.value = '0';
        return;
    }
    event.target.value = parseInt(value);
    stockStore.updateStockDetail([box]);
}

const calcTotalStems = (box_items) => {
    let total = 0;
    box_items.forEach(item => {
        total += item.qty_stem_flower;
    });
    return total;
}

const uniqueColors = (boxItems) => {
    const allColors = boxItems.flatMap(box => box.product_colors);
    return [...new Set(allColors)];
}

// COMPUTED
const isAllLoaded = computed(() => {
    return baseStore.stagesLoaded === totalStages;
})

const filterData = computed(() => {
    return stockStore.stock.filter(item => item.is_visible);
})

const getClass = (color) => {
    if (color === null || color === undefined || color === '' || color === ' ') {
        return baseStore.colors.OTRO;
    }
    if (color in baseStore.colors) {
        return baseStore.colors[color];
    }
    return baseStore.colors.OTRO;
}

// Add computed property for merge detection
const canMergeSelected = computed(() => {
    const selectedItems = stockStore.stock.filter(item => item.is_selected);
    
    if (selectedItems.length === 0) return false;
    
    // Group by box model and supplier
    const groupedItems = {};
    selectedItems.forEach(item => {
        const key = `${item.box_model}-${item.partner.id}`;
        if (!groupedItems[key]) {
            groupedItems[key] = [];
        }
        groupedItems[key].push(item);
    });
    
    // Check if any group can be merged
    return Object.values(groupedItems).some(group => {
        const boxModel = group[0].box_model;
        const totalQuantity = group.reduce((sum, item) => sum + item.quantity, 0);
        return canMerge(boxModel, group.length, totalQuantity);
    });
});

// Watchers
watch(() => querySearch.value, (newValue) => {
    stockStore.filterStock(newValue);
    confirmDelete.value = false;
},
    { immediate: true }
);

onMounted(() => {
    baseStore.stagesLoaded = 0;
    stockStore.getStock(baseStore);
    baseStore.loadProducts(baseStore);
    ordersStore.loadCustomers(baseStore);
    baseStore.loadSuppliers();
    calcIndicators();
    setTimeout(() => {
        if (!stockStore.stock.length) {
            router.push({ name: 'import' });
        }
    }, 3000);
});

/**
 * Split a box into smaller boxes
 * @param {Object} item - The stock item to split
 */
const splitBox = (item) => {
    if (!canSplit(item.box_model)) {
        console.error('Cannot split this box size');
        return;
    }

    const targetSize = getSplitTarget(item.box_model);
    const newQuantity = getSplitQuantity(item.box_model, item.quantity);
    
    // Create the new split item
    const newItem = JSON.parse(JSON.stringify(item));
    newItem.box_model = targetSize;
    newItem.quantity = newQuantity;
    newItem.is_selected = false;
    
    // Adjust stem quantities - divide by 2 for each box_item
    newItem.box_items.forEach(boxItem => {
        const originalStems = parseInt(boxItem.qty_stem_flower) || 0;
        boxItem.qty_stem_flower = Math.floor(originalStems / 2);
    });
    
    // Remove original item and add new split items
    const itemIndex = stockStore.stock.findIndex(stockItem => stockItem === item);
    if (itemIndex !== -1) {
        stockStore.stock.splice(itemIndex, 1, newItem);
        calcIndicators();
        setVibilityButtons();
    }
};

/**
 * Merge selected boxes into larger boxes
 */
const mergeBoxes = () => {
    const selectedItems = stockStore.stock.filter(item => item.is_selected);
    
    if (selectedItems.length === 0) {
        console.error('No items selected for merge');
        return;
    }

    // Group selected items by box model and supplier
    const groupedItems = {};
    selectedItems.forEach(item => {
        const key = `${item.box_model}-${item.partner.id}`;
        if (!groupedItems[key]) {
            groupedItems[key] = [];
        }
        groupedItems[key].push(item);
    });

    // Process each group
    Object.values(groupedItems).forEach(group => {
        const boxModel = group[0].box_model;
        
        if (!canMerge(boxModel)) {
            console.error(`Cannot merge ${boxModel} boxes`);
            return;
        }

        const targetSize = getMergeTarget(boxModel);
        
        // Calculate total quantity to merge
        const totalQuantity = group.reduce((sum, item) => sum + item.quantity, 0);
        const mergedQuantity = getMergeQuantity(boxModel, totalQuantity);
        const remainingQuantity = getRemainingAfterMerge(boxModel, totalQuantity);
        
        if (mergedQuantity === 0) {
            console.error('Not enough boxes to merge');
            return;
        }

        // Create merged item based on the first item in the group
        const mergedItem = JSON.parse(JSON.stringify(group[0]));
        mergedItem.box_model = targetSize;
        mergedItem.quantity = mergedQuantity;
        mergedItem.is_selected = false;
        
        // Combine and sum box_items from all items in the group
        const combinedBoxItems = {};
        group.forEach(item => {
            item.box_items.forEach(boxItem => {
                const key = `${boxItem.product_name}-${boxItem.product_variety}-${boxItem.length}`;
                if (!combinedBoxItems[key]) {
                    combinedBoxItems[key] = JSON.parse(JSON.stringify(boxItem));
                    combinedBoxItems[key].qty_stem_flower = 0;
                }
                // Sum the stems, accounting for the quantity of each box
                combinedBoxItems[key].qty_stem_flower += 
                    (parseInt(boxItem.qty_stem_flower) || 0) * item.quantity;
            });
        });
        
        // Adjust stem quantities for the merged boxes
        Object.values(combinedBoxItems).forEach(boxItem => {
            // Double the stems and divide by the number of merged boxes
            boxItem.qty_stem_flower = Math.floor(boxItem.qty_stem_flower * 2 / mergedQuantity);
        });
        
        mergedItem.box_items = Object.values(combinedBoxItems);
        
        // Remove original items from stock
        group.forEach(item => {
            const index = stockStore.stock.findIndex(stockItem => stockItem === item);
            if (index !== -1) {
                stockStore.stock.splice(index, 1);
            }
        });
        
        // Add merged item
        stockStore.stock.push(mergedItem);
        
        // Add remaining item if there are leftover boxes
        if (remainingQuantity > 0) {
            const remainingItem = JSON.parse(JSON.stringify(group[0]));
            remainingItem.quantity = remainingQuantity;
            remainingItem.is_selected = false;
            stockStore.stock.push(remainingItem);
        }
    });
    
    calcIndicators();
    setVibilityButtons();
};

// Add these methods to handle the UI interactions
const handleSplit = (item) => {
    splitBox(item);
};

const handleMerge = () => {
    mergeBoxes();
};
</script>
<template>
    <div class="container-fluid">
        <div class="row">
            <div class="col-2 bg-opacity-75">
                <SideBar />
            </div>
            <div class="col p-1 m-1">
                <div class="row" v-if="!isAllLoaded">
                    <div class="col text-center">
                        <Loader />
                        <h6 class="text-blue-600">
                            {{ baseStore.stagesLoaded }} / {{ totalStages }}
                        </h6>
                    </div>
                </div>
                <div class="row" v-else="">
                    <div class="container">
                        <!-- Header Stats Row -->
                        <div class="row pt-1 pb-3">
                            <div class="col d-flex gap-1 justify-content-start align-items-center">
                                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                                    <span class="text-white bg-blue-600 ps-1 pe-2">
                                        Disponibilidad
                                    </span>
                                    <span class="text-secondary ps-1 pe-2">
                                        {{ stockStore.stockDay.date }}
                                    </span>
                                </div>
                                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                                    <span class="text-white bg-blue-600 ps-1 pe-2">
                                        Estado
                                    </span>
                                    <span class="text-blue-600 ps-1 pe-2">
                                        <span class="text-success" v-if="stockStore.stockDay.is_active">
                                            <IconLockOpen2 size="20" stroke="1.5" />
                                            Activa
                                        </span>
                                        <span class="text-danger" v-else>
                                            <IconLock size="20" stroke="1.5" />
                                            Inactiva
                                        </span>
                                    </span>
                                </div>
                            </div>
                            <div class="col d-flex gap-1 justify-content-end align-items-center">
                                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                                    <span class="text-white bg-blue-600 ps-1 pe-2">
                                        Proveedores
                                    </span>
                                    <span class="text-blue-600 ps-1 pe-2">
                                        <span v-if="generalIndicators.total_suppliers">
                                            {{ generalIndicators.total_suppliers.length }}
                                        </span>
                                    </span>
                                </div>
                                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                                    <span class="text-white bg-blue-600 ps-1 pe-2">
                                        Pedidos
                                    </span>
                                    <span class="text-blue-600 ps-1 pe-2">
                                        0
                                    </span>
                                </div>
                                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                                    <span class="text-white bg-blue-600 ps-1 pe-2">
                                        QB's
                                    </span>
                                    <span class="text-blue-600 ps-1 pe-2">
                                        {{ generalIndicators.total_QB }}
                                    </span>
                                </div>
                                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                                    <span class="text-white bg-blue-600 ps-1 pe-2">
                                        HB's
                                    </span>
                                    <span class="text-blue-600 ps-1 pe-2">
                                        {{ generalIndicators.total_HB }}
                                    </span>
                                </div>
                                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                                    <span class="text-white bg-blue-600 ps-1 pe-2">
                                        EB's
                                    </span>
                                    <span class="text-blue-600 ps-1 pe-2">
                                        {{ generalIndicators.total_EB }}
                                    </span>
                                </div>
                                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                                    <span class="text-white bg-blue-600 ps-1 pe-2">
                                        FB's
                                    </span>
                                    <span class="text-blue-600 ps-1 pe-2">
                                        {{ generalIndicators.total_FB }}
                                    </span>
                                </div>
                                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                                    <span class="text-white bg-blue-600 ps-1 pe-2">
                                        Tallos
                                    </span>
                                    <span class="text-blue-600 ps-1 pe-2">
                                        {{ generalIndicators.total_stems }}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <!-- Search and Actions Row -->
                        <div class="row d-flex justify-content-start p-1 rounded-1">
                            <div class="col-3">
                                <input type="text" class="form-control form-control-sm rounded-1 border-slate-500"
                                    placeholder="Buscar" v-model="querySearch">
                            </div>
                            <div class="col-2 text-start text-secondary">
                                {{ stockStore.stock.length }} Registros Totales
                            </div>
                            <div class="col-7 d-flex gap-3 justify-content-end">
                                <!-- Add merge button for selected items -->
                                <button class="btn btn-sm btn-default text-primary" 
                                        v-if="buttonsVisibility.order && canMergeSelected"
                                        @click="handleMerge">
                                    <IconLayersIntersect2 size="15" stroke="1.5" />
                                    Unificar Cajas
                                </button>
                                <button class="btn btn-sm btn-default text-danger" v-if="buttonsVisibility.delete"
                                    @click="deleteSelected">
                                    <IconTrash size="15" stroke="1.5" />
                                    <span v-if="!confirmDelete">
                                        Eliminar
                                    </span>
                                    <span v-else="">
                                        Confirmar Borrado
                                    </span>
                                </button>
                                <button class="btn btn-sm btn-default" v-if="buttonsVisibility.share" data-bs-toggle="modal"
                                    data-bs-target="#shareModal">
                                    <IconShare size="15" stroke="1.5" />
                                    Compartir
                                </button>
                                <button class="btn btn-sm btn-default" v-if="buttonsVisibility.cost" data-bs-toggle="modal"
                                    data-bs-target="#updateValuesModal">
                                    <IconCurrencyDollar size="15" stroke="1.5" />
                                    Valores
                                </button>
                                <button class="btn btn-sm btn-default" v-if="buttonsVisibility.order" data-bs-toggle="modal" data-bs-target="#orderPreviewModal" @click="addToOrder">
                                    <IconShoppingCart size="15" stroke="1.5" />
                                    Crear Pedido
                                </button>
                                <button class="btn btn-sm btn-default" v-if="buttonsVisibility.all"
                                    @click="stockStore.selectAll(true); setVibilityButtons()">
                                    <IconCheckbox size="15" stroke="1.5" />
                                    Todos
                                </button>
                                <button class="btn btn-sm btn-default" v-if="buttonsVisibility.none"
                                    @click="stockStore.selectAll(false); setVibilityButtons()">
                                    <IconSquare size="15" stroke="1.5" />
                                    Ninguno
                                </button>
                            </div>
                        </div>

                        <!-- Modern Table -->
                        <div class="row">
                            <div class="col-12">
                                <div class="card card-soft border-0">
                                    <div class="card-header header-soft-blue py-reduced">
                                        <h6 class="mb-0">
                                            <i class="fas fa-warehouse me-2"></i>
                                            Detalle de Disponibilidad {{ stockStore.stockDay.date }}
                                        </h6>
                                    </div>
                                    
                                    <div class="card-body p-0">
                                        <!-- Table Header -->
                                        <div class="table-header bg-gray-700 text-white">
                                            <div class="row g-0">
                                                <div class="col-1 border-end text-center py-2">
                                                    <small class="fw-bold">#</small>
                                                </div>
                                                <div class="col-1 border-end text-center py-2">
                                                    <small class="fw-bold">CANT</small>
                                                </div>
                                                <div class="col-1 border-end text-center py-2">
                                                    <small class="fw-bold">TALLOS</small>
                                                </div>
                                                <div class="col-2 border-end text-center py-2">
                                                    <small class="fw-bold">PROVEEDOR</small>
                                                </div>
                                                <div class="col-1 border-end text-center py-2">
                                                    <small class="fw-bold">TOTAL</small>
                                                </div>
                                                <div class="col-5 border-end bg-blue-600 py-2">
                                                    <div class="row g-0 text-center">
                                                        <div class="col" style="flex: 0 0 20%;">
                                                            <small class="fw-bold">PRODUCTO</small>
                                                        </div>
                                                        <div class="col border-start" style="flex: 0 0 15%;">
                                                            <small class="fw-bold">VARIEDAD</small>
                                                        </div>
                                                        <div class="col border-start" style="flex: 0 0 8%;">
                                                            <small class="fw-bold">LARGO</small>
                                                        </div>
                                                        <div class="col border-start" style="flex: 0 0 10%;">
                                                            <small class="fw-bold">T/CAJA</small>
                                                        </div>
                                                        <div class="col border-start" style="flex: 0 0 10%;">
                                                            <small class="fw-bold">BUNCHES</small>
                                                        </div>
                                                        <div class="col border-start" style="flex: 0 0 12%;">
                                                            <small class="fw-bold">COSTO</small>
                                                        </div>
                                                        <div class="col border-start" style="flex: 0 0 12%;">
                                                            <small class="fw-bold">MARGEN</small>
                                                        </div>
                                                        <div class="col border-start" style="flex: 0 0 13%;">
                                                            <small class="fw-bold">PVP</small>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div class="col-1 bg-green-600 text-center py-2">
                                                    <small class="fw-bold">SEL</small>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Table Body -->
                                        <div class="table-body">
                                            <div v-for="(item, index) in filterData" :key="item" 
                                                 class="order-row"
                                                 :class="{ 'bg-gray-50': index % 2 === 0 }">
                                                <div class="row g-0 align-items-center">
                                                    <!-- Index -->
                                                    <div class="col-1 border-end p-1 text-center">
                                                        <small class="text-muted">{{ index + 1 }}</small>
                                                    </div>

                                                    <!-- Quantity -->
                                                    <div class="col-1 border-end p-1">
                                                        <div class="d-flex align-items-center gap-1">
                                                            <button class="btn btn-sm btn-default border-0"
                                                                    @click="stockItemSeletec = item" 
                                                                    data-bs-toggle="modal"
                                                                    data-bs-target="#editBoxModal">
                                                                <IconEdit size="14" stroke="1.5" />
                                                            </button>
                                                            <!-- Add split button for splittable boxes -->
                                                            <button class="btn btn-sm btn-default border-0 text-primary"
                                                                    @click="handleSplit(item)"
                                                                    v-if="canSplit(item.box_model)"
                                                                    title="Dividir caja">
                                                                <IconSitemap size="14" stroke="1.5" />
                                                            </button>
                                                            <span class="fw-medium">{{ item.quantity }} {{ item.box_model }}</span>
                                                        </div>
                                                    </div>

                                                    <!-- Stems -->
                                                    <div class="col-1 border-end p-1 text-center">
                                                        <span class="fw-bold text-primary">{{ calcTotalStems(item.box_items) }}</span>
                                                    </div>

                                                    <!-- Supplier -->
                                                    <div class="col-2 border-end p-1">
                                                        <div class="d-flex align-items-center gap-1">
                                                            <small class="text-muted">#{{ item.partner.id }}</small>
                                                            <button class="btn btn-sm btn-default border-0"
                                                                    @click="suplierSelected = item.partner" 
                                                                    data-bs-toggle="modal"
                                                                    data-bs-target="#suplierModal">
                                                                <IconEye size="14" stroke="1.5" />
                                                            </button>
                                                            <small class="fw-medium">{{ item.partner.short_name }}</small>
                                                        </div>
                                                    </div>

                                                    <!-- Total -->
                                                    <div class="col-1 border-end p-1">
                                                        <div v-for="box in item.box_items" :key="box.id" class="mb-1 text-center">
                                                            <span class="fw-bold text-success">
                                                                ${{ (parseFloat(box.margin) + parseFloat(box.stem_cost_price)).toFixed(2) }}
                                                            </span>
                                                        </div>
                                                    </div>

                                                    <!-- Products -->
                                                    <div class="col-5 border-end p-1">
                                                        <div v-for="box in item.box_items" :key="box.id" class="product-row mb-1">
                                                            <div class="row g-1 align-items-center">
                                                                <div class="col" style="flex: 0 0 20%;">
                                                                    <div class="d-flex align-items-center gap-1">
                                                                        <button class="btn btn-sm btn-default border-0"
                                                                                @click="productSelected = box" 
                                                                                data-bs-toggle="modal"
                                                                                data-bs-target="#productModal">
                                                                            <IconEye size="12" stroke="1.5" />
                                                                        </button>
                                                                        <div class="d-flex align-items-center gap-1">
                                                                            <div class="d-flex gap-1">
                                                                                <span v-for="color in box.product_colors" :key="color"
                                                                                      :class="getClass(color)">
                                                                                    <IconPoint size="12" stroke="1.5" v-if="color === 'BLANCO'" />
                                                                                    <IconPointFilled size="12" stroke="1.5" v-else="" />
                                                                                </span>
                                                                            </div>
                                                                            <small class="fw-medium">{{ box.product_name }}</small>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                                <div class="col" style="flex: 0 0 15%;">
                                                                    <small class="fw-medium">{{ box.product_variety }}</small>
                                                                </div>
                                                                <div class="col text-center" style="flex: 0 0 8%;">
                                                                    <span class="badge badge-soft-info">{{ box.length }}</span>
                                                                </div>
                                                                <div class="col" style="flex: 0 0 10%;">
                                                                    <input type="number" 
                                                                           step="1" 
                                                                           class="form-control form-control-sm text-end input-soft my-input"
                                                                           @keydown="event => handleKeydown(event, '.my-input')"
                                                                           @focus="selectText" 
                                                                           @change="(event) => formatInteger(event, box)"
                                                                           @input="calcIndicators" 
                                                                           v-model="box.qty_stem_flower"
                                                                           :class="{ 
                                                                             'input-error': !box.qty_stem_flower || parseInt(box.qty_stem_flower) <= 0,
                                                                             'border-danger': !box.qty_stem_flower || parseInt(box.qty_stem_flower) <= 0
                                                                           }">
                                                                </div>
                                                                <div class="col text-center" style="flex: 0 0 10%;">
                                                                    <span class="badge badge-soft-warning">{{ box.bunches_display }}</span>
                                                                </div>
                                                                <div class="col" style="flex: 0 0 12%;">
                                                                    <input type="number" 
                                                                           step="0.01" 
                                                                           class="form-control form-control-sm text-end input-soft my-input-2"
                                                                           @keydown="event => handleKeydown(event, '.my-input-2')"
                                                                           @focus="selectText" 
                                                                           @change="(event) => formatNumber(event, box)"
                                                                           v-model="box.stem_cost_price"
                                                                           :class="{ 
                                                                             'input-error': !box.stem_cost_price || parseFloat(box.stem_cost_price) <= 0.00,
                                                                             'border-danger': !box.stem_cost_price || parseFloat(box.stem_cost_price) <= 0.00
                                                                           }">
                                                                </div>
                                                                <div class="col" style="flex: 0 0 12%;">
                                                                    <input type="number" 
                                                                           step="0.01" 
                                                                           class="form-control form-control-sm text-end input-soft my-input-3"
                                                                           @keydown="event => handleKeydown(event, '.my-input-3')"
                                                                           @focus="selectText" 
                                                                           @change="(event) => formatNumber(event, box)"
                                                                           v-model="box.margin"
                                                                           :class="{ 
                                                                             'input-error': !box.margin || parseFloat(box.margin) <= 0.00,
                                                                             'border-danger': !box.margin || parseFloat(box.margin) <= 0.00
                                                                           }">
                                                                </div>
                                                                <div class="col text-center" style="flex: 0 0 13%;">
                                                                    <span class="badge badge-soft-success">
                                                                        {{ (parseFloat(box.margin) + parseFloat(box.stem_cost_price)).toFixed(2) }}
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <!-- Selection -->
                                                    <div class="col-1 p-1 text-center">
                                                        <input type="checkbox" 
                                                               class="form-check-input"
                                                               v-model="item.is_selected"
                                                               @change="setVibilityButtons()">
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Modals -->
                        <ModalProduct :product="productSelected" />
                        <ModalSuplier :suplier="suplierSelected" />
                        <ModalEditBox :stockItem="stockItemSeletec" />
                        <ModalShareStock />
                        <ModalUpdateValues />
                        <ModalOrderPreview />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<style scoped>
.table-header {
    position: sticky;
    top: 0;
    z-index: 10;
}

.order-row {
    transition: background-color 0.15s ease;
    border-bottom: 1px solid #f1f5f9;
}

.order-row:hover {
    background-color: #f8fafc !important;
}

/* Zebra striping */
.table-body .order-row:nth-child(odd) {
    background-color: #ffffff;
}
.table-body .order-row:nth-child(even) {
    background-color: #d5eefb; /* light gray */
}

/* Intensificar el contraste al pasar el mouse sin perder el color base */
.table-body .order-row:nth-child(even):hover,
.table-body .order-row:nth-child(odd):hover {
    background-color: #e2e8f0 !important; /* slate-200 */
}

.product-row {
    padding: 0.125rem 0;
}

.cursor-pointer {
    cursor: pointer;
}

.card {
    border-radius: 6px;
}

.card-header {
    border-radius: 6px 6px 0 0 !important;
}

.badge {
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
}

input[type="checkbox"] {
    width: 14px;
    height: 14px;
}

.btn-sm {
    padding: 0.125rem 0.375rem;
    font-size: 0.75rem;
}

/* Mantener las clases my-input para la funcionalidad de navegación */
.my-input,
.my-input-2,
.my-input-3 {
    border: 1px solid #ccc;
    border-radius: 2px;
    text-align: right;
}

.input-error {
    background-color: #fff3f3;
    border-color: #f5c2c7;
}

@media (max-width: 768px) {
    .container-fluid {
        padding: 0.75rem;
    }

    .card-body {
        padding: 0.75rem;
    }
}
</style>