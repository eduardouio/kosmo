<script setup>
import { ref } from 'vue'
import { useBaseStore } from '@/stores/base'

const baseStore = useBaseStore();
const products = ref(baseStore.products);


const searchTerm = ref("")
const filteredProducts = ref([])
const selectedProductId = ref(null)
const showSuggestions = ref(false)
const highlightIndex = ref(-1)

function filterProducts() {
  showSuggestions.value = searchTerm.value.length > 0
  filteredProducts.value = products.value.filter(item =>
    item.variety.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
  highlightIndex.value = -1
}

function selectProduct(product) {
  baseStore.selectedProduct = product
  selectedProductId.value = product.id
  searchTerm.value = `${product.name} - ${product.variety}`
  showSuggestions.value = false
}

function handleKeyDown(e) {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (highlightIndex.value < filteredProducts.value.length - 1) {
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
      selectProduct(filteredProducts.value[highlightIndex.value])
    }
  }
}
</script>
<template>
    <div class="position-relative mb-3">
      <input 
        type="text"
        class="form-control"
        placeholder="Buscar producto"
        v-model="searchTerm"
        @input="filterProducts"
        @keydown="handleKeyDown"
      >
      <ul 
        class="list-group position-absolute w-100"
        v-if="filteredProducts.length && showSuggestions"
        style="z-index: 1000;"
      >
        <li 
          class="list-group-item"
          :class="{'active': highlightIndex === index}"
          v-for="(product, index) in filteredProducts"
          :key="product.id"
          @click="selectProduct(product)"
        >
          {{ product.name }} - {{ product.variety }}
        </li>
      </ul>
    </div>
  </template>