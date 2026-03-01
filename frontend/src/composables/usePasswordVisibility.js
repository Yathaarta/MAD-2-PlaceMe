import { ref, computed } from 'vue';

export function usePasswordVisibility() {
  const inputType = ref('password');

  const toggleVisibility = () => {
    inputType.value = inputType.value === 'password' ? 'text' : 'password';
  };

  const iconClass = computed(() => {
    return inputType.value === 'password' ? 'bi-eye-slash' : 'bi-eye';
  });

  return {
    inputType,
    iconClass,
    toggleVisibility
  };
}
