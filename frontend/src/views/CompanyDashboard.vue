<template>
<NavbarStructure>
  <button class="btn btn-primary" type="button" @click="handleLogout()">Logout</button>
</NavbarStructure>
</template>

<script setup>
import NavbarStructure from '@/components/NavbarStructure.vue';
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
