<template>
  <nav class="navbar navbar-dark bg-dark border-bottom shadow-sm px-3 fixed-top d-flex flex-nowrap align-items-center"
    style="height: 55px; z-index: 1050;">

    <button class="btn btn-dark d-md-none me-2 p-1" type="button" @click="$emit('toggle-mobile-sidebar')">
      <i class="bi bi-list fs-3"></i>
    </button>

    <router-link class="navbar-brand fw-bold d-flex align-items-center me-auto" to="/">
      <img src="/src/assets/images/logo.svg" alt="PlaceMe" height="30" class="me-2 d-none d-sm-block" />
      <span class="fs-4 d-sm-none">Place<span class="text-primary">Me</span></span>
    </router-link>

    <div class="d-flex align-items-center gap-3">
      <div class="text-light d-none d-sm-block">
        Welcome, <span class="text-lightgreen text-capitalize">{{ displayUserName }}</span>
      </div>

      <router-link v-if="authStore.userRole !== 'admin'" :to="`/${authStore.userRole}-dashboard/profile`"
        class="btn btn-outline-light rounded-circle d-flex align-items-center justify-content-center p-0 overflow-hidden"
        style="width: 35px; height: 35px; border: 2px solid #198754;" title="Profile">
        <img v-if="authStore.userUniquifier"
          :src="`https://api.dicebear.com/7.x/identicon/svg?seed=${authStore.userUniquifier}&backgroundColor=198754`"
          alt="Avatar" width="35" height="35" />
        <i v-else
          class="bi bi-person-fill fs-5 text-secondary bg-light w-100 h-100 d-flex align-items-center justify-content-center"></i>
      </router-link>

      <button class="btn btn-danger btn-sm rounded-pill px-3 d-flex align-items-center" @click="handleLogout">
        <i class="bi bi-box-arrow-right me-0 me-sm-2"></i>
        <span class="d-none d-sm-inline">Logout</span>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useToastNotifications } from '@/composables/useToastNotification';

defineEmits(['toggle-mobile-sidebar']);

const authStore = useAuthStore();
const router = useRouter();
const { addToastNotifications } = useToastNotifications();

const displayUserName = computed(() => {
  return authStore.userName || (authStore.userRole ? authStore.userRole.toUpperCase() : 'User');
});

const handleLogout = async () => {
  try {
     await axios.post('/api/logout');
  } catch (e) {
    console.log(e)
    addToastNotifications('Could not logout', 'error')
  }
  finally {
    authStore.logout();
    router.push('/');
    addToastNotifications('Logged out successfully', 'success');
  }
};
</script>
