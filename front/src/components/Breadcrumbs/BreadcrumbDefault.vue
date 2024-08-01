<script setup lang="ts">
const props = defineProps(['pageTitle'])
</script>

<template>
  <div class="mb-3 flex flex-col justify-end  sm:flex-row sm:items-center sm:justify-between bg-slate-200">
    <nav>
      <ol class="flex items-center gap-2">
        <li>
          <router-link class="font-medium" to="/"> </router-link>
        </li>
        <li class="font-medium text-primary">{{ props.pageTitle }}</li>
      </ol>
    </nav>
  </div>
</template>
