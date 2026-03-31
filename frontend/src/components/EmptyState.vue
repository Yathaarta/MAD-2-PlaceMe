<template>
  <div class="text-center py-5">
    <i :class="['bi', icon, 'fs-1 text-muted mb-3 d-block']"></i>
    <h5 class="text-muted fw-bold">{{ title }}</h5>
    <p v-if="message" class="text-muted small">{{ message }}</p>

    <!-- Optional slot -->
    <slot></slot>
  </div>
</template>

<script setup>
defineProps({
  icon: {
    type: String,
    default: 'bi-inbox'
  },
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    default: ''
  }
});
</script>
