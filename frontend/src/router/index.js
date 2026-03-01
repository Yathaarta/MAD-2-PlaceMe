import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '@/views/LandingPage.vue'
import StudentDashboard from '@/views/StudentDashboard.vue'
import CompanyDashboard from '@/views/CompanyDashboard.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'
import NotFound from '@/views/NotFound.vue'

import { useAuthStore } from '@/stores/authStore'


const router = createRouter({
    history: createWebHistory(),
    routes: [
{ path: '/', component: LandingPage },
      { path: '/login', component: LandingPage },
      { path: '/reset_password', component: LandingPage },

      // --- PROTECTED ROUTES ---
      {
        path: '/student-dashboard',
        component: StudentDashboard,
        meta: { requiresAuth: true, role: 'student' } // Only students
      },
      {
        path: '/company-dashboard',
        component: CompanyDashboard,
        meta: { requiresAuth: true, role: 'company' } // Only companies
      },
      {
        path: '/admin-dashboard',
        component: AdminDashboard, // Admin Route
        meta: { requiresAuth: true, role: 'admin' }
      },
      {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: NotFound
      }
    ]
})

// --- THE NAVIGATION GUARD ---
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (!authStore.isAuthenticated && localStorage.getItem('userRole')) {
    authStore.initAuth();
  }

  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      return next('/');
    }

    if (to.meta.role && to.meta.role !== authStore.userRole) {
      return next(`/${authStore.userRole}-dashboard`);
    }
  }

  if (to.path === '/' && authStore.isAuthenticated) {
     return next(`/${authStore.userRole}-dashboard`);
  }

  next();
});
export default router
