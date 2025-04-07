<script setup>
import { ref } from 'vue';
import { useBaseStore } from '@/stores/base';

const baseStore = useBaseStore();
baseStore.loadSuppliers();

const suppliers = ref(baseStore.suppliers);
const searchTerm = ref("");
const filteredSuppliers = ref([]);
const selectedSupplierId = ref(null);
const showSuggestions = ref(false);
const highlightIndex = ref(-1);

function filterSuppliers() {
    showSuggestions.value = searchTerm.value.length > 0;
    filteredSuppliers.value = suppliers.value.filter(supplier =>
        supplier.name.toLowerCase().includes(searchTerm.value.toLowerCase())
    );
    highlightIndex.value = -1;
}

function selectSupplier(supplier) {
    baseStore.selectedSupplier = supplier;
    selectedSupplierId.value = supplier.id;
    searchTerm.value = supplier.name;
    showSuggestions.value = false;
}

function handleKeyDown(e) {
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (highlightIndex.value < filteredSuppliers.value.length - 1) {
            highlightIndex.value++;
        }
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (highlightIndex.value > 0) {
            highlightIndex.value--;
        }
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (highlightIndex.value >= 0) {
            selectSupplier(filteredSuppliers.value[highlightIndex.value]);
        }
    }
}

</script>
<template>
    <div class="position-relative mb-3">
        <input 
            type="text"
            class="form-control"
            placeholder="Buscar proveedor"
            v-model="searchTerm"
            @input="filterSuppliers"
            @keydown="handleKeyDown"
            autofocus
        >
        <ul 
            v-if="showSuggestions && filteredSuppliers.length"
            class="list-group position-absolute w-100 bg-white shadow rounded-3 mt-1"
        >
            <li 
                v-for="(supplier, index) in filteredSuppliers"
                :key="supplier.id"
                @click="selectSupplier(supplier)"
                @mouseover="highlightIndex = index"
                :class="{ 'list-group-item': true, 'active': highlightIndex === index }"
            >
                {{ supplier.name }}
            </li>
        </ul>
    </div>
</template>