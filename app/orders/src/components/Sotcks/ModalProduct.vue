<script setup>
import { IconX, IconFlower, IconRuler, IconCurrencyDollar, IconPalette, IconHash } from '@tabler/icons-vue';
import ProductImage from '@/components/Sotcks/ProductImage.vue';
const props = defineProps(['product']);
</script>

<template>
  <div class="modal fade modal-lg" id="productModal" tabindex="-1" aria-labelledby="productModal" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content" v-if="product">
        <!-- Header -->
        <div class="modal-header header-soft-primary py-2">
          <div class="d-flex align-items-center">
            <IconFlower size="24" stroke="1.5" class="me-2 text-kosmo-secondary" />
            <div>
              <h5 class="modal-title mb-0 text-kosmo-secondary fw-bold">
                {{ product.product_name }} {{ product.product_variety }}
              </h5>
              <small class="text-kosmo-secondary opacity-75">ID: {{ product.product_id }}</small>
            </div>
          </div>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <!-- Body -->
        <div class="modal-body p-0">
          <div class="p-3">
            <!-- Product Image and Basic Info -->
            <div class="row mb-3">
              <div class="col-md-5">
                <div class="card card-soft border-0">
                  <div class="card-header header-soft-secondary py-2">
                    <h6 class="mb-0">
                      <i class="fas fa-image me-2"></i>
                      Imagen del Producto
                    </h6>
                  </div>
                  <div class="card-body p-2 text-center">
                    <ProductImage :product="product" style="width: 100%; max-height: 200px; object-fit: cover;" />
                  </div>
                </div>
              </div>
              
              <div class="col-md-7">
                <!-- Product Details -->
                <div class="card card-soft border-0 mb-3">
                  <div class="card-header header-soft-blue py-2">
                    <h6 class="mb-0">
                      <i class="fas fa-info-circle me-2"></i>
                      Información del Producto
                    </h6>
                  </div>
                  <div class="card-body p-reduced">
                    <div class="row g-2">
                      <div class="col-12">
                        <div class="info-item">
                          <IconHash size="16" stroke="1.5" class="text-muted me-2" />
                          <div>
                            <strong>Nombre</strong>
                            <div class="text-muted">{{ product.product_name }}</div>
                          </div>
                        </div>
                      </div>
                      <div class="col-12">
                        <div class="info-item">
                          <IconFlower size="16" stroke="1.5" class="text-success me-2" />
                          <div>
                            <strong>Variedad</strong>
                            <div class="text-muted">{{ product.product_variety }}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Colors Section -->
                <div class="card card-soft border-0">
                  <div class="card-header header-soft-teal py-2">
                    <h6 class="mb-0">
                      <IconPalette size="16" stroke="1.5" class="me-2" />
                      Colores Disponibles
                    </h6>
                  </div>
                  <div class="card-body p-reduced">
                    <div class="d-flex flex-wrap gap-1">
                      <span v-for="color in product.product_colors" :key="color" 
                            class="badge badge-soft-info">
                        {{ color }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Technical Specifications -->
            <div class="card card-soft border-0">
              <div class="card-header header-soft-orange py-2">
                <h6 class="mb-0">
                  <i class="fas fa-cogs me-2"></i>
                  Especificaciones Técnicas
                </h6>
              </div>
              <div class="card-body p-reduced">
                <div class="row g-3">
                  <div class="col-md-4">
                    <div class="d-flex align-items-center justify-content-center p-2 bg-soft-primary rounded">
                      <div class="text-center">
                        <IconRuler size="20" stroke="1.5" class="text-primary mb-1" />
                        <div class="h5 mb-0 text-primary">{{ product.length }} cm</div>
                        <small class="text-muted">Largo</small>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="d-flex align-items-center justify-content-center p-2 bg-soft-success rounded">
                      <div class="text-center">
                        <IconFlower size="20" stroke="1.5" class="text-success mb-1" />
                        <div class="h5 mb-0 text-success">{{ product.qty_stem_flower }}</div>
                        <small class="text-muted">Tallos</small>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="d-flex align-items-center justify-content-center p-2 bg-soft-secondary rounded">
                      <div class="text-center">
                        <IconCurrencyDollar size="20" stroke="1.5" class="text-warning mb-1" />
                        <div class="h5 mb-0 text-warning">${{ product.stem_cost_price.toFixed(2) }}</div>
                        <small class="text-muted">Costo por Tallo</small>
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
              Información del producto actualizada
            </small>
            <button class="btn btn-outline-secondary" data-bs-dismiss="modal">
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
    
    .h5 {
        font-size: 1.125rem;
    }
    
    .card-body {
        padding: 0.75rem;
    }
}

.text-teal-600 {
    color: #0d9488 !important;
}
</style>