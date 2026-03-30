<template>
  <DashboardLayout :menuLinks="companyMenu">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in"><component :is="Component" /></transition>
    </router-view>
  </DashboardLayout>
</template>

<script setup>
import DashboardLayout from '@/components/DashboardLayout.vue';
const companyMenu = [
  { name: 'Dashboard', icon: 'bi bi-grid-1x2-fill', route: '/company-dashboard' },
  { name: 'Manage Drives', icon: 'bi bi-briefcase-fill', route: '/company-dashboard/drives' },
  { name: 'Applicants', icon: 'bi bi-people-fill', route: '/company-dashboard/applicants' },
  { name: 'Company Profile', icon: 'bi bi-building', route: '/company-dashboard/profile' },
  { name: 'Stats', icon: 'bi bi-bar-chart-line-fill', route: '/company-dashboard/stats' }
];
</script>
<style scoped>.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; } .fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(10px); }</style>
