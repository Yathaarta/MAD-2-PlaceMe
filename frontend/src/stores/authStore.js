import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false);
  const userRole = ref(null);
  const userName = ref(null);
  const userUniquifier = ref(null);
  const isAuthReady = ref(false);

  const login = (role, name, uniquifier) => {
    isAuthenticated.value = true;
    userRole.value = role;
    userName.value = name;
    userUniquifier.value = uniquifier;
  };

  const logout = () => {
    isAuthenticated.value = false;
    userRole.value = null;
    userName.value = null;
    userUniquifier.value = null;
  };

  const checkAuth = async () => {
    try {
      const res = await axios.get('/api/auth/status');
      isAuthenticated.value = true;
      userRole.value = res.data.role;
      userName.value = res.data.name;
      userUniquifier.value = res.data.uniquifier;
    } catch (error) {
      isAuthenticated.value = false;
      userRole.value = null;
      userName.value = null;
      userUniquifier.value = null;
    } finally {
      isAuthReady.value = true;
    }
  };

  return { isAuthenticated, userRole, userName, userUniquifier, isAuthReady, login, logout, checkAuth };
});
