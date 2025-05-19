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
            length: 0,
            qty_stem_flower: 0,
            stem_cost_price: 0,
            profit_margin: 0,
            commission: 0,
            total_bunches: 0,
            stems_bunch: 0,
            total: 0
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
    
    // Asegurarse de que el producto no se pierda durante la actualización
    // Creamos una copia profunda para evitar problemas de referencia
    const productCopy = JSON.parse(JSON.stringify(productValue));
    
    // Crear un nuevo objeto con una copia completa para evitar referencias mutables
    newboxItem.value = {
        ...newboxItem.value,
        product: productCopy,
        stem_cost_price: newboxItem.value.stem_cost_price || '0.00',
        profit_margin: newboxItem.value.profit_margin || '0.00',
        qty_stem_flower: newboxItem.value.qty_stem_flower || 0,
        total: newboxItem.value.total || '0.00'
    };
    
    // Emitir el evento update:modelValue fuera del watcher para asegurar la actualización inmediata
    // sin depender del ciclo reactivo normal
    nextTick(() => {
        emit('update:modelValue', JSON.parse(JSON.stringify(newboxItem.value)));
        setTimeout(() => {
            updating.value = false;
        }, 50); // Aumentar el tiempo para asegurar que otras actualizaciones se completen
    });
}

// Simplificar la función onFocusField para eliminar el manejo de eventos
const onFocusField = (field) => {
    // Guardamos el valor actual antes de cualquier modificación
    previousValues.value[field] = newboxItem.value[field];
    
    // Si es un campo numérico con formato, eliminar el formato al entrar
    if (field === 'stem_cost_price' || field === 'profit_margin') {
        const cleanValue = newboxItem.value[field].toString().replace(/,/g, '');
        newboxItem.value[field] = cleanValue;
    }
};

const onBlurField = (field, format = false) => {
    // Si el campo está vacío y es stems_bunch, verificamos si bunches tiene valor
    if ((newboxItem.value[field] === '' || newboxItem.value[field] === null) && field === 'stems_bunch') {
        // Si bunches tiene valor, forzar el valor por defecto 25
        const bunches = parseInt(newboxItem.value.total_bunches) || 0;
        if (bunches > 0) {
            newboxItem.value[field] = 25;
        } else {
            // Si no tiene bunches, recuperar el valor anterior
            newboxItem.value[field] = previousValues.value[field];
        }
    } 
    // Para los demás campos, comportamiento normal
    else if (newboxItem.value[field] === '' || newboxItem.value[field] === null) {
        newboxItem.value[field] = previousValues.value[field];
    }    
    // Cuando total_bunches tiene un valor > 0 pero stems_bunch es 0, asignar 25
    if (field === 'total_bunches') {
        const bunches = parseInt(newboxItem.value.total_bunches) || 0;
        if (bunches > 0) {
            const stemsBunch = parseInt(newboxItem.value.stems_bunch) || 0;
            if (stemsBunch === 0) {
                newboxItem.value.stems_bunch = 25;
                // Forzar la actualización inmediatamente para evitar problemas de sincronización
                nextTick(() => {
                    // Asegurar que el valor se mantenga
                    if (parseInt(newboxItem.value.stems_bunch) === 0) {
                        newboxItem.value.stems_bunch = 25;
                    }
                });
            }
            // Actualizar la cantidad de tallos (qty_stem_flower)
            newboxItem.value.qty_stem_flower = bunches * (stemsBunch || 25);
        }
    }
    
    // Asegurar stems_bunch > 0 cuando bunches > 0
    if (field === 'stems_bunch') {
        const bunches = parseInt(newboxItem.value.total_bunches) || 0;
        let stemsBunch = parseInt(newboxItem.value.stems_bunch) || 0;
        
        // Si bunches tiene valor pero stems_bunch es 0, forzar el valor por defecto
        if (bunches > 0 && stemsBunch === 0) {
            stemsBunch = 25;
            newboxItem.value.stems_bunch = stemsBunch;
        }
        
        // Actualizar qty_stem_flower solo si ambos tienen valores
        if (bunches > 0 && stemsBunch > 0) {
            newboxItem.value.qty_stem_flower = bunches * stemsBunch;
        }
    }
    
    // Actualizar el total después de salir del campo
    if (field === 'stem_cost_price' || field === 'profit_margin') {
        const currentTotal = newboxItem.value.total;
        const newTotal = calculateTotal.value;
        if (currentTotal !== newTotal) {
            newboxItem.value.total = newTotal;
        }
    }
};

// Compute the total safely with null checks - Eliminamos console.log
const calculateTotal = computed(() => {
    // Eliminamos el console.log que genera spam
    const priceStr = newboxItem.value?.stem_cost_price?.toString() || '0';
    const marginStr = newboxItem.value?.profit_margin?.toString() || '0';
    
    const price = parseFloat(priceStr.replace(/,/g, '')) || 0;
    const margin = parseFloat(marginStr.replace(/,/g, '')) || 0;
    
    const total = price + margin;
    return baseStore.formatInputNumber(total.toFixed(2));
});

watch([
    () => newboxItem.value?.stem_cost_price,
    () => newboxItem.value?.qty_stem_flower,
    () => newboxItem.value?.profit_margin
], () => {
    // Reducimos la frecuencia usando un debounce implícito
    if (updating.value) return;
    
    // Solo actualizar si newboxItem existe y tiene todas las propiedades necesarias
    if (newboxItem.value && 
        newboxItem.value.stem_cost_price !== undefined && 
        newboxItem.value.profit_margin !== undefined) {
        
        const currentTotal = newboxItem.value.total;
        const newTotal = calculateTotal.value;
        
        // Evitar actualizaciones innecesarias que podrían causar ciclos
        if (currentTotal !== newTotal) {
            newboxItem.value.total = newTotal;
        }
    }
}, { deep: true });

// Calcular el nombre del producto para mostrar en el autocomplete
const productInitialValue = computed(() => {
    if (newboxItem.value.product && newboxItem.value.product.name) {
        return `${newboxItem.value.product.name} ${newboxItem.value.product.variety || ''}`.trim();
    }
    return '';
});

// Agregar un watcher específico para el producto para asegurar que se mantenga
watch(() => props.modelValue?.product, (newProduct) => {
    if (newProduct && !updating.value) {
        // Asegurarse de que newboxItem.product se actualice correctamente
        newboxItem.value.product = JSON.parse(JSON.stringify(newProduct));
    }
}, { deep: true });
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
                        class="border w-100 text-end trade-nav-input" 
                        step="1" 
                    />
                </div>
                 <div style="width:10%" class="text-end">
                    <input 
                        type="number"
                        v-model="newboxItem.total_bunches"
                        class="border w-100 text-end trade-nav-input" 
                        step="1"
                        @blur="onBlurField('total_bunches')"
                    />
                </div>
                <div style="width:10%" class="text-end">
                    <input 
                        type="number"
                        v-model="newboxItem.stems_bunch"
                        class="border w-100 text-end trade-nav-input" 
                        step="1"
                    />
                </div>
                <div style="width:10%" class="text-end">
                    <input 
                        type="text"
                        v-model="newboxItem.stem_cost_price"
                        class="border w-100 text-end trade-nav-input"
                        @blur="onBlurField('stem_cost_price', true)" />
                </div>
                <div style="width:10%" class="text-end">
                    <input 
                        type="text"
                        v-model="newboxItem.profit_margin"
                        class="border w-100 text-end trade-nav-input" 
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