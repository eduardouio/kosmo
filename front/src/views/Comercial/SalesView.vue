<script setup lang="ts">
import { ref } from 'vue'
import BreadcrumbDefault from '@/components/Breadcrumbs/BreadcrumbDefault.vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import InvoiceHeader from '@/components/Invoices/InvoiceHeader.vue'

const pageTitle = ref('New Invoice')

</script>
<template>
    <DefaultLayout>
        <BreadcrumbDefault  :pageTitle="pageTitle"/>
        <InvoiceHeader />
    </DefaultLayout>
</template>