<template>
  <DashboardLayout :menuLinks="studentMenu">
    <!-- Nested views (Home, Drives, Apps, Stats, Profile) inject here -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </DashboardLayout>
</template>

<script setup>
import DashboardLayout from '@/components/DashboardLayout.vue';

const studentMenu = [
  { name: 'Home', icon: 'bi bi-house-door-fill', route: '/student-dashboard' },
  { name: 'Drives', icon: 'bi bi-briefcase-fill', route: '/student-dashboard/drives' },
  { name: 'Applications', icon: 'bi bi-file-earmark-text-fill', route: '/student-dashboard/applications' },
  { name: 'Stats', icon: 'bi bi-bar-chart-line-fill', route: '/student-dashboard/stats' },
  { name: 'Profile', icon: 'bi bi-person-lines-fill', route: '/student-dashboard/profile' }
];
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
