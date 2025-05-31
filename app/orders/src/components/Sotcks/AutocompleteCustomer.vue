<script setup>
import { ref, watch } from 'vue'
import { useOrdersStore } from '@/stores/ordersStore.js';

const ordersStore = useOrdersStore();
const searchTerm = ref("")
const filteredCustomers = ref([])
const selectedCustomerId = ref(null)
const showSuggestions = ref(false)
const highlightIndex = ref(-1)
const isCustomerSelected = ref(false)

function filterCustomers() {
  if (!isCustomerSelected.value) {
    filteredCustomers.value = ordersStore.customers.filter(customer =>
      customer.name.toLowerCase().includes(searchTerm.value.toLowerCase())
    )
  }
  highlightIndex.value = -1
}

function selectCustomer(customer) {
  ordersStore.selectedCustomer = customer
  selectedCustomerId.value = customer.id
  searchTerm.value = customer.name
  showSuggestions.value = false
  isCustomerSelected.value = true
}

function handleKeyDown(e) {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (highlightIndex.value < filteredCustomers.value.length - 1) {
      highlightIndex.value++
    }
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    if (highlightIndex.value > 0) {
      highlightIndex.value--
    }
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (highlightIndex.value >= 0) {
      selectCustomer(filteredCustomers.value[highlightIndex.value])
    }
  } else if (e.key === 'Escape') {
    showSuggestions.value = false
  }
}

watch(() => searchTerm.value, (newValue) => {
  if (isCustomerSelected.value) {
    isCustomerSelected.value = false
    return
  }
  showSuggestions.value = newValue.length > 0
  filterCustomers()
})

const selectAllCustomers = () => {
    const allCustomersOption = {
        id: 'all',
        name: 'Todos los Clientes',
        business_tax_id: '*',
        related_partners: null // Sin filtro de proveedores
    };
    
    orderStore.selectedCustomer = allCustomersOption;
    stockStore.selectedCustomer = allCustomersOption;
    searchQuery.value = '';
    showDropdown.value = false;
    
    // Regenerar el texto del stock sin filtros
    stockStore.stockToText();
};
</script>

<template>
  <div class="position-relative mb-3" v-if="ordersStore.customers.length">
    <input 
      type="text"
      class="form-control"
      placeholder="Buscar cliente"
      v-model="searchTerm"
      @keydown="handleKeyDown"
      @focus="showSuggestions = true"
    >
    <ul 
      class="list-group position-absolute w-100"
      v-if="filteredCustomers.length && showSuggestions"
      style="z-index: 1000;"
    >
      <li 
        class="list-group-item"
        :class="{'active': highlightIndex === index}"
        v-for="(customer, index) in filteredCustomers"
        :key="customer.id"
        @click="selectCustomer(customer)"
      >
        {{ customer.name }}
      </li>
    </ul>
  </div>
  <div v-if="showDropdown && (filteredCustomers.length > 0 || searchQuery)" 
       class="dropdown-menu show position-absolute w-100 mt-1 shadow-lg border-0 rounded">
    
    <!-- Opción "Todos" -->
    <div class="dropdown-item cursor-pointer d-flex align-items-center py-2"
         @mousedown="selectAllCustomers"
         :class="{ 'bg-primary text-white': selectedCustomer?.id === 'all' }">
      <i class="fas fa-globe me-2 text-success"></i>
      <div>
        <strong>Todos los Clientes</strong>
        <small class="d-block text-muted">Mostrar stock completo sin filtrar</small>
      </div>
    </div>
    
    <div class="dropdown-divider my-1"></div>
    
    <!-- Lista de clientes filtrados -->
    <div v-for="customer in filteredCustomers" 
         :key="customer.id"
         class="dropdown-item cursor-pointer d-flex align-items-center py-2"
         @mousedown="selectCustomer(customer)"
         :class="{ 'bg-primary text-white': selectedCustomer?.id === customer.id }">
      <i class="fas fa-building me-2 text-primary"></i>
      <div>
        <strong>{{ customer.name }}</strong>
        <small class="d-block text-muted">{{ customer.business_tax_id }}</small>
      </div>
    </div>
    
    <!-- Mensaje cuando no hay resultados -->
    <div v-if="filteredCustomers.length === 0 && searchQuery" 
         class="dropdown-item-text text-muted py-3 text-center">
      <i class="fas fa-search me-2"></i>
      No se encontraron clientes
    </div>
  </div>
</template>