<script setup>
import BoxItem from '@/components/trade/BoxItem.vue'
import { IconTrash, IconPlus, IconMinus } from '@tabler/icons-vue'

const emit = defineEmits(['showProductModal'])

const showProductModal = ($event) => {
  console.log("propagacion segundo nivel")
  emit('showProductModal', $event);
}

</script>
<template>
  <tr>
    <td class="bg-gray-200 w-10">
      <input 
        type="number"
        class="border w-100 text-center"
        min="1"
        step="1"
      >
    </td>
    <td class="w-10">
      <select class="border w-100" model="normalizedLine.box_model">
        <option>QB</option>
        <option>HB</option>
        <option>FB</option>
      </select>
    </td>
    <td>
     <BoxItem @showProductModal="showProductModal"/>
    </td>
    <td class="text-end">
      00
    </td> 
    <td class="text-center" style="width: 20px;">
        <IconTrash
          size="15"
          stroke="1.5"
          class="text-danger"
          />
    </td>
  </tr>
</template>
