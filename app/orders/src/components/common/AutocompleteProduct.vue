<script setup>
import { ref, watch, onMounted } from 'vue';
import { useBaseStore } from '@/stores/baseStore';

const emit = defineEmits(['selectProduct']);
const props = defineProps({
  initialValue: {
    type: String,
    default: ''
  }
});

const store = useBaseStore();
const searchTerm = ref(props.initialValue || '');
const showDropdown = ref(false);
const filteredProducts = ref([]);
const selectedIndex = ref(-1);
const isUpdatingFromProps = ref(false);

// Observar cambios en initialValue para actualizar searchTerm
watch(() => props.initialValue, (newValue) => {
  if (newValue !== searchTerm.value && !isUpdatingFromProps.value) {
    isUpdatingFromProps.value = true;
    searchTerm.value = newValue;
    setTimeout(() => {
      isUpdatingFromProps.value = false;
    }, 10);
  }
});

function filterProducts() {
  if (!searchTerm.value) {
    filteredProducts.value = [];
    return;
  }
  
  const search = searchTerm.value.toLowerCase();
  filteredProducts.value = store.products.filter(product => {
    const productName = `${product.name} ${product.variety}`.toLowerCase();
    return productName.includes(search);
  }).slice(0, 10); // Limitar a 10 resultados
  
  selectedIndex.value = -1;
}

function selectProduct(product) {
  // Limitar cambios reactivos
  const productValue = { ...product };
  isUpdatingFromProps.value = true;
  searchTerm.value = `${productValue.name} ${productValue.variety}`;
  showDropdown.value = false;
  
  // Emitir el evento después de actualizar los valores locales
  setTimeout(() => {
    emit('selectProduct', productValue);
    isUpdatingFromProps.value = false;
  }, 10);
}

function handleKeyDown(event) {
  if (showDropdown.value) {
    if (event.key === 'ArrowDown') {
      selectedIndex.value = Math.min(selectedIndex.value + 1, filteredProducts.value.length - 1);
      event.preventDefault();
    } else if (event.key === 'ArrowUp') {
      selectedIndex.value = Math.max(selectedIndex.value - 1, 0);
      event.preventDefault();
    } else if (event.key === 'Enter' && selectedIndex.value >= 0) {
      selectProduct(filteredProducts.value[selectedIndex.value]);
      event.preventDefault();
    } else if (event.key === 'Escape') {
      showDropdown.value = false;
      event.preventDefault();
    }
  }
}

// Nueva función para ocultar el dropdown usando setTimeout
function hideDropdown() {
  setTimeout(() => {
    showDropdown.value = false;
  }, 200);
}

watch(searchTerm, filterProducts);

// Si ya hay un valor inicial, asegurarse de que se muestre correctamente al montar
onMounted(() => {
  if (props.initialValue) {
    searchTerm.value = props.initialValue;
  }
});
</script>

<template>
  <div class="position-relative">
    <input
      type="text"
      class="form-control form-control-sm"
      v-model="searchTerm"
      @focus="showDropdown = true; filterProducts()"
      @blur="hideDropdown"
      @keydown="handleKeyDown"
      placeholder="Buscar producto..."
    />
    <div
      v-if="showDropdown && filteredProducts.length > 0"
      class="dropdown-menu show w-100 position-absolute"
      style="max-height: 250px; overflow-y: auto; z-index: 9999; top: 100%; left: 0; right: 0;"
    >
      <div
        v-for="(product, index) in filteredProducts"
        :key="product.id"
        class="dropdown-item py-1"
        :class="{ 'active': index === selectedIndex }"
        @mousedown="selectProduct(product)"
        @mouseover="selectedIndex = index"
      >
        {{ product.name }} {{ product.variety }}
      </div>
    </div>
  </div>
</template>
