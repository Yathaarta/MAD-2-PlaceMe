<template>
  <form @submit.prevent="submitFlow" class="col-lg-5 align-self-center mb-lg-5 rounded-4 p-lg-5 bg-dark">
    <div class="mb-3">
      <label class="col-form-label text-white">Your Email:</label>
      <input v-model="form.email" type="email" class="form-control bg-darkgray" :disabled="step > 1" required>
    </div>

    <div v-if="step === 2 && requiresOtp" class="mb-3 animate-slide-down">
      <label class="col-form-label text-info">Enter OTP sent to email:</label>
      <input v-model="form.otp" type="text" class="form-control border-info bg-darkgray" required>
    </div>

    <div v-if="step >= 2" class="mb-3 animate-slide-down">
      <label class="col-form-label text-white">Enter New Password:</label>
      <div class="input-group">
        <input v-model="form.newPassword" :type="pwdType" class="form-control bg-darkgray" required/>
        <button class="btn btn-outline-secondary" type="button" @click="togglePwd">
          <i class="bi" :class="pwdIcon"></i>
        </button>
      </div>
    </div>

    <div class="mt-5 d-flex gap-3 justify-content-end align-items-center mb-lg-5">
      <button type="button" class="btn btn-sm btn-secondary" @click="resetFormOrGoBack">Back</button>

      <button v-if="step === 1" type="submit" class="btn btn-primary" :disabled="isLoading">
        {{ isLoading ? 'Checking...' : 'Verify Email' }}
      </button>
      <button v-else type="submit" class="btn btn-success" :disabled="isLoading">
        {{ isLoading ? 'Resetting...' : 'Reset Password' }}
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, reactive } from 'vue';
import axios from 'axios';
import { useToastNotifications } from '@/composables/useToastNotification';
import { usePasswordVisibility } from '@/composables/usePasswordVisibility';

const emit = defineEmits(['backToLogin']);
const { addToastNotifications } = useToastNotifications();
const { inputType: pwdType, iconClass: pwdIcon, toggleVisibility: togglePwd } = usePasswordVisibility();

const step = ref(1); // 1: Enter Email, 2: Enter OTP & New Password
const requiresOtp = ref(true);
const isLoading = ref(false);

const form = reactive({ email: '', otp: '', newPassword: '' });

const submitFlow = () => {
  if (step.value === 1) checkEmail();
  else handleReset();
};

const checkEmail = async () => {
  isLoading.value = true;
  try {
    const res = await axios.post('/api/reset-password/request', { email: form.email });
    requiresOtp.value = res.data.requires_otp;
    addToastNotifications(res.data.message, 'success');
    step.value = 2; // Move to next UI step
  } catch (error) {
    addToastNotifications(error.response?.data?.error || "Error checking email", "error");
  } finally {
    isLoading.value = false;
  }
};

const handleReset = async () => {
  if (form.newPassword.length < 6) {
      addToastNotifications("Password must be at least 6 characters.", "error");
      return;
  }

  isLoading.value = true;
  try {
    const res = await axios.post('/api/reset-password/confirm', {
      email: form.email,
      otp: form.otp,
      new_password: form.newPassword
    });
    addToastNotifications(res.data.message, 'success');
    emit('backToLogin'); // Send user back to login screen on success
  } catch (error) {
    addToastNotifications(error.response?.data?.error || "Reset failed", "error");
  } finally {
    isLoading.value = false;
  }
};

const resetFormOrGoBack = () => {
  if (step.value === 2) {
    step.value = 1; // Go back to email entry
    form.otp = '';
    form.newPassword = '';
  } else {
    emit('backToLogin');
  }
};
</script>

<style scoped>

</style>
