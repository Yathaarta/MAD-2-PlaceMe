<template>
    <div class="col-12 col-lg-6">
      <div class="card border-0 shadow-lg my-3 transition-all" :class="{ 'focus-pulse': isAnimating }" style="background: rgba(255,255,255,0.98); border-radius: 15px;" ref="formCardRef">
        <div class="card-body p-4 p-lg-5">
          <h3 class="fw-bold mb-4 text-center text-success">Student Registration</h3>

          <form @submit.prevent="handleRegister" >
              <fieldset :disabled="isProcessing">
            <!-- Name -->
            <div class="mb-3">
              <input v-model="form.fullName" type="text" class="form-control bg-light py-2" placeholder="Full Name" required>
            </div>
            <!-- Email input  -->
            <div class="mb-1 position-relative">
              <input
                v-model="form.email"
                type="email"
                class="form-control bg-light py-2"
                placeholder="University Email"
                :readonly="isVerified"
                required
              >
              <i v-if="isVerified" class="bi bi-check-circle-fill text-success position-absolute top-50 end-0 translate-middle-y me-3"></i>
            </div>
            <!-- Verify link  -->
            <div v-if="!isVerified" class="d-flex justify-content-end mb-3 gap-2 align-items-center">
              <a href="#" @click.prevent="requestOtp(form.email)" class="text-decoration-none small fw-bold text-success" style="font-size: 12px;">
                <span v-if="isSendingOtp">Sending...</span>
                <span v-else>{{ otpSent ? 'Resend OTP?' : 'Verify with OTP?' }}</span>
              </a>
              <i class="bi bi-info-circle-fill text-warning"
                data-bs-toggle="tooltip"
                data-bs-delay='{"show":0, "hide":100}'
                title="You can register with non existant fake emails too 😒, But use real email if you want to be able to recieve pdf/xlsx reports or test OTP verification feature 😁"
                style="cursor: help;">
              </i>
            </div>
            <!-- hidden otp feild -->
            <div v-if="showOtpField && !isVerified" class="mb-3 bg-light p-2 rounded border border-success border-opacity-25 animate-slide-down">
              <div class="input-group input-group-sm">
                <input v-model="form.otp" type="text" class="form-control border-0 bg-white" placeholder="Enter 6-digit Code">
                <button class="btn btn-success" type="button" @click="verifyOtp(form.email, form.otp)" :disabled="isVerifying">
                  {{ isVerifying ? 'Checking...' : 'Verify' }}
                </button>
              </div>
            </div>
            <!-- Education -->
                <div class="row g-2 mb-3">
                  <div class="col-6">
                    <select v-model="form.degree" class="form-select bg-light py-2" required>
                      <option value="" disabled selected>Degree</option>
                      <option v-for="deg in degreeOptions" :key="deg.id" :value="deg.id">
                        {{ deg.name }}
                      </option>
                    </select>
                  </div>
                  <div class="col-6">
                    <select
                      v-model="form.stream"
                      class="form-select bg-light py-2"
                      required
                      :disabled="!form.degree || isStreamsLoading"
                    >
                      <option value="" disabled selected>
                        {{ isStreamsLoading ? 'Loading...' : 'Stream' }}
                      </option>
                      <option v-for="st in streamOptions" :key="st.id" :value="st.id">
                        {{ st.name }}
                      </option>
                    </select>
                  </div>
                </div>
            <!-- Password Row -->
            <div class="row g-2 mb-4">
              <div class="col-6 position-relative">
                <div class="input-group">
                  <input v-model="form.password" :type="pwdType" class="form-control bg-light py-2" placeholder="Password" required>
                  <button class="btn btn-outline-gray bg-light " type="button" @click="togglePwd">
                    <i class="bi" :class="pwdIcon"></i>
                  </button>
                </div>
              </div>
              <div class="col-6">
                <input
                  v-model="form.confirmPassword"
                  type="password"
                  class="form-control bg-light py-2"
                  :class="{'is-invalid': !passwordsMatch && form.confirmPassword}"
                  placeholder="Confirm"
                  required
                >
              </div>
            </div>

            <div class="d-grid">
              <button type="submit" class="btn btn-success fw-bold shadow-sm py-2">
                Create Account
              </button>
            </div>
            </fieldset>
          </form>
        </div>
      </div>
    </div>
</template>



<script setup>
import { reactive, onMounted, watch, ref } from 'vue';
import { useRegisterUI } from '@/composables/RegistrationUI';
import { useToastNotifications } from '@/composables/useToastNotification';
import { useOtpVerification } from '@/composables/useOtpVerification';
import { usePasswordVisibility } from '@/composables/usePasswordVisibility';
import { useFormReset } from '@/composables/ResetForm';

import axios from 'axios';

const form = reactive({
  fullName: '',
  email: '',
  otp: '',
  degree: '',
  stream: '',
  password: '',
  confirmPassword: ''
});

const { isProcessing, formCardRef, isAnimating, passwordsMatch, validPassword } = useRegisterUI('student', form);
const {addToastNotifications } = useToastNotifications()
const {otpSent, showOtpField, isSendingOtp, isVerifying, isVerified, requestOtp, verifyOtp, verifiedAt, resetOtpState} = useOtpVerification();
const { inputType: pwdType, iconClass: pwdIcon, toggleVisibility: togglePwd } = usePasswordVisibility();
const { resetForm } = useFormReset();

const degreeOptions = ref([]);
const streamOptions = ref([]);
const isStreamsLoading = ref(false);


onMounted(async () => {
  try {
    const res = await axios.get('/api/degrees');
    degreeOptions.value = res.data;
  } catch (e) {
    console.error("Failed to load degrees", e);
    addToastNotifications("Failed to load degrees", "error")
  }
});

watch(() => form.degree, async (newDegreeId) => {
  form.stream = '';
  streamOptions.value = [];

  if (newDegreeId) {
    isStreamsLoading.value = true;
    try {
      const res = await axios.get(`/api/streams/${newDegreeId}`);
      streamOptions.value = res.data;
    } catch (error) {
      console.error("Failed to load streams", error);
      addToastNotifications("Failed to load streams", "error")
    } finally {
      isStreamsLoading.value = false;
    }
  }
});


const handleRegister = async () => {

  if (!validPassword()) return;

  if (isVerified.value && verifiedAt.value) {
    const timeElapsed = Date.now() - verifiedAt.value;
    const tenMinutes = 10 * 60 * 1000; // 10 minutes

    if (timeElapsed > tenMinutes) {
      addToastNotifications("Form expired. Please fill again.", "error");
      resetForm(form, resetOtpState);
      return
    }
  }

  try {
    isProcessing.value = true;
    const response = await axios.post('/api/register/student', {
      full_name: form.fullName,
      email: form.email,
      degree: form.degree,
      stream: form.stream,
      password: form.password,
      is_verified_flow: isVerified.value
    });

    if (response.status === 201) {
      await new Promise(resolve => setTimeout(resolve, 1500));

      addToastNotifications(response.data.message, "success");

      resetForm(form, resetOtpState);
    }
  } catch (error) {
    console.error("Registration Error:", error);

    // Marshmallow Validation Errors - showing only first error
    if (error.response?.data?.errors) {
      const errors = error.response.data.errors;
      const firstField = Object.keys(errors)[0];
      const firstMessage = errors[firstField][0];
      addToastNotifications(firstMessage, "error");
    } else {
      // Generic Errors (e.g. "Email already exists" or 500 Server Error)
      const msg = error.response?.data?.error || "Registration failed. Please try again.";
      addToastNotifications(msg, "error");
    }
  }
  isProcessing.value = false
};

</script>






<style scoped>
/* Subtle focus inputs */
.form-control:focus, .form-select:focus {
  border-color: #10b981;
  box-shadow: 0 0 0 0.25rem rgba(16, 185, 129, 0.25);
}

/* The focus animatoin */
.focus-pulse {
  animation: pulseGreen 0.7s ease-in-out 0s 2;
  border: 2px solid #096244 !important;
}
@keyframes pulseGreen {
  0% { box-shadow: 0 0 0 0 rgba(10, 138, 96, 0.7); transform: scale(1); }
  50% { box-shadow: 0 0 0 20px rgba(52, 57, 55, 0.816); transform: scale(1.02); }
  100% { box-shadow: 0 0 0 0 rgba(28, 30, 29, 0.738); transform: scale(1); }
}
.transition-all {
  transition: all 0.3s ease;
}
</style>
