<template>
  <div class="container mt-5 text-center">
    <h1 class="text-danger">Admin Control Panel</h1>
    <p>Welcome, Superuser. You have full system access.</p>

    <button class="btn btn-outline-danger mt-4" @click="handleLogout">
      Logout
    </button>
  </div>
</template>

<script setup>
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';
import { useRouter } from 'vue-router';
import { useToastNotifications } from '@/composables/useToastNotification';

const authStore = useAuthStore();
const router = useRouter();
const { addToastNotifications } = useToastNotifications();


const handleLogout = async () => {
  try {
    await axios.post('/api/logout');
  } catch (error) {
    console.warn("Logout error:", error);
  } finally {
    authStore.logout();
    router.push('/');
    addToastNotifications('Logged out', 'success');
  }
};
</script>
