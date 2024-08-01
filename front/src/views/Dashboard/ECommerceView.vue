<script setup lang="ts">
import DataStatsOne from '@/components/DataStats/DataStatsOne.vue'
import ChartOne from '@/components/Charts/ChartOne.vue'
import TableThree from '@/components/Tables/TableThree.vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
</script>

<template>
  <DefaultLayout>
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-6 xl:grid-cols-4 2xl:gap-7.5">
      <DataStatsOne />
    </div>

    <div class="mt-4 grid grid-cols-12 gap-4 md:mt-6 md:gap-6 2xl:mt-7.5 2xl:gap-7.5">
      <!-- ====== Table One Start -->
      <div class="col-span-12">
        <TableThree  />
      </div>
      <!-- ====== Table One End -->
      <!-- ====== Chart One Start -->
      <ChartOne />
      <!-- ====== Chart One End -->
    </div>
  </DefaultLayout>
</template>
