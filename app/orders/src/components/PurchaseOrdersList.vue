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
<div class="row">
    <div class="col-12 pt-3">
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th class="p-1 text-center"># OC</th>
                                <th class="p-1 text-center">Fecha</th>
                                <th class="p-1 text-center">Proveedor</th>
                                <th class="p-1 text-center">Estado</th>
                                <th class="p-1 text-end">Total</th>
                                <th class="p-1 text-center">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="purchase in purchasesStore.purcharses_by_order" :key="purchase">
                                <td class="p-1 text-center">{{ purchase.order.id }}</td>
                                <td class="p-1">{{ baseStore.formatDate(purchase.order.date) }}</td>
                                <td class="p-1">{{ purchase.order.partner.name }}</td>
                                <td class="p-1 text-center" 
                                    :class="{
                                        'text-green-600':purchase.order.status==='CONFIRMADO', 
                                        'text-yellow-600':purchase.order.status==='PENDIENTE',
                                        'text-red-600':purchase.order.status==='CANCELADO',
                                        'text-orange-600':purchase.order.status==='MODIFICADO'
                                }">
                                <strong>
                                    {{ purchase.order.status }}
                                </strong>
                            </td>
                                <td class="p-1 text-end">{{ baseStore.formatCurrency(purchase.order.total_price) }}</td>
                                <td class="p-1 d-flex justify-content-end gap-3">
                                    <IconFolderOpen size="20" class="text-sky-600"  stroke="1.5" v-if="purchase.is_selected"/>
                                    <IconFolder size="20"  stroke="1.5" v-else @click="selectPurchase(purchase.order.id)"/>
                                    <a :href="getUrlReportSupOrder(purchase.order.id)">
                                        <IconPrinter size="20"  stroke="1.5"/>
                                    </a>
                                </td>
                            </tr>
                        </tbody>
                    </table>
        </div>
    </div>
</div>
</template>