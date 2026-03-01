import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useUIStore = defineStore('ui', () => {
  const activeSlideIndex = ref(0);

  const focusTarget = ref(null);

  function triggerRegisterAction(target) {

    if (target === 'student') {
      activeSlideIndex.value = 0;
    } else if (target === 'company') {
      activeSlideIndex.value = 1;
    }

    focusTarget.value = target;

    setTimeout(() => {
      focusTarget.value = null;
    }, 1500);
  }

  return { activeSlideIndex, focusTarget, triggerRegisterAction };
});
