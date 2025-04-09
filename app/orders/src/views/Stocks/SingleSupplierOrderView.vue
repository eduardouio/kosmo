<script setup>
import SideBar from '@/components/Sotcks/SideBar.vue';
import SingleOrderSuplier from '@/components/Sotcks/SingleOrderSuplier.vue';
</script><IconPrinter size="20" stroke="1.5" />
<template>
     <div class="container-fluid">
    <div class="row pt-2">
      <div class="col-2">
        <SideBar />
      </div>
      <div class="col-10">
        <SingleOrderSuplier/>
      </div>
    </div>
  </div>
</template>