<script setup>
import { usePurchaseStore } from '@/stores/purcharsesStore.js';
import { onMounted } from 'vue';
import { 
    IconFolderOpen, IconFolder
} from '@tabler/icons-vue';

// Variables
const purchasesStore = usePurchaseStore();

// Methods
const selectPurchase = (id) => {
    purchasesStore.selectedPurchase = {};
    purchasesStore.purcharses_by_order.forEach((purchase) => {
        if (purchase.order.id === id) {
            purchase.is_selected = true;
            purchasesStore.selectedPurchase =  purchase;
        }else{
            purchase.is_selected = false;
        }
        });
};

// Lifecycle
onMounted(() => {
    selectPurchase(purchasesStore.purcharses_by_order[0].order.id);
});

</script>

<template>
    <div>
        <ul class="list-group">
            <li v-for="purchase in purchasesStore.purcharses_by_order" 
                :key="purchase"
                class="list-group-item d-flex gap-2 align-items-center cursor-pointer"
                @click="selectPurchase(purchase.order.id)"
                :class="{'bg-orange-700 text-white': purchase.is_selected}">
                <strong>OC #{{ purchase.order.id }}</strong>
                <div class="d-flex align-items-center gap-2">
                    <IconFolderOpen size="20" class="text-sky-600" stroke="1.5" v-if="purchase.is_selected" />
                    <IconFolder size="20" stroke="1.5" v-else />
                </div>
            </li>
        </ul>
    </div>
</template>