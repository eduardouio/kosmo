<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  props: {
    label: String,
    type: String,
    placeholder: String,
    customClasses: String,
    classInput: String,
    required: {
      type: Boolean,
      default: false
    }
  }
})
</script>

<template>
  <div :class="customClasses">
    <label>
      {{ label }}
      <span v-if="required" class="text-meta-1">*</span>
    </label>
    <input
      :type="type"
      :placeholder="placeholder"
      :class="classInput" 
      class="input input-bordered"
    />
  </div>
</template>
