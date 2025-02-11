<script setup>
import { usePurchaseStore } from '@/stores/purcharses';
import { useBaseStore } from '@/stores/base';   
import { IconTrash, IconFolderOpen, IconFolder  } from '@tabler/icons-vue';

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
</script>

<template>
<div class="row">
    <div class="col-12 pt-3">
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th class="p-1 text-center"># OC</th>
                                <th class="p-1 text-center">Fecha</th>
                                <th class="p-1 text-center">Proveedor</th>
                                <th class="p-1 text-center">HB/QB</th>
                                <th class="p-1 text-center">Estado</th>
                                <th class="p-1 text-center">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="purchase in purchasesStore.purcharses_by_order" :key="purchase" @click="selectPurchase(purchase.order.id)">
                                <td class="p-1 text-center">{{ purchase.order.id }}</td>
                                <td class="p-1">{{ baseStore.formatDate(purchase.order.date) }}</td>
                                <td class="p-1">{{ purchase.order.partner.name }}</td>
                                <td class="p-1 text-center">{{ purchase.order.hb_total }}/{{ purchase.order.qb_total }}</td>
                                <td class="p-1">{{ purchase.order.status }}</td>
                                <td class="p-1 d-flex justify-content-end gap-3">
                                    <IconFolderOpen size="20" class="text-sky-600"  stroke="1.5" v-if="purchase.is_selected"/>
                                    <IconFolder size="20"  stroke="1.5" v-else/>
                                    <IconTrash size="20"  stroke="1.5"/>
                                </td>
                            </tr>
                        </tbody>
                    </table>
        </div>
    </div>
</div>
</template>
