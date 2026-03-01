<template>
  <form @submit.prevent="handleLogin" class="col-lg-5 align-self-center mb-lg-5 rounded-4 p-lg-5 bg-dark">
    <div class="mb-3">
      <label for="recipient-name" class="col-form-label">Email:</label>
      <input v-model="form.email" type="email" class="form-control bg-darkgray" id="email" required>
    </div>
    <div class="mb-3">
      <label for="message-text" class="col-form-label">Password:</label>
      <input v-model="form.password" type="password" class="form-control bg-darkgray" id="password" required/>

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

    authStore.login(res.data.role);

    // bootstrap modal backdrop remove from dom
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => backdrop.remove());

    // Restore body scrolling and remove Bootstrap's lock classes
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
    // ---------------------------------------------


    // Redirect based on role
    if (res.data.role === 'admin') router.push('/admin-dashboard');
    else if (res.data.role === 'company') router.push('/company-dashboard');
    else router.push('/student-dashboard');

  } catch (error) {
    const msg = error.response?.data?.error || "Login failed.";
    addToastNotifications(msg, "error");
  } finally {
    isLoading.value = false;
  }
};

</script>


<style scoped>

</style>
