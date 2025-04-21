<script setup>
import { ref } from 'vue'
import { computed, defineProps } from 'vue'
import BoxItem from '@/components/trade/BoxItem.vue'
import { IconTrash } from '@tabler/icons-vue'

const props = defineProps({
  line: {
    type: Object,
    required: true
  },
  lineIndex: {
    type: Number,
    required: true
  }
})

const lineIndex = computed(() => props.lineIndex);
const normalizedLine = computed(() => store.normalizeLine(props.line));

function addBoxItem() {
  store.addBoxItem(lineIndex.value, newBoxItem.value);
  newBoxItem.value = { product: null, length: '', stems_bunch: 0, total_bunches: 0, qty_stem_flower: 0, stem_cost_price: 0 };
}

function removeBoxItem(idx) {
  store.removeBoxItem(lineIndex.value, idx);
}

const totalLine = computed(() => store.calculateTotalLine(lineIndex.value));

</script>
<template>
  <tr>
    <td class="bg-gray-200 w-10">

      <input type="number" class="form-control form-control-sm" min="1" model.number="normalizedLine.quantity">
    </td>
    <td class="w-10">
      <select class="form-select form-select-sm" model="normalizedLine.box_model">
        <option>QB</option>
        <option>HB</option>
        <option>FB</option>
      </select>
    </td>
    <td>
     <BoxItem/>
    </td>
    <td class="text-end">
      00
    </td>
    <td class="text-center" style="width: 20px;">
        <IconTrash size="15" stroke="1.5" @click="$emit('remove')"/>
    </td>
  </tr>
</template>
