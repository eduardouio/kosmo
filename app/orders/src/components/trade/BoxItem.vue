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

// Función mejorada para comparar objetos y evitar actualizaciones innecesarias
const isEqual = (a, b) => {
    if (a === b) return true;
    try {
        return JSON.stringify(a) === JSON.stringify(b);
    } catch {
        return false;
    }
}

// Watchers mejorados con manejo de estado updating para evitar recursión
watch(() => props.modelValue, (val) => {
    if (!updating.value) {
        updating.value = true;
        newboxItem.value = JSON.parse(JSON.stringify(val));
        setTimeout(() => {
            updating.value = false;
        }, 10);
    }
}, { deep: true })

watch(newboxItem, (val) => {
    if (!updating.value && !isEqual(val, props.modelValue)) {
        updating.value = true;
        emit('update:modelValue', JSON.parse(JSON.stringify(val)));
        setTimeout(() => {
            updating.value = false;
        }, 10);
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

// Modificar la función selectProduct para garantizar que todos los valores necesarios estén inicializados
const selectProduct = ($event) => {
    updating.value = true;
    const productValue = $event;
    
    // Crear un nuevo objeto para evitar referencias mutables, asegurando valores por defecto
    newboxItem.value = {
        ...newboxItem.value,
        product: productValue,
        stem_cost_price: newboxItem.value.stem_cost_price || '0.00',
        profit_margin: newboxItem.value.profit_margin || '0.00',
        qty_stem_flower: newboxItem.value.qty_stem_flower || 0,
        total: newboxItem.value.total || '0.00'
    };
    
    setTimeout(() => {
        updating.value = false;
    }, 10);
}

// Modificada para preparar el campo para edición - guarda el valor anterior y elimina formato
const onFocusField = (field) => {
    previousValues.value[field] = newboxItem.value[field];
    
    // Si es un campo numérico con formato, eliminar el formato al entrar
    if (field === 'stem_cost_price' || field === 'profit_margin') {
        const cleanValue = newboxItem.value[field].toString().replace(/,/g, '');
        newboxItem.value[field] = cleanValue;
    }
};

// Compute the total safely with null checks
const calculateTotal = computed(() => {
    console.log('Propiesdad conputada caculateTotal');
    const priceStr = newboxItem.value?.stem_cost_price?.toString() || '0';
    const marginStr = newboxItem.value?.profit_margin?.toString() || '0';
    
    const price = parseFloat(priceStr.replace(/,/g, '')) || 0;
    const margin = parseFloat(marginStr.replace(/,/g, '')) || 0;
    
    const total = price + margin;
    return baseStore.formatInputNumber(total.toFixed(2));
});

const onBlurField = (field, format = false) => {
    console.log('Propiesdad al avandonart el input');
    if (newboxItem.value[field] === '' || newboxItem.value[field] === null) {
        newboxItem.value[field] = previousValues.value[field];
    } else if (format) {
        // Clean the input and format it properly
        const cleanValue = newboxItem.value[field].toString().replace(/,/g, '');
        const numValue = parseFloat(cleanValue);
        if (!isNaN(numValue)) {
            newboxItem.value[field] = baseStore.formatInputNumber(numValue.toFixed(2));
        }
    }
    
    // Actualizar inmediatamente el total después de salir del campo
    if (field === 'stem_cost_price' || field === 'profit_margin') {
        newboxItem.value.total = calculateTotal.value;
    }  
};

// Watch for changes in calculation fields and update total - with additional safety checks
watch([
    () => newboxItem.value?.stem_cost_price,
    () => newboxItem.value?.qty_stem_flower,
    () => newboxItem.value?.profit_margin
], () => {
    // Solo actualizar si newboxItem existe y tiene todas las propiedades necesarias
    if (newboxItem.value && 
        newboxItem.value.stem_cost_price !== undefined && 
        newboxItem.value.profit_margin !== undefined) {
        newboxItem.value.total = calculateTotal.value;
    }
}, { deep: true });

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