<template>
  <div>
    <input
      type="text"
      class="form-control"
      v-model="search"
      @input="onInput"
      :placeholder="placeholder"
      @focus="showListAndHighlightFirst"
      @blur="hideList"
      @keydown="onKeydown"
    />
    <ul v-if="showList && filteredCustomers.length" 
        class="list-group position-absolute w-100 z-3 autocomplete-list"
        :style="{ maxWidth: '300px' }"
    >
      <li
        v-for="(customer, idx) in filteredCustomers"
        :key="customer.id"
        class="list-group-item list-group-item-action"
        :class="{ 'active': idx === highlightedIndex }"
        @mousedown.prevent="selectCustomer(customer)"
      >
        {{ customer.name }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useBaseStore } from '@/stores/baseStore.js'

const props = defineProps({
  placeholder: {
    type: String,
    default: 'Buscar cliente...'
  },
  initialValue: {
    type: String,
    default: ''
  }
})
const emit = defineEmits(['select'])

const baseStore = useBaseStore()
const search = ref('')
const showList = ref(false)
const highlightedIndex = ref(-1)
const selecting = ref(false)  // Flag para evitar actualizaciones recursivas

// Inicializar el valor de búsqueda cuando el componente se monta
onMounted(() => {
  if (props.initialValue) {
    search.value = props.initialValue
  }
})

// Observar cambios en initialValue para actualizar el campo
watch(() => props.initialValue, (newValue) => {
  if (newValue && !selecting.value) {
    search.value = newValue
  }
})

const filteredCustomers = computed(() => {
  if (!search.value) return baseStore.customers
  return baseStore.customers.filter(c =>
    c.name.toLowerCase().includes(search.value.toLowerCase())
  )
})

function selectCustomer(customer) {
  if (!customer || !customer.name || selecting.value) {
    // Evitar errores si el cliente es undefined o está en proceso de selección
    return;
  }
  
  selecting.value = true;
  
  // Usar nextTick para diferir las actualizaciones y evitar ciclos
  nextTick(() => {
    search.value = customer.name
    showList.value = false
    highlightedIndex.value = -1
    
    // Emitir el evento después de actualizar el estado local
    emit('select', customer)
    
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
  if (!showList.value || !filteredCustomers.value.length || selecting.value) return
  
  if (e.key === 'ArrowDown') {
    highlightedIndex.value = (highlightedIndex.value + 1) % filteredCustomers.value.length
    e.preventDefault()
  } else if (e.key === 'ArrowUp') {
    highlightedIndex.value = (highlightedIndex.value - 1 + filteredCustomers.value.length) % filteredCustomers.value.length
    e.preventDefault()
  } else if (e.key === 'Enter') {
    if (highlightedIndex.value >= 0 && highlightedIndex.value < filteredCustomers.value.length) {
      e.preventDefault()
      selectCustomer(filteredCustomers.value[highlightedIndex.value])
    }
  } else if (e.key === 'Escape') {
    showList.value = false
    e.preventDefault()
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
