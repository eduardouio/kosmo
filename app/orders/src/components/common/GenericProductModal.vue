<script setup>
import { IconX } from '@tabler/icons-vue';
import ProductImage from '@/components/Sotcks/ProductImage.vue';
const props = defineProps(['product']);

</script>
<template>
  <div class="modal fade modal" id="productModal" tabindex="-1" aria-labelledby="productModal" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content" v-if="product">
        <div class="modal-header bg-kosmo-primary p-1 text-white">
          <span class="modal-title fs-6 ps-3" id="productModal">
            # {{ product.id }} -
            {{ product.name }} {{ product.variety }}
          </span>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="row">
            <div class="col-5 d-flex justify-content-center">
              <ProductImage :product="product" style="height: 100%;" />
            </div>
            <div class="col-7 fs-6">
              <div class="row border shdow">
                <div class="col-5 pb-2 border-bottom border-end text-end bg-gray-200">Nombre:</div>
                <div class="col-7 pb-2 border-bottom">{{ product.name }}</div>
                <div class="col-5 pb-2 border-bottom border-end text-end bg-gray-200">Variedad:</div>
                <div class="col-7 pb-2 border-bottom">{{ product.variety }}</div>
                <div class="col-5 pb-2 border-bottom border-end text-end bg-gray-200">Colores:</div>
                <div class="col-7 pb-2 border-bottom">
                  <span v-if="Array.isArray(product.colors)">
                    <span v-for="color in product.colors" :key="color">
                      <small>{{ color }}</small><br />
                    </span>
                  </span>
                  <span v-else>
                    <small>{{ product.colors }}</small>
                  </span>
                </div>
                <div class="col-5 pb-2 border-bottom border-end text-end bg-gray-300">Margen de ganancia:</div>
                <div class="col-7 pb-2 border-bottom">{{ product.default_profit_margin }}</div>
                <div class="col-5 pb-2 border-bottom border-end text-end bg-gray-300">ID:</div>
                <div class="col-7 pb-2 border-bottom">{{ product.id }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer bg-secondary bg-gradient p-1">
          <button class="btn bnt-sm btn-default" data-bs-dismiss="modal">
                        <IconX  size="20" stroke="1.5" />
                        Cerrar
                    </button>
        </div>
      </div>
    </div>
  </div>
</template>