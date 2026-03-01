import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false);
  const userRole = ref(null); // student, company, or admin

  const login = (role) => {
    isAuthenticated.value = true;
    userRole.value = role;
    // Saving to localStorage so it survives page reloads
    localStorage.setItem('userRole', role);
  };

  const logout = () => {
    isAuthenticated.value = false;
    userRole.value = null;
    localStorage.removeItem('userRole');
  };

  // Auto-login on refresh if localStorage has data
  const initAuth = () => {
    const savedRole = localStorage.getItem('userRole');
    if (savedRole) {
      isAuthenticated.value = true;
      userRole.value = savedRole;
    }
  };

  return { isAuthenticated, userRole, login, logout, initAuth };
});
