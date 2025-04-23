<script setup>
import { ref, computed, nextTick } from 'vue'
import { useBaseStore } from '@/stores/baseStore.js'

const props = defineProps({
  placeholder: {
    type: String,
    default: 'Buscar producto...'
  }
})
const emit = defineEmits(['selectProduct'])

const baseStore = useBaseStore()
const search = ref('')
const showList = ref(false)
const highlightedIndex = ref(-1)
const selecting = ref(false)

const filteredProducts = computed(() => {
  if (!search.value) return baseStore.products
  return baseStore.products.filter(p =>
    p.variety.toLowerCase().includes(search.value.toLowerCase())
  )
})

function selectProduct(product) {
  if (!product || !product.variety || selecting.value) {
    // Evita errores si el producto es undefined o no tiene variety
    // O si ya estamos en proceso de selección
    return;
  }
  
  selecting.value = true;
  
  // Usar nextTick para diferir las actualizaciones y evitar ciclos
  nextTick(() => {
    console.log('Selected product:', product)
    search.value = product.variety
    showList.value = false
    highlightedIndex.value = -1
    
    // Emitir el evento después de actualizar el estado local
    emit('selectProduct', product)
    
    // Permitir nuevas selecciones después de un breve retraso
    setTimeout(() => {
      selecting.value = false;
    }, 50);
  });
}

function showListAndHighlightFirst() {
  if (!selecting.value) {
    showList.value = true
    highlightedIndex.value = 0
  }
}

function onInput() {
  if (!selecting.value) {
    showList.value = true
    highlightedIndex.value = 0
  }
}

function hideList() {
  // Usar un pequeño retraso para permitir que el clic se procese primero
  setTimeout(() => {
    if (!selecting.value) {
      showList.value = false
    }
  }, 150);
}

function onKeydown(e) {
  if (!showList.value || !filteredProducts.value.length || selecting.value) return
  
  if (e.key === 'ArrowDown') {
    highlightedIndex.value = (highlightedIndex.value + 1) % filteredProducts.value.length
    e.preventDefault()
  } else if (e.key === 'ArrowUp') {
    highlightedIndex.value = (highlightedIndex.value - 1 + filteredProducts.value.length) % filteredProducts.value.length
    e.preventDefault()
  } else if (e.key === 'Enter') {
    if (highlightedIndex.value >= 0 && highlightedIndex.value < filteredProducts.value.length) {
      e.preventDefault()
      selectProduct(filteredProducts.value[highlightedIndex.value])
    }
  } else if (e.key === 'Escape') {
    showList.value = false
    e.preventDefault()
  }
}
</script>
<template>
  <div>
    <input
      type="text"
      v-model="search"
      class="border w-100" 
      @input="onInput"
      :placeholder="placeholder"
      @focus="showListAndHighlightFirst"
      @blur="hideList"
      @keydown="onKeydown"
    />
    <ul v-if="showList && filteredProducts.length" 
        class="list-group position-absolute w-100 z-3 autocomplete-list mt-1 ms-1"
        :style="{ maxWidth: '500px' }"
    >
      <li
        v-for="(product, idx) in filteredProducts"
        :key="product.id"
        class="list-group-item list-group-item-action"
        :class="{ 'active': idx === highlightedIndex }"
        @mousedown.prevent="selectProduct(product)"
      >
        {{ product.variety }}
      </li>
    </ul>
  </div>
</template>
<style scoped>
.list-group {
  max-height: 200px;
  overflow-y: auto;
}

.autocomplete-list {
  max-width: 300px;
  min-width: 180px;
}

.list-group-item.active {
  background-color: #007bff;
  color: white;
}
</style>
