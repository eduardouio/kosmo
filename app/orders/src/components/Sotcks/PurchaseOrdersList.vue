<script setup>
import { usePurchaseStore } from '@/stores/purcharses';
import { useBaseStore } from '@/stores/base';   
import { appConfig } from '@/AppConfig';
import { 
    IconFolderOpen, IconFolder, IconPrinter
} from '@tabler/icons-vue';

// Variables
const purchasesStore = usePurchaseStore();
const baseStore = useBaseStore();

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

const getUrlReportSupOrder = (id) => {
    let urlReportSupOrder = appConfig.urlReportSupOrder.replace('{id_order}', id);
    return urlReportSupOrder;
};

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
                    <span class="badge border" :class="{
                        'text-success': purchase.order.status === 'CONFIRMADO',
                        'text-warning': purchase.order.status === 'PENDIENTE',
                        'text-danger': purchase.order.status === 'CANCELADO',
                        'text-orange': purchase.order.status === 'MODIFICADO',
                        'text-primary': purchase.order.status === 'FACTURADO',
                    }">
                        {{ purchase.order.status }}
                    </span>
                </div>
            </li>
        </ul>
    </div>
</template>