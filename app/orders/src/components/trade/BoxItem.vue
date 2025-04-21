<script setup>
import { computed, defineProps, ref } from 'vue'
import AutocompleteProduct from '@/components/common/AutocompleteProduct.vue'
import { useBaseStore } from '@/stores/baseStore';

const baseStore = useBaseStore();
const selectedProduct = ref(null)
const selectProduct = ($event) => {
    selectedProduct.value = product
    console.log('Product selected in BoxItem:', product)  
}

const newboxItem = ref({
    product: null,
    length: '0',
    qty_stem_flower: 0,
    stem_cost_price: '0.00',
    profit_margin: '0.00',
    commission: '0.00',
    total_bunches: 0,
    total: '0.00',
    stems_bunch: 0
});

// Variables temporales para respaldar valores previos
const previousValues = ref({
    length: '',
    qty_stem_flower: '',
    stem_cost_price: '',
    profit_margin: ''
});

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
    if (field === 'stem_cost_price' || field === 'qty_stem_flower') {
        const price = parseFloat(newboxItem.value.stem_cost_price) || 0;
        const qty = parseFloat(newboxItem.value.qty_stem_flower) || 0;
        newboxItem.value.total = baseStore.formatInputNumber(price * qty);
    }

    newboxItem.value.total = baseStore.formatInputNumber(
        parseFloat(newboxItem.value.stem_cost_price) + parseFloat(newboxItem.value.profit_margin)
    );
    
};

</script>
<template>
    <div class="container-fluid">
        <div class="row">
            <div class="d-flex align-items-center justify-between gap-1 p-0">
                <div style="width:55%;">
                    <AutocompleteProduct @selectProduct="selectProduct" />
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
                        />
                </div>
            </div>
        </div>
    </div>
</template>