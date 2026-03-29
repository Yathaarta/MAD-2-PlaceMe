<template>
  <form @submit.prevent="handleLogin" class="col-lg-5 align-self-center mb-lg-5 rounded-4 p-lg-5 bg-dark">
    <div class="mb-3">
      <label class="col-form-label text-light">Email:</label>
      <input v-model="form.email" type="email" class="form-control bg-darkgray" required>
    </div>
    <div class="mb-3">
      <label class="col-form-label text-light">Password:</label>
      <input v-model="form.password" type="password" class="form-control bg-darkgray" required/>
    </div>
    <div class="mt-5 d-flex gap-3 justify-content-end align-items-center mb-lg-5">
      <button type="button" class="btn btn-sm btn-danger" @click="$emit('requestReset')">Forgot Password</button>
      <button type="submit" class="btn btn-success" :disabled="isLoading">{{ isLoading ? 'Logging in...' : 'Log in' }}</button>
    </div>
  </form>
</template>

<script setup>
import { ref, reactive } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useToastNotifications } from '@/composables/useToastNotification';
import { useAuthStore } from '@/stores/authStore';

defineEmits(['requestReset']);
const router = useRouter();
const { addToastNotifications } = useToastNotifications();
const authStore = useAuthStore();

const form = reactive({ email: '', password: '' });
const isLoading = ref(false);

const handleLogin = async () => {
  isLoading.value = true;
  try {
    const res = await axios.post('/api/login', form);
    addToastNotifications(res.data.message, 'success');

    authStore.login(res.data.role, res.data.name, res.data.uniquifier);

    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => backdrop.remove());
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';

    router.push(`/${res.data.role}-dashboard`);
  } catch (error) {
    addToastNotifications(error.response?.data?.error || "Login failed.", "error");
  } finally {
    isLoading.value = false;
  }
};
</script>
