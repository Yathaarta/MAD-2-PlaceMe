<template>
  <div class="col-12 col-lg-6">
    <div class="card border-0 shadow-lg my-3 transition-all" :class="{ 'focus-pulse': isAnimating }"
      style="background: rgba(255,255,255,0.98); border-radius: 15px;" ref="formCardRef">
      <div class="card-body p-4 p-lg-5">
        <h3 class="fw-bold mb-4 text-center text-primary">Company Registration</h3>

        <form @submit.prevent="handleRegister">
          <fieldset :disabled="isProcessing">
             <!-- Name -->
            <div class="mb-3">
              <input v-model="form.companyName" type="text" class="form-control bg-light py-2"
                placeholder="Company Name" required>
            </div>
            <!-- Select Industry  -->
            <div class="mb-3">
              <select v-model="form.industry" class="form-select bg-light py-2" required>
                <option value="" disabled selected>Select Industry</option>
                <option v-for="ind in industries" :key="ind" :value="ind">{{ ind }}</option>
              </select>
            </div>
             <!-- Email input  -->
            <div class="mb-1 position-relative">
              <input v-model="form.hrEmail" type="email" class="form-control bg-light py-2"
                placeholder="University Email" :readonly="isVerified" required>
              <i v-if="isVerified"
                class="bi bi-check-circle-fill text-success position-absolute top-50 end-0 translate-middle-y me-3"></i>
            </div>

            <!-- Verify link  -->
            <div v-if="!isVerified" class="d-flex justify-content-end mb-3 gap-2 align-items-center">
              <a href="#" @click.prevent="requestOtp(form.hrEmail)"
                class="text-decoration-none small fw-bold text-primary" style="font-size: 12px;">
                <span v-if="isSendingOtp">Sending...</span>
                <span v-else>{{ otpSent ? 'Resend OTP?' : 'Verify with OTP?' }}</span>
              </a>
              <i class="bi bi-info-circle-fill text-warning" data-bs-toggle="tooltip"
                data-bs-delay='{"show":0, "hide":100}'
                title="You can register with non existant fake emails too 😒, But use real email if you want to be able to recieve pdf/xlsx reports or test OTP verification feature 😁"
                style="cursor: help;">
              </i>
            </div>
            <!-- hidden opt feild  -->
            <div v-if="showOtpField && !isVerified"
              class="mb-3 bg-light p-2 rounded border border-primary border-opacity-25 animate-slide-down">
              <div class="input-group input-group-sm">
                <input v-model="form.otp" type="text" class="form-control border-0 bg-white"
                  placeholder="Enter 6-digit Code">
                <button class="btn btn-primary" type="button" @click="verifyOtp(form.hrEmail, form.otp)"
                  :disabled="isVerifying">
                  {{ isVerifying ? 'Checking...' : 'Verify' }}
                </button>
              </div>
            </div>

            <!-- Password Row -->
            <div class="row g-2 mb-4">
              <div class="col-6 position-relative">
                <div class="input-group">
                  <input v-model="form.password" :type="pwdType" class="form-control bg-light py-2"
                    placeholder="Password" required>
                  <button class="btn btn-outline-gray bg-light " type="button" @click="togglePwd">
                    <i class="bi" :class="pwdIcon"></i>
                  </button>
                </div>
              </div>
              <div class="col-6">
                <input v-model="form.confirmPassword" type="password" class="form-control bg-light py-2"
                  :class="{ 'is-invalid': !passwordsMatch && form.confirmPassword }" placeholder="Confirm" required>
              </div>
            </div>

            <div class="d-grid">
              <button type="submit" class="btn btn-primary fw-bold shadow-sm py-2">
                Start Hiring
              </button>
            </div>
          </fieldset>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { useRegisterUI } from '@/composables/RegistrationUI';
import { useDataStore } from '@/stores/dataStore';
import { useToastNotifications } from '@/composables/useToastNotification';
import { useOtpVerification } from '@/composables/useOtpVerification';
import { usePasswordVisibility } from '@/composables/usePasswordVisibility';
import { useFormReset } from '@/composables/ResetForm';
import axios from 'axios';

const form = reactive({
  companyName: '',
  hrEmail: '',
  otp: '',
  industry: '',
  password: '',
  confirmPassword: ''
});

const { isProcessing, formCardRef, isAnimating, passwordsMatch, validPassword } = useRegisterUI('company', form);
const { industries } = useDataStore()
const { addToastNotifications } = useToastNotifications();
const { otpSent, showOtpField, isSendingOtp, isVerifying, isVerified, requestOtp, verifyOtp, verifiedAt, resetOtpState } = useOtpVerification();
const { inputType: pwdType, iconClass: pwdIcon, toggleVisibility: togglePwd } = usePasswordVisibility();
const { resetForm } = useFormReset();

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
    const response = await axios.post('/api/register/company', {
      company_name: form.companyName,
      hr_email: form.hrEmail,
      industry: form.industry,
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
      const msg = error.response?.data?.error || "Registration failed.";
      addToastNotifications(msg, "error");
    }
  }
  isProcessing.value = false
};
</script>



<style scoped>
/* Subtle focus inputs */
.form-control:focus, .form-select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 0.25rem rgba(59, 130, 246, 0.25);
}

/* The focus animatoin */
.focus-pulse {
  animation: pulseBlue 0.7s ease-in-out 0s 2;
  border: 2px solid #102fb9 !important;
}
@keyframes pulseBlue {
  0% { box-shadow: 0 0 0 0 rgba(16, 81, 185, 0.7); transform: scale(1); }
  50% { box-shadow: 0 0 0 20px rgba(16, 185, 129, 0); transform: scale(1.02); }
  100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); transform: scale(1); }
}
.transition-all {
  transition: all 0.3s ease;
}
</style>
