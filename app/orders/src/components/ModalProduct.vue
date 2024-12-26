<script setup>
import { appConfig } from '@/AppConfig';
const props = defineProps(['product']);

</script>
<template>
  <div class="modal fade modal-lg" id="productModal" tabindex="-1" aria-labelledby="productModal" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content" v-if="product">
        <div class="modal-header bg-kosmo-primary p-1 text-white">
          <span class="modal-title fs-6 ps-3" id="productModal">
            # {{ product.product_id }} -
            {{ product.product_name }} {{ product.product_variety }}
          </span>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="row">
            <div class="col-5">
              <img :src="appConfig.apiBaseUrl + product.product_image" :alt="product.product_name"
                class="img-fluid border rounded" />
            </div>
            <div class="col-7">
              <div class="row border shdow">
                <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Nombre:</div>
                <div class="col-7 border-bottom">{{ product.product_name }}</div>
                <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Variedad:</div>
                <div class="col-7 border-bottom">{{ product.product_variety }}</div>
                <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Colores:</div>
                <div class="col-7 border-bottom">
                  <span v-for="color in product.product_colors" :key="color">
                    <small>{{ color }}</small><br />
                  </span>
                </div>
                <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Largo:</div>
                <div class="col-7 border-bottom">{{ product.length }} cm</div>
                <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Tallos:</div>
                <div class="col-7 border-bottom">{{ product.qty_stem_flower }}</div>
                <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Costo:</div>
                <div class="col-7 border-bottom">$ {{ product.stem_cost_price.toFixed(2) }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer bg-secondary bg-gradient p-1">

        </div>
      </div>
    </div>
  </div>
</template>