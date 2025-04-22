<script setup>
const props = defineProps({
    show: {
        type: Boolean,
        default: true,
        required: false
    }
})
</script>
<template>
    <div v-if="show" class="d-flex flex-column justify-content-center align-items-center pt-5">
        <div class="spinner-border text-primary p-5 m-5" role="status">
        </div>
        <span class="text-primary fs-5 blink">
            Cargando...
        </span>
    </div>
</template>