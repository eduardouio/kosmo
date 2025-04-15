<scritp setup>
</script>
<template>
  <div class="autocomplete">
    <input type="text" v-model="searchTerm" @keydown="handleKeyDown" @focus="showSuggestions = true" @blur="showSuggestions = false" placeholder="Search for a customer..." />
    <ul v-if="showSuggestions && filteredCustomers.length > 0">
      <li v-for="(customer, index) in filteredCustomers" :key="customer.id" :class="{ 'highlighted': index === highlightIndex }" @click="selectCustomer(customer)">
        {{ customer.name }}
      </li>
    </ul>
  </div>
</template>