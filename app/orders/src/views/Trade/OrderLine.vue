<script setup>
import { computed, defineProps } from 'vue'
import AutocompleteProduct from '@/components/common/AutocompleteProduct.vue'
import { ref } from 'vue'
import { useInvoiceStore } from '@/stores/trade/orders-trade';

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

const store = useInvoiceStore();
const lineIndex = computed(() => props.lineIndex);
const normalizedLine = computed(() => store.normalizeLine(props.line));
const newBoxItem = ref({
  product: null,
  length: '',
  stems_bunch: 0,
  total_bunches: 0,
  qty_stem_flower: 0,
  stem_cost_price: 0
});

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
    <td>
      <input type="number" class="form-control form-control-sm" min="1" v-model.number="normalizedLine.quantity">
    </td>
    <td>
      <select class="form-select form-select-sm" v-model="normalizedLine.box_model">
        <option>HB</option>
        <option>FB</option>
        <option>QB</option>
      </select>
    </td>
    <td colspan="7">
      <div class="d-flex gap-2 align-items-center mb-2">
        <AutocompleteProduct @select="p => newBoxItem.product = p" :placeholder="'Buscar producto...'" />
        <input type="number" class="form-control form-control-sm" v-model="newBoxItem.length" placeholder="Length" style="width: 80px">
        <input type="number" class="form-control form-control-sm" v-model="newBoxItem.stems_bunch" placeholder="Stems/Bunch" style="width: 100px">
        <input type="number" class="form-control form-control-sm" v-model="newBoxItem.total_bunches" placeholder="Total Bunches" style="width: 100px">
        <input type="number" class="form-control form-control-sm" v-model="newBoxItem.qty_stem_flower" placeholder="Total Stems" style="width: 100px">
        <input type="number" class="form-control form-control-sm" v-model="newBoxItem.stem_cost_price" placeholder="Stem Cost Price" style="width: 100px">
        <button class="btn btn-primary btn-sm" @click="addBoxItem">+</button>
      </div>
      <table v-if="normalizedLine.box_items.length" class="table table-sm table-bordered mb-0">
        <thead>
          <tr class="text-center small">
            <th>Variety</th>
            <th>Length</th>
            <th>Stems/Bunch</th>
            <th>Total Bunches</th>
            <th>Total Stems</th>
            <th>Stem Cost Price</th>
            <th>Total</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(prod, idx) in normalizedLine.box_items" :key="idx" class="text-end small">
            <td>{{ prod.product?.name || '' }}{{ prod.product?.variety ? ' - ' + prod.product.variety : '' }}</td>
            <td>{{ prod.length }}</td>
            <td>{{ prod.stems_bunch }}</td>
            <td>{{ prod.total_bunches }}</td>
            <td>{{ prod.qty_stem_flower }}</td>
            <td>{{ prod.stem_cost_price }}</td>
            <td>{{ (prod.qty_stem_flower * prod.stem_cost_price).toFixed(2) }}</td>
            <td><button class="btn btn-danger btn-sm" @click="removeBoxItem(idx)"><i class="bi bi-trash"></i></button></td>
          </tr>
        </tbody>
      </table>
    </td>
    <td class="form-control form-control-sm text-end" style="width: 100px">
      00
    </td>
    <td class="text-center">
      <button class="btn btn-danger btn-sm" @click="$emit('remove')">
        <i class="bi bi-trash"></i>
      </button>
    </td>
  </tr>
</template>
