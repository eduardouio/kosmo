<script setup>
import { useBaseStore } from '@/stores/base';


const storeBase = useBaseStore();
storeBase.loadSupliers();
const supliers = storeBase.supliers;

</script>
<template>
    
</template>