<script setup lang="ts">
import BreadcrumbDefault from '@/components/Breadcrumbs/BreadcrumbDefault.vue'
import ChartOne from '@/components/Charts/ChartOne.vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

import { ref } from 'vue'

const pageTitle = ref('Basic Chart')
</script>

<template>
  <DefaultLayout>
    <!-- Breadcrumb Start -->
    <BreadcrumbDefault :pageTitle="pageTitle" />
    <!-- Breadcrumb End -->

    <div class="grid grid-cols-12 gap-4 md:gap-6 2xl:gap-7.5">
      <!-- ====== Chart One Start -->
      <ChartOne />
      <!-- ====== Chart One End -->

    </div>
  </DefaultLayout>
</template>
