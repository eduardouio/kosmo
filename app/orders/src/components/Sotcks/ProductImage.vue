<script setup>
import { computed } from 'vue';
import { appConfig } from '@/AppConfig';
const props = defineProps(['product']);

let imgAlt = 'Imagen del producto';

const urlImage = computed(() => {
    if (props.product_image === null || props.product.product_image === '') {
        return appConfig.imgPlaceholder;
    }
    imgAlt = `${props.product.product_name} ${props.product.product_variety}`;
    return appConfig.apiBaseUrl + props.product.product_image;
});

</script>
<template>
    <img :src="urlImage" :alt="imgAlt" class="img-fluid border rounded" />
</template>