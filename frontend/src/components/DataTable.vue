<template>
  <div class="card bg-white border-0 shadow-sm rounded-2 overflow-hidden">
    <div class="table-responsive">
      <table class="table table-hover align-middle mb-0">

        <!-- Standardized Header -->
        <thead class="table-light">
          <tr>
            <th v-for="(col, index) in headers" :key="index"
              class="py-3 px-5 text-uppercase small fw-bold"
              >
              {{ col }}
            </th>
          </tr>
        </thead>

        <!-- Parent injects rows here -->
        <tbody>
          <slot></slot>
        </tbody>

      </table>

      <!-- Slot for injecting empty state component -->
      <slot name="empty"></slot>

    </div>
  </div>
</template>

<script setup>
defineProps({
  // array of column names: ['Company', 'Job Role', 'Deadline', 'Status', 'Actions']
  headers: {
    type: Array,
    required: true
  }
});
</script>
