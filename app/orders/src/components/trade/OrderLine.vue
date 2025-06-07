<script setup>
import { ref, watch, toRefs, computed } from 'vue'
import BoxItem from '@/components/trade/BoxItem.vue'
import { IconTrash, IconPlus, IconMinus } from '@tabler/icons-vue'
import { useSingleOrderStore } from '@/stores/trade/singleOrderStore'

const emit = defineEmits(['showProductModal', 'update:quantity', 'update:box_model', 'update:boxItems', 'remove'])

const props = defineProps({
  quantity: { type: [Number, String], default: 1 },
  box_model: { type: String, default: 'QB' },
  boxItems: { type: Array, default: () => [{}] },
})

const { quantity, box_model, boxItems } = toRefs(props)

const localQuantity = ref(quantity.value)
const localBoxModel = ref(box_model.value)
const localBoxItems = ref([...boxItems.value])
const isUpdating = ref(false)

// Computed properties para validación mejoradas
const isQuantityInvalid = computed(() => {
  const value = Number(localQuantity.value)
  return !value || value <= 0 || isNaN(value)
})

const isBoxModelInvalid = computed(() => {
  return !localBoxModel.value || localBoxModel.value.trim() === '' || localBoxModel.value === 'Seleccionar'
})

// Función para validar cada boxItem individualmente
const isBoxItemInvalid = (item) => {
  if (!item) return true
  
  const largoCm = Number(item.largo_cm)
  const bunches = Number(item.bunches)
  const tb = Number(item.tb)
  const costo = Number(item.costo)
  const margen = Number(item.margen)
  
  return !largoCm || largoCm <= 0 || isNaN(largoCm) ||
         !bunches || bunches <= 0 || isNaN(bunches) ||
         !tb || tb <= 0 || isNaN(tb) ||
         !costo || costo <= 0 || isNaN(costo) ||
         !margen || margen <= 0 || isNaN(margen)
}

// Mejorar watchers para evitar actualizaciones recursivas
watch(() => props.quantity, val => { 
  if (!isUpdating.value) {
    localQuantity.value = val 
  }
})
watch(() => props.box_model, val => { 
  if (!isUpdating.value) {
    localBoxModel.value = val 
  }
})
watch(() => props.boxItems, val => { 
  if (!isUpdating.value) {
    localBoxItems.value = [...val] 
  }
}, { deep: true })

// Optimizar emisión de eventos
watch(localQuantity, val => {
  isUpdating.value = true;
  emit('update:quantity', val);
  setTimeout(() => { isUpdating.value = false }, 10);
})
watch(localBoxModel, val => {
  isUpdating.value = true;
  emit('update:box_model', val);
  setTimeout(() => { isUpdating.value = false }, 10);
})

// Usar debounce para actualizar boxItems solo cuando sea necesario
let debounceTimer = null;
watch(localBoxItems, val => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    isUpdating.value = true;
    emit('update:boxItems', val);
    setTimeout(() => { isUpdating.value = false }, 10);
  }, 50);
}, { deep: true })

const orderStore = useSingleOrderStore()

const showProductModal = ($event) => {
  emit('showProductModal', $event)
}

const addBoxItem = () => {
  localBoxItems.value.push({})
}
const removeBoxItem = (idx) => {
  if (localBoxItems.value.length > 1) {
    localBoxItems.value.splice(idx, 1)
  }
}
const removeLine = () => {
  emit('remove')
}
</script>

<template>
  <tr>
    <td class="w-10">
      <input 
        type="number"
        :class="[
          'form-control form-control-sm text-center input-soft my-input',
          isQuantityInvalid ? 'input-error border-danger' : ''
        ]"
        min="1"
        step="1"
        v-model="localQuantity"
      >
    </td>
    <td class="w-10">
      <select 
        :class="[
          'form-control form-control-sm input-soft my-input',
          isBoxModelInvalid ? 'input-error border-danger' : ''
        ]"
        v-model="localBoxModel"
      >
        <option value="">Seleccionar</option>
        <option>EB</option>
        <option>QB</option>
        <option>HB</option>
        <option>FB</option>
      </select>
    </td>
    <td class="d-flex flex-column gap-1">
      <div v-for="(item, idx) in localBoxItems" :key="idx" class="d-flex align-items-center gap-1 mb-1">
        <BoxItem 
          v-model="localBoxItems[idx]" 
          @showProductModal="showProductModal"
          :isInvalid="isBoxItemInvalid(localBoxItems[idx])"
        />
        <IconPlus stroke="1.5" size="20" class="text-primary border-blue-400" @click="addBoxItem"/>
        <IconMinus stroke="1.5" size="20" class="text-danger border-red-500" @click="removeBoxItem(idx)"/>
      </div>
    </td>
    <td class="text-center bg-red-400 bg-gradient" style="width: 20px;">
        <IconTrash
          size="15"
          stroke="1.5"
          class="text-danger"
          @click="removeLine"
        />
    </td>
  </tr>
</template>

<style scoped>
.input-error.border-danger {
  border-color: #dc3545 !important;
  border-width: 2px !important;
}

.input-error.border-danger:focus {
  border-color: #dc3545 !important;
  box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25) !important;
}

.border {
  border: 1px solid #ced4da;
}

.border:focus {
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}
</style>