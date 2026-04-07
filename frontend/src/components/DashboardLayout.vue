<template>
  <div class="dashboard-theme min-vh-100 position-relative">

    <DashNavbarStructure @toggle-mobile-sidebar="isMobileOpen = !isMobileOpen" />

    <aside
      class="custom-sidebar bg-dark shadow-lg d-flex flex-column"
      :class="{ 'expanded': isHovered, 'mobile-open': isMobileOpen }"
      @mouseenter="isHovered = true"
      @mouseleave="isHovered = false"
    >
      <div class="nav flex-column py-2 w-100 flex-grow-1" style="margin-top: 55px;">
        <router-link
          v-for="link in menuLinks"
          :key="link.name"
          :to="link.route"
          class="nav-link text-white sidebar-link d-flex align-items-center px-3 py-3"
          exact-active-class="active-link"
          @click="isMobileOpen = false"
        >
          <div class="icon-wrapper text-center">
            <i :class="link.icon + ' fs-5'"></i>
          </div>
          <span class="sidebar-text ms-3 fw-semibold">{{ link.name }}</span>
        </router-link>
      </div>
    </aside>

    <div v-if="isMobileOpen" class="mobile-overlay d-md-none" @click="isMobileOpen = false"></div>

    <main class="main-content flex-grow-1 p-3 p-md-4 pb-5 pt-5 mt-4 mt-lg-5 mt-md-5" @click="isMobileOpen = false">
      <slot></slot>
    </main>

  </div>
</template>

<script setup>
import { ref } from 'vue';
import DashNavbarStructure from '@/components/DashNavbarStructure.vue';

defineProps({
  menuLinks: {
    type: Array,
    required: true
  }
});

const isHovered = ref(false);
const isMobileOpen = ref(false);
</script>

<style scoped>
.dashboard-theme {
  background: linear-gradient(135deg, rgb(227, 242, 253) 0%, #c8e6c9 100%);
  overflow-x: hidden;
}

.custom-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 70px;
  z-index: 1040;
  transition: width 0.3s ease, transform 0.3s ease;
  overflow-x: hidden;
  white-space: nowrap;
}

.custom-sidebar.expanded { width: 250px; }
.icon-wrapper { min-width: 30px; }
.sidebar-text { opacity: 0; transition: opacity 0.2s ease; }
.custom-sidebar.expanded .sidebar-text { opacity: 1; transition-delay: 0.1s; }

.sidebar-link { transition: all 0.2s ease; border-left: 4px solid transparent; }
.sidebar-link:hover, .active-link {
  background-color: rgba(255, 255, 255, 0.1);
  color: #a5d6a7 !important;
  border-left: 4px solid #a5d6a7;
}

.main-content {
  margin-left: 70px;
  transition: margin-left 0.3s ease;
  min-height: 100vh;
}

@media (max-width: 768px) {
  .custom-sidebar { transform: translateX(-100%); width: 250px; }
  .custom-sidebar .sidebar-text { opacity: 1; }
  .custom-sidebar.mobile-open { transform: translateX(0); }
  .main-content { margin-left: 0; }
  .mobile-overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1030; backdrop-filter: blur(2px);
  }
}
</style>
