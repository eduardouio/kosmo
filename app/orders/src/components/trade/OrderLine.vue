<script setup>
import { ref, watch, toRefs, computed } from 'vue'
import BoxItem from '@/components/trade/BoxItem.vue'
import { IconTrash, IconPlus, IconMinus } from '@tabler/icons-vue'
import { useSingleOrderStore } from '@/stores/trade/singleOrderStore'

const emit = defineEmits(['showProductModal', 'update:quantity', 'update:box_model', 'update:boxItems', 'remove', 'updateLineTotal'])

const props = defineProps({
  quantity: { type: [Number, String], default: 1 },
  box_model: { type: String, default: 'QB' },
  boxItems: { type: Array, default: () => [{}] },
  line_total: { type: Number, default: 0 }
})

const { quantity, box_model, boxItems } = toRefs(props)

const localQuantity = ref(quantity.value)
const localBoxModel = ref(box_model.value)
const localBoxItems = ref([...boxItems.value])

watch(() => props.quantity, val => { localQuantity.value = val })
watch(() => props.box_model, val => { localBoxModel.value = val })
watch(() => props.boxItems, val => { localBoxItems.value = [...val] })

watch(localQuantity, val => emit('update:quantity', val))
watch(localBoxModel, val => emit('update:box_model', val))
watch(localBoxItems, val => emit('update:boxItems', val), { deep: true })

const orderStore = useSingleOrderStore()

// Watch para recalcular el total de la línea cuando cambian los items
watch([localQuantity, localBoxModel, localBoxItems], () => {
  // Calcula el total usando la función del store, pasando los valores actuales
  const tempLine = {
    quantity: localQuantity.value,
    box_model: localBoxModel.value,
    order_box_items: localBoxItems.value
  }
  emit('updateLineTotal', tempLine)
}, { deep: true })

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
        class="border w-100 text-center"
        min="1"
        step="1"
        v-model="localQuantity"
      >
    </td>
    <td class="w-10">
      <select class="border w-100" v-model="localBoxModel">
        <option>QB</option>
        <option>HB</option>
        <option>FB</option>
      </select>
    </td>
    <td class="d-flex flex-column gap-1">
      <div v-for="(item, idx) in localBoxItems" :key="idx" class="d-flex align-items-center gap-1 mb-1">
        <BoxItem v-model="localBoxItems[idx]" @showProductModal="showProductModal" />
        <IconPlus stroke="1.5" size="20" class="text-primary border-blue-400" @click="addBoxItem"/>
        <IconMinus stroke="1.5" size="20" class="text-danger border-red-500" @click="removeBoxItem(idx)"/>
      </div>
    </td>
    <td class="text-end">
      {{ line_total.toFixed(2) }}
    </td> 
    <td class="text-center" style="width: 20px;">
        <IconTrash
          size="15"
          stroke="1.5"
          class="text-danger"
          @click="removeLine"
        />
    </td>
  </tr>
</template>
