<script setup>
import {ref, computed} from 'vue';
import { useBaseStore } from '@/stores/base';
import { useStockStore } from '@/stores/stock';
import { IconClipboard, IconX  } from '@tabler/icons-vue';

const baseStore = useBaseStore();
const stockStore = useStockStore();

const copyToClipboard = () => {
    const textArea = document.querySelector('textarea');
    textArea.select();
    navigator.clipboard.writeText(stockStore.stockText);
}

</script>

<template>
    <div class="modal fade modal-lg" id="shareModal" tabindex="-1" aria-labelledby="shareModal" aria-hidden="true" v-if="!baseStore.isLoading">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-kosmo-primary p-1 text-white">
                    <span class="modal-title fs-6 ps-3" id="shareModal">
                        Compartir Disponibilidad
                    </span>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                   <textarea class="form-control" v-model="stockStore.stockText" readonly rows="20"></textarea>
                </div>
                <div class="modal-footer bg-secondary bg-gradient p-1">
                    <button type="button" class="btn btn-default btn-sm" data-bs-dismiss="modal">
                        <IconX size="20" stroke="1.5" />
                        Cerrar
                    </button>
                    <button type="button" class="btn btn-default btn-sm" @click="copyToClipboard()">
                        <IconClipboard size="20" stroke="1.5" />
                        Copiar
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
