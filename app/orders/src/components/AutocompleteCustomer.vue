<script setup>
import { ref } from 'vue'
import { useOrdersStore } from '@/stores/orders';

const ordersStore = useOrdersStore();
const customers = ref(ordersStore.customers);

const searchTerm = ref("")
const filteredCustomers = ref([])
const selectedCustomerId = ref(null)
const showSuggestions = ref(false)
const highlightIndex = ref(-1)

function filterCustomers() {
  showSuggestions.value = searchTerm.value.length > 0
  filteredCustomers.value = customers.value.filter(customer =>
    customer.name.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
  highlightIndex.value = -1
}

function selectCustomer(customer) {
  ordersStore.selectedCustomer = customer
  selectedCustomerId.value = customer.id
  searchTerm.value = customer.name
  showSuggestions.value = false
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
  }
}
</script>

<template>
  <div class="position-relative mb-3">
    <input 
      type="text"
      class="form-control"
      placeholder="Buscar cliente"
      v-model="searchTerm"
      @input="filterCustomers"
      @keydown="handleKeyDown"
      autofocus
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
</template>
