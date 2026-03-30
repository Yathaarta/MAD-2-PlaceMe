<template>
  <DashboardLayout :menuLinks="adminMenu">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in"><component :is="Component" /></transition>
    </router-view>
  </DashboardLayout>
</template>

<script setup>
import DashboardLayout from '@/components/DashboardLayout.vue';
const adminMenu = [
  { name: 'Dashboard', icon: 'bi bi-grid-1x2-fill', route: '/admin-dashboard' },
  { name: 'Companies', icon: 'bi bi-buildings-fill', route: '/admin-dashboard/companies' },
  { name: 'Students', icon: 'bi bi-mortarboard-fill', route: '/admin-dashboard/students' },
  { name: 'Placement Drives', icon: 'bi bi-briefcase-fill', route: '/admin-dashboard/drives' }
];
</script>
<style scoped>.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; } .fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(10px); }</style>
