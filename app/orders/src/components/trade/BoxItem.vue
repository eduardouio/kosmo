<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import AutocompleteProduct from '@/components/common/AutocompleteProduct.vue'
import { useBaseStore } from '@/stores/baseStore';
import { IconWindowMaximize } from '@tabler/icons-vue';
const baseStore = useBaseStore()

const emit = defineEmits(['showProductModal', 'update:modelValue'])
const props = defineProps({
    modelValue: {
        type: Object,
        default: () => ({
            product: null,
            length: '0',
            qty_stem_flower: 0,
            stem_cost_price: '0.00',
            profit_margin: '0.00',
            commission: '0.00',
            total_bunches: 0,
            total: '0.00',
            stems_bunch: 0
        })
    }
})

const newboxItem = ref({ ...props.modelValue })
const updating = ref(false)

watch(() => props.modelValue, (val) => {
    if (!updating.value) {
        newboxItem.value = { ...val }
    }
}, { deep: true })

const isEqual = (a, b) => {
    // Comparación profunda simple para objetos planos
    return JSON.stringify(a) === JSON.stringify(b);
};

watch(newboxItem, (val) => {
    if (!isEqual(val, props.modelValue) && !updating.value) {
        updating.value = true;
        nextTick(() => {
            emit('update:modelValue', val);
            updating.value = false;
        });
    }
}, { deep: true })

const previousValues = ref({
    length: '',
    qty_stem_flower: '',
    stem_cost_price: '',
    profit_margin: ''
});

const showProductModal = (product)=>{
    console.log('Activamos el modal del ', product)
    emit('showProductModal', product)
}

const selectProduct = ($event) => {
    updating.value = true;
    nextTick(() => {
        newboxItem.value.product = $event;
        console.log('Product selected in BoxItem:', $event);
        updating.value = false;
    });
}

const onFocusField = (field) => {
    previousValues.value[field] = newboxItem.value[field];
    newboxItem.value[field] = '';
};

const onBlurField = (field, format = false) => {
    if (newboxItem.value[field] === '' || newboxItem.value[field] === null) {
        newboxItem.value[field] = previousValues.value[field];
    } else if (format) {
        newboxItem.value[field] = baseStore.formatInputNumber(newboxItem.value[field]);
    }
    
    // Corregido: Actualizar el total solo cuando cambian campos relevantes
    if (field === 'stem_cost_price' || field === 'qty_stem_flower' || field === 'profit_margin') {
        const price = parseFloat(newboxItem.value.stem_cost_price) || 0;
        const qty = parseFloat(newboxItem.value.qty_stem_flower) || 0;
        const margin = parseFloat(newboxItem.value.profit_margin) || 0;
        
        // El total debe ser (precio + margen) * cantidad
        updating.value = true;
        newboxItem.value.total = baseStore.formatInputNumber(price + margin);
        nextTick(() => {
            updating.value = false;
        });
    }  
};

// Calcular el nombre del producto para mostrar en el autocomplete
const productInitialValue = computed(() => {
    if (newboxItem.value.product) {
        return `${newboxItem.value.product.name} ${newboxItem.value.product.variety}`.trim();
    }
    return '';
});
</script>
<template>
    <div class="container-fluid">
        <div class="row">
            <div class="d-flex align-items-center justify-between gap-1 p-0">
                <div class="d-flex align-items-center">
                    <IconWindowMaximize
                        v-if="newboxItem.product"
                        stroke="1.5"
                        size="15"
                        class="text-primary"
                        @click="showProductModal(newboxItem.product)"
                         data-bs-toggle="modal"
                         data-bs-target="#productModal"
                        />
                </div>
                <div style="width:55%;">
                    <AutocompleteProduct 
                        @selectProduct="selectProduct" 
                        :initialValue="productInitialValue"
                    />
                </div>
                <div style="width:10%" class="text-end">
                    <input 
                        type="number"
                        v-model="newboxItem.length"
                        class="border w-100 text-end" 
                        step="1" 
                        @focus="onFocusField('length')"
                        @blur="onBlurField('length')"
                    />
                </div>
                <div style="width:10%" class="text-end">
                    <input 
                        type="number"
                        v-model="newboxItem.qty_stem_flower"
                        class="border w-100 text-end" 
                        step="1"
                        @focus="onFocusField('qty_stem_flower')"
                        @blur="onBlurField('qty_stem_flower')"
                    />
                </div>
                <div style="width:10%" class="text-end">
                    <input 
                        type="text"
                        v-model="newboxItem.stem_cost_price"
                        class="border w-100 text-end"
                        @focus="onFocusField('stem_cost_price')"
                        @blur="onBlurField('stem_cost_price', true)" />
                </div>
                <div style="width:10%" class="text-end">
                    <input 
                        type="text"
                        v-model="newboxItem.profit_margin"
                        class="border w-100 text-end" 
                        @focus="onFocusField('profit_margin')"
                        @blur="onBlurField('profit_margin', true)"
                        />
                </div>
                <div style="width:10%" class="text-end">
                    <input 
                        type="text"
                        v-model="newboxItem.total"
                        class="border w-100 text-end" 
                        readonly
                        tabindex="-1"
                        />
                </div>
            </div>
        </div>
    </div>
</template>