<template>
  <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 gap-3">
    <h3 class="fw-bold text-dark mb-2 mb-md-0">{{ title }}</h3>

    <!-- Filters Container -->
    <div class="d-flex gap-2">
      <!-- Search Input -->
      <div v-if="showSearch" class="input-group shadow-sm rounded-pill overflow-hidden" style="max-width: 250px;">
        <span class="input-group-text bg-white border-0" style="margin-right: -0.7rem;"><i class="bi bi-search text-muted"></i></span>
        <input
          type="text"
          class="form-control border-0 bg-white shadow-none -2"
          :placeholder="searchPlaceholder"
          :value="searchQuery"
          @input="$emit('update:searchQuery', $event.target.value)"
        >
      </div>

      <!-- Dropdown Filter -->
      <select
        v-if="filterOptions.length > 0"
        class="form-select bg-white shadow-sm border-0 rounded-pill"
        style="max-width: 180px;"
        :value="filterValue"
        @change="$emit('update:filterValue', $event.target.value)"
      >
        <option v-for="opt in filterOptions" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>

      <!-- Optional slot -->
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },

  // Search Props
  showSearch: { type: Boolean, default: true },
  searchPlaceholder: { type: String, default: 'Search...' },
  searchQuery: { type: String, default: '' },

  // Filter Props
  filterOptions: {
    type: Array,
    default: () => []  // Array like { label: 'Approved', value: 'approved' }
  },
  filterValue: { type: String, default: 'all' }
});

defineEmits(['update:searchQuery', 'update:filterValue']);
</script>
