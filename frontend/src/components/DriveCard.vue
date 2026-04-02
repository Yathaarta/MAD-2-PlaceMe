<template>
  <div class="card bg-white border-0 shadow-sm rounded-4 h-100 hover-card d-flex flex-column" :class="{'opacity-75': !isActive}">
    <div class="card-body p-4 d-flex flex-column flex-grow-1">

      <!-- Header -->
      <div class="d-flex justify-content-between align-items-start mb-3">
        <slot name="header-left"></slot>
        <slot name="header-right"></slot>
      </div>

      <slot name="title-section"></slot>

      <!-- Stats Box -->
      <div class="bg-light rounded-3 p-3 mb-4 flex-grow-1">
        <div class="d-flex justify-content-between mb-2">
          <span class="text-muted small fw-bold text-uppercase">Min CGPA</span>
          <span class="fw-bold text-dark">{{ minCgpa }}</span>
        </div>
        <div class="d-flex justify-content-between">
          <span class="text-muted small fw-bold text-uppercase">{{ statLabel }}</span>
          <span class="fw-bold" :class="statValueClass">{{ statValue }}</span>
        </div>
      </div>

      <!-- Footer -->
      <div class="mt-auto">
        <slot name="actions"></slot>
      </div>

    </div>
  </div>
</template>

<script setup>
defineProps({
  isActive: { type: Boolean, default: true },
  minCgpa: { type: [String, Number], default: 'No minimum' },
  statLabel: { type: String, required: true },
  statValue: { type: [String, Number], required: true },
  statValueClass: { type: String, default: 'text-primary' }
});
</script>

<style scoped>
.hover-card { transition: transform 0.2s ease, box-shadow 0.2s ease; }
.hover-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }
</style>
