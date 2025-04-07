<script setup>
import { useRoute } from 'vue-router';
const route = useRoute();
</script>

<template>
<h1>Hola Mundo {{ route.params.id }}</h1>
</template>