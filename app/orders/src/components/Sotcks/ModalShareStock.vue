<script setup>
import { watch, onMounted } from 'vue';
import { useBaseStore } from '@/stores/baseStore.js';
import { useOrdersStore } from '@/stores/ordersStore.js';
import { useStockStore } from '@/stores/stockStore.js';
import { IconClipboard, IconX, IconShare, IconUsers, IconInnerShadowBottomLeft, IconAlertCircle } from '@tabler/icons-vue';
import AutocompleteCustomer from './AutocompleteCustomer.vue';

const baseStore = useBaseStore();
const orderStore = useOrdersStore();
const stockStore = useStockStore();

const copyToClipboard = () => {
    const textArea = document.querySelector('textarea');
    textArea.select();
    navigator.clipboard.writeText(stockStore.stockText);
}

// Regenerar el texto cuando se abra el modal
onMounted(() => {
    stockStore.stockToText();
});

watch(() => orderStore.selectedCustomer, (newValue) => {
    if (newValue) {
        stockStore.selectedCustomer = newValue;
        stockStore.stockToText();
    }
});

// Watch para regenerar texto cuando cambie la selección de stock
watch(() => stockStore.stock, () => {
    stockStore.stockToText();
}, { deep: true });
</script>

<template>
    <div class="modal fade modal-lg" id="shareModal" tabindex="-1" aria-labelledby="shareModal" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <!-- Header -->
                <div class="modal-header header-soft-blue py-2">
                    <div class="d-flex align-items-center">
                        <IconShare size="24" stroke="1.5" class="me-2 text-cyan-800" />
                        <div>
                            <h5 class="modal-title mb-0 text-cyan-800 fw-bold">
                                Compartir Disponibilidad
                            </h5>
                            <small class="text-cyan-800 opacity-75">Generar reporte de stock personalizado</small>
                        </div>
                    </div>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>

                <!-- Body -->
                <div class="modal-body p-3">
                    <!-- Customer Selection -->
                    <div class="card card-soft border-0 mb-3">
                        <div class="card-header header-soft-secondary py-2">
                            <h6 class="mb-0">
                                <i class="fas fa-user-tag me-2"></i>
                                Seleccionar Cliente
                            </h6>
                        </div>
                        <div class="card-body p-reduced">
                            <AutocompleteCustomer />
                        </div>
                    </div>

                    <!-- Related Suppliers Section -->
                    <div class="card card-soft border-0 mb-3" v-if="stockStore.selectedCustomer">
                        <div class="card-header header-soft-orange py-2 d-flex justify-content-between align-items-center">
                            <h6 class="mb-0">
                                <IconUsers size="16" stroke="1.5" class="me-2" />
                                <span v-if="stockStore.selectedCustomer.id === 'all'">Todos los Proveedores</span>
                                <span v-else>Proveedores Relacionados</span>
                            </h6>
                            <!-- Botón para ver todo el stock -->
                            <button v-if="stockStore.selectedCustomer.id !== 'all'" 
                                    type="button" 
                                    class="btn btn-outline-secondary btn-sm"
                                    @click="() => { stockStore.selectedCustomer = { id: 'all', name: 'Todos los clientes' }; stockStore.stockToText(); }">
                                <i class="fas fa-globe me-1"></i>
                                Ver Todo
                            </button>
                        </div>
                        <div class="card-body p-reduced">
                            <!-- Opción "Todos" seleccionada -->
                            <div v-if="stockStore.selectedCustomer.id === 'all'">
                                <div class="alert alert-soft-info d-flex align-items-center">
                                    <i class="fas fa-globe me-2"></i>
                                    <span>Se mostrará el stock completo de todos los proveedores disponibles sin filtros</span>
                                </div>
                                <div class="mt-2">
                                    <small class="text-muted">
                                        <i class="fas fa-info-circle me-1"></i>
                                        Para filtrar por cliente específico, utilice el selector de cliente arriba.
                                    </small>
                                </div>
                            </div>
                            
                            <!-- Cliente específico con proveedores relacionados -->
                            <div v-else-if="stockStore.selectedCustomer.related_partners && stockStore.selectedCustomer.related_partners.length > 0">
                                <div class="alert alert-soft-success d-flex align-items-center mb-2">
                                    <IconInnerShadowBottomLeft size="16" stroke="1.5" class="me-2" />
                                    <small>Este cliente tiene {{ stockStore.selectedCustomer.related_partners.length }} proveedor(es) relacionado(s)</small>
                                </div>
                                <div class="d-flex flex-wrap gap-2">
                                    <span v-for="supplier in stockStore.selectedCustomer.related_partners" 
                                          :key="supplier.id"
                                          class="badge badge-soft-secondary px-2 py-1">
                                        <strong>#{{ supplier.id }}</strong> {{ supplier.name }}
                                    </span>
                                </div>
                            </div>
                            
                            <!-- Cliente sin proveedores relacionados -->
                            <div v-else class="alert alert-soft-warning d-flex align-items-center">
                                <IconAlertCircle size="16" stroke="1.5" class="me-2" />
                                <div>
                                    <span>Este cliente no tiene proveedores relacionados</span>
                                    <div class="mt-1">
                                        <small class="text-muted">Se mostrará el stock completo disponible</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Stock Text Preview -->
                    <div class="card card-soft border-0">
                        <div class="card-header header-soft-teal py-2">
                            <h6 class="mb-0">
                                <i class="fas fa-file-text me-2"></i>
                                Vista Previa del Reporte
                            </h6>
                        </div>
                        <div class="card-body p-reduced">
                            <div class="position-relative">
                                <textarea class="form-control input-soft" 
                                          v-model="stockStore.stockText" 
                                          readonly 
                                          rows="15"
                                          style="font-family: monospace; font-size: 0.875rem; resize: vertical;"
                                          placeholder="Seleccione productos en el inventario para generar el reporte..."></textarea>
                                <div class="position-absolute top-0 end-0 m-2">
                                    <button type="button" 
                                            class="btn btn-outline-primary btn-sm" 
                                            @click="copyToClipboard()"
                                            title="Copiar al portapapeles"
                                            :disabled="!stockStore.stockText || stockStore.stockText === 'Sin Seleccion'">
                                        <IconClipboard size="14" stroke="1.5" />
                                    </button>
                                </div>
                            </div>
                            <div class="text-muted mt-2">
                                <small>
                                    <i class="fas fa-info-circle me-1"></i>
                                    El reporte se genera automáticamente basado en los productos seleccionados y el cliente elegido.
                                    <span v-if="!stockStore.stockText || stockStore.stockText === 'Sin Seleccion'">
                                        <strong>Seleccione productos en el inventario principal.</strong>
                                    </span>
                                </small>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer -->
                <div class="modal-footer bg-soft-secondary p-2">
                    <div class="d-flex justify-content-between align-items-center w-100">
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>
                            Reporte generado automáticamente
                        </small>
                        <div class="d-flex gap-2">
                            <button type="button" 
                                    class="btn btn-outline-primary btn-sm" 
                                    @click="copyToClipboard()"
                                    :disabled="!stockStore.stockText || stockStore.stockText === 'Sin Seleccion'">
                                <IconClipboard size="16" stroke="1.5" class="me-1" />
                                Copiar
                            </button>
                            <button type="button" 
                                    class="btn btn-outline-secondary btn-sm" 
                                    data-bs-dismiss="modal">
                                <IconX size="16" stroke="1.5" class="me-1" />
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.modal-content {
    border-radius: 8px;
    border: none;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.modal-header {
    border-radius: 8px 8px 0 0;
    border-bottom: none;
}

.modal-footer {
    border-radius: 0 0 8px 8px;
    border-top: 1px solid #e5e7eb;
}

.card {
    border-radius: 6px;
}

.card-header {
    border-radius: 6px 6px 0 0;
}

.badge {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
}

.btn-close-white {
    filter: invert(1) grayscale(100%) brightness(200%);
}

.position-relative textarea {
    padding-right: 3rem;
}

.alert {
    border-radius: 6px;
    padding: 0.75rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .modal-dialog {
        margin: 0.5rem;
    }
    
    .card-body {
        padding: 0.75rem;
    }
    
    textarea {
        font-size: 0.75rem !important;
    }
}

/* Better textarea styling */
textarea.form-control {
    border: 1px solid #d1d5db;
    background-color: #f9fafb;
}

textarea.form-control:focus {
    border-color: #6366f1;
    box-shadow: 0 0 0 0.2rem rgba(99, 102, 241, 0.25);
}
</style>