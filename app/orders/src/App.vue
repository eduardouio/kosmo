<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { appConfig } from "@/AppConfig.js"
import SideBar from './components/SideBar.vue';
</script>

<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-2 bg-light p-1 m-1 bg-opacity-50">
        <SideBar />
      </div>
      <div class="col bg-light border p-1 m-1 rounded-1 shadow bg-opacity-50 content">
        <div class="container-fluid">
          <RouterView />
        </div>
      </div>
    </div>
</div>
</template>
<style scoped>
  .content {
    min-height:50vh;
  }
</style>