<template>
  <div class="modal fade" :id="modalId" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered" :class="size">
      <div class="modal-content border-0 shadow-lg rounded-4" v-if="selectedObject">

        <!-- Standardized Header -->
        <div class="modal-header border-0 py-3 rounded-top-4" :class="headerClass">
          <h5 class="modal-title fw-bold">
            <i v-if="icon" :class="['bi', icon, 'me-2']"></i> {{ title }}
          </h5>
          <button type="button" class="btn-close" :class="{'btn-close-white': isHeaderDark}" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <!-- Slot for main content -->
        <div class="modal-body p-3 p-md-4">
          <slot></slot>
        </div>

        <!-- Footer Actions - for close or other action buttons -->
        <div class="modal-footer border-0 p-4 rounded-bottom-4" v-if="$slots.footer">
          <slot name="footer"></slot>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  modalId: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: '' // can pass 'modal-lg' or 'modal-xl'
  },
  selectedObject: {
    type: Object,
    default: null
  },
  headerClass: {
    type: String,
    default: 'bg-primary text-white'
  }
});

const isHeaderDark = computed(() => {
  return props.headerClass.includes('text-white') || props.headerClass.includes('bg-dark');
});
</script>
