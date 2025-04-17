<template>
  <div>
    <input
      type="text"
      class="form-control"
      v-model="search"
      @input="onInput"
      :placeholder="placeholder"
      @focus="showList = true"
      @blur="hideList"
      @keydown="onKeydown"
    />
    <ul v-if="showList && filteredSuppliers.length" 
        class="list-group position-absolute w-100 z-3 autocomplete-list"
        :style="{ maxWidth: '300px' }"
    >
      <li
        v-for="(supplier, idx) in filteredSuppliers"
        :key="supplier.id"
        class="list-group-item list-group-item-action"
        :class="{ 'active': idx === highlightedIndex }"
        @mousedown.prevent="selectSupplier(supplier)"
      >
        {{ supplier.name }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useBaseStore } from '@/stores/baseStore.js'

const props = defineProps({
  placeholder: {
    type: String,
    default: 'Buscar proveedor...'
  }
})
const emit = defineEmits(['select'])

const baseStore = useBaseStore()
const search = ref('')
const showList = ref(false)
const highlightedIndex = ref(-1)

const filteredSuppliers = computed(() => {
  if (!search.value) return baseStore.suppliers
  return baseStore.suppliers.filter(s =>
    s.name.toLowerCase().includes(search.value.toLowerCase())
  )
})

function selectSupplier(supplier) {
  search.value = supplier.name
  emit('select', supplier)
  showList.value = false
  highlightedIndex.value = -1
}

function onInput() {
  showList.value = true
  highlightedIndex.value = 0
}

function hideList() {
  setTimeout(() => { showList.value = false }, 150)
}

function onKeydown(e) {
  if (!showList.value || !filteredSuppliers.value.length) return
  if (e.key === 'ArrowDown') {
    highlightedIndex.value = (highlightedIndex.value + 1) % filteredSuppliers.value.length
    e.preventDefault()
  } else if (e.key === 'ArrowUp') {
    highlightedIndex.value = (highlightedIndex.value - 1 + filteredSuppliers.value.length) % filteredSuppliers.value.length
    e.preventDefault()
  } else if (e.key === 'Enter') {
    if (highlightedIndex.value >= 0 && highlightedIndex.value < filteredSuppliers.value.length) {
      selectSupplier(filteredSuppliers.value[highlightedIndex.value])
      e.preventDefault()
    }
  }
}
</script>

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
