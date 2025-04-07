<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { appConfig } from "@/AppConfig.js"
</script>

<template>
  <RouterView />
</template>
<style scoped>
  .content {
    min-height:50vh;
  }
</style>