<script setup>
import { IconX, IconBuildingFactory, IconMail, IconPhone, IconWorld, IconMapPin, IconCreditCard, IconBrandSkype } from '@tabler/icons-vue';
const props = defineProps(['suplier']);
</script>

<template>
    <div class="modal fade modal-lg" id="suplierModal" tabindex="-1" aria-labelledby="suplierModal" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content" v-if="suplier">
                <!-- Header -->
                <div class="modal-header header-soft-orange py-2">
                    <div class="d-flex align-items-center">
                        <IconBuildingFactory size="50" stroke="1.5" class="me-2 text-orange-800" />
                        <div>
                            <h5 class="modal-title mb-0 text-orange-800 fw-bold">
                                {{ suplier.name }}
                                <span class="badge ms-2" :class="suplier.is_active ? 'badge-soft-success' : 'badge-soft-danger'">
                                    <i class="fas fa-circle me-1" :class="suplier.is_active ? 'text-success' : 'text-danger'"></i>
                                    {{ suplier.is_active ? 'Activo' : 'Inactivo' }}
                                </span>
                            </h5>
                            <small class="text-orange-800 opacity-75">ID: {{ suplier.id }} | Tax ID: {{ suplier.business_tax_id }}</small>
                        </div>
                    </div>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>

                <!-- Body -->
                <div class="modal-body p-0">
                    <div class="p-3">
                        <!-- Basic Information -->
                        <div class="card card-soft border-0 mb-3">
                            <div class="card-header header-soft-secondary py-2">
                                <h6 class="mb-0">
                                    <i class="fas fa-info-circle me-2"></i>
                                    Información General
                                </h6>
                            </div>
                            <div class="card-body p-reduced">
                                <div class="row g-2">
                                    <div class="col-md-6">
                                        <div class="info-item">
                                            <IconMapPin size="16" stroke="1.5" class="text-muted me-2" />
                                            <div>
                                                <strong>Dirección</strong>
                                                <div class="text-muted">{{ suplier.address }}</div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="info-item">
                                            <i class="fas fa-city text-muted me-2"></i>
                                            <div>
                                                <strong>Ciudad</strong>
                                                <div class="text-muted">{{ suplier.city }}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Contact Information -->
                        <div class="card card-soft border-0 mb-3">
                            <div class="card-header header-soft-blue py-2">
                                <h6 class="mb-0">
                                    <i class="fas fa-address-book me-2"></i>
                                    Información de Contacto
                                </h6>
                            </div>
                            <div class="card-body p-reduced">
                                <div class="row g-2">
                                    <div class="col-md-4">
                                        <div class="info-item">
                                            <IconMail size="16" stroke="1.5" class="text-primary me-2" />
                                            <div>
                                                <strong>Email</strong>
                                                <div class="text-break">
                                                    <a :href="`mailto:${suplier.email}`" class="text-decoration-none">
                                                        {{ suplier.email || 'No registrado' }}
                                                    </a>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="info-item">
                                            <IconPhone size="16" stroke="1.5" class="text-success me-2" />
                                            <div>
                                                <strong>Teléfono</strong>
                                                <div class="text-muted">
                                                    <a :href="`tel:${suplier.phone}`" class="text-decoration-none">
                                                        {{ suplier.phone || 'No registrado' }}
                                                    </a>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="info-item">
                                            <IconBrandSkype size="16" stroke="1.5" class="text-info me-2" />
                                            <div>
                                                <strong>Skype</strong>
                                                <div class="text-muted">{{ suplier.skype || 'No registrado' }}</div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-12" v-if="suplier.website">
                                        <div class="info-item">
                                            <IconWorld size="16" stroke="1.5" class="text-warning me-2" />
                                            <div>
                                                <strong>Sitio Web</strong>
                                                <div>
                                                    <a :href="suplier.website" target="_blank" class="text-decoration-none">
                                                        {{ suplier.website }}
                                                        <i class="fas fa-external-link-alt ms-1"></i>
                                                    </a>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Financial Information -->
                        <div class="card card-soft border-0">
                            <div class="card-header header-soft-teal py-2">
                                <h6 class="mb-0">
                                    <i class="fas fa-dollar-sign me-2"></i>
                                    Información Financiera
                                </h6>
                            </div>
                            <div class="card-body p-reduced">
                                <div class="row g-3">
                                    <div class="col-md-4">
                                        <div class="d-flex align-items-center justify-content-center p-2 bg-soft-success rounded">
                                            <div class="text-center">
                                                <div class="h4 mb-0 text-success">{{ suplier.default_profit_margin }}%</div>
                                                <small class="text-muted">Margen Base</small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="d-flex align-items-center justify-content-center p-2 bg-soft-secondary rounded">
                                            <div class="text-center">
                                                <div class="h5 mb-1">
                                                    <span class="badge" :class="suplier.is_profit_margin_included ? 'badge-soft-success' : 'badge-soft-warning'">
                                                        {{ suplier.is_profit_margin_included ? 'Incluido' : 'No Incluido' }}
                                                    </span>
                                                </div>
                                                <small class="text-muted">Margen en Precio</small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="d-flex align-items-center justify-content-center p-2 bg-soft-orange rounded">
                                            <div class="text-center">
                                                <IconCreditCard size="20" stroke="1.5" class="text-warning mb-1" />
                                                <div class="fw-bold">{{ suplier.credit_term || 'Contado' }}</div>
                                                <small class="text-muted">Términos de Crédito</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer -->
                <div class="modal-footer bg-soft-secondary p-2">
                    <div class="d-flex justify-content-between align-items-center w-100">
                        <small class="text-muted">
                            <i class="fas fa-info-circle me-1"></i>
                            Información del proveedor actualizada
                        </small>
                        <button class="btn btn-outline-secondary btn-sm" data-bs-dismiss="modal">
                            <IconX size="16" stroke="1.5" class="me-1" />
                            Cerrar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.info-item {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.5rem 0;
}

.info-item strong {
    display: block;
    font-size: 0.875rem;
    color: #374151;
    margin-bottom: 0.125rem;
}

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

.text-break {
    word-break: break-word;
}

.btn-close-white {
    filter: invert(1) grayscale(100%) brightness(200%);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .modal-dialog {
        margin: 0.5rem;
    }
    
    .info-item {
        padding: 0.25rem 0;
    }
    
    .h4 {
        font-size: 1.25rem;
    }
    
    .card-body {
        padding: 0.75rem;
    }
}
</style>
