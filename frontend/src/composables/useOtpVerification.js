import { ref } from 'vue';
import axios from 'axios';
import { useToastNotifications } from '@/composables/useToastNotification';

export function useOtpVerification() {
  const { addToastNotifications } = useToastNotifications();

  const otpSent = ref(false);
  const showOtpField = ref(false);
  const isSendingOtp = ref(false);

  const isVerifying = ref(false);
  const isVerified = ref(false); // Tracks if they successfully verified
  const verifiedAt = ref(null);

  const requestOtp = async (email) => {
    if (!email) {
      addToastNotifications("Please enter an email first.", "error");
      return;
    }

    isSendingOtp.value = true;
    try {
      const response = await axios.post('/api/send-registration-otp', { email });
      addToastNotifications(response.data.message, "success");
      showOtpField.value = true;
      otpSent.value = true;
    } catch (error) {
      addToastNotifications(error.response?.data?.error || "Failed to send OTP", "error");
    } finally {
      isSendingOtp.value = false;
    }
  };

  const verifyOtp = async (email, otp) => {
    if (!otp) {
      addToastNotifications("Please enter the OTP.", "error");
      return;
    }

    isVerifying.value = true;
    try {
      const res = await axios.post('/api/verify-registration-otp', { email, otp });
      addToastNotifications(res.data.message, "success");

      // Update UI states on success
      isVerified.value = true;
      showOtpField.value = false; 
      verifiedAt.value = Date.now();
    } catch (error) {
      addToastNotifications(error.response?.data?.error || "Invalid OTP", "error");
    } finally {
      isVerifying.value = false;
    }
  };

  const resetOtpState = () => {
    otpSent.value = false;
    showOtpField.value = false;
    isSendingOtp.value = false;
    isVerifying.value = false;
    isVerified.value = false;
    verifiedAt.value = null;
  };

  return {
    otpSent, showOtpField, isSendingOtp, isVerifying, isVerified, verifiedAt, requestOtp, verifyOtp, resetOtpState
  };
}
