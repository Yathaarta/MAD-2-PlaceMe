import { ref, computed, watch, onMounted } from 'vue';
import { useUIStore } from '@/stores/uiStore';
import { Tooltip } from 'bootstrap';
import { useToastNotifications } from '@/composables/useToastNotification';

export function useRegisterUI(targetname, formState) {
  const uiStore = useUIStore();
  const { addToastNotifications } = useToastNotifications();
  const formCardRef = ref(null);
  const isAnimating = ref(false);
  const isProcessing = ref(false)

  const validPassword = () => {
      if (formState.password.length < 6) {
        addToastNotifications("Password must be at least 6 characters.", "error");
        return false;
      }

      if (formState.password !== formState.confirmPassword) {
        addToastNotifications("Passwords do not match!", "error");
        return false;
      }
    return true;
  }

  const passwordsMatch = computed(() => {
    return formState.password === formState.confirmPassword || formState.confirmPassword === '';
  });


  watch(() => uiStore.focusTarget, (newTarget) => {
    if (newTarget === targetname) {
      isAnimating.value = true;

      // Focus the first input
      if (formCardRef.value) {
        const firstInput = formCardRef.value.querySelector('input');
        if (firstInput) firstInput.focus();
      }

      setTimeout(() => isAnimating.value = false, 1500);
    }
  });

  onMounted(() => {
    const elements = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    elements.forEach(el => {
      new Tooltip(el, {
        delay: { show: 0, hide: 100 },
        trigger: 'hover'
      })
    })
  })

  return {
    isProcessing,
    formCardRef,
    isAnimating,
    passwordsMatch,
    validPassword
  };

}
