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
        if (purchase?.order?.id === id) {
            purchase.is_selected = true;
            purchasesStore.selectedPurchase = purchase;
        } else {
            purchase.is_selected = false;
        }
    });
};

// Lifecycle
onMounted(() => {
    // Verificar que hay datos y que el primer elemento tiene la estructura esperada
    if (purchasesStore.purcharses_by_order?.length > 0 && 
        purchasesStore.purcharses_by_order[0]?.order?.id) {
        selectPurchase(purchasesStore.purcharses_by_order[0].order.id);
    }
});

</script>

<template>
    <div>
        <div v-if="!purchasesStore.purcharses_by_order || purchasesStore.purcharses_by_order.length === 0" 
             class="text-center p-3 text-muted">
            <p>No hay órdenes de compra disponibles</p>
        </div>
        <ul class="list-group" v-else>
            <li v-for="purchase in purchasesStore.purcharses_by_order" 
                :key="purchase?.order?.id || purchase.id"
                class="list-group-item d-flex gap-2 align-items-center cursor-pointer"
                @click="selectPurchase(purchase?.order?.id)"
                :class="{'bg-orange-700 text-white': purchase.is_selected}">
                <strong>OC #{{ purchase?.order?.id || 'N/A' }}</strong>
                <div class="d-flex align-items-center gap-2">
                    <IconFolderOpen size="20" class="text-sky-600" stroke="1.5" v-if="purchase.is_selected" />
                    <IconFolder size="20" stroke="1.5" v-else />
                </div>
            </li>
        </ul>
    </div>
</template>