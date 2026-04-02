import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '@/views/LandingPage.vue'
import { useAuthStore } from '@/stores/authStore'
import NotFound from '@/views/NotFound.vue'

import StudentDashboard from '@/views/StudentDashboard.vue'
import CompanyDashboard from '@/views/CompanyDashboard.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'

import AdminHome from '@/views/admin/AdminHome.vue'
import AdminCompanies from '@/views/admin/AdminCompanies.vue'
import AdminStudents from '@/views/admin/AdminStudents.vue'
import AdminDrives from '@/views/admin/AdminDrives.vue'

// Company Views
import CompanyHome from '@/views/company/CompanyHome.vue'
import CompanyDrives from '@/views/company/CompanyDrives.vue'
import CompanyApplicants from '@/views/company/CompanyApplicants.vue'
import CompanyProfile from '@/views/company/CompanyProfile.vue'
import CompanyStats from '../views/company/CompanyStats.vue'


const router = createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', component: LandingPage },
      { path: '/login', component: LandingPage },
      { path: '/reset_password', component: LandingPage },

      // --- STUDENT ROUTES ---
      {
        path: '/student-dashboard',
        component: StudentDashboard,
        meta: { requiresAuth: true, role: 'student' },
      },
      // --- COMPANY ROUTES ---
      {
        path: '/company-dashboard',
        component: CompanyDashboard,
        meta: { requiresAuth: true, role: 'company' },
        children: [
          { path: '', name: 'CompanyHome', component: CompanyHome },
          { path: 'drives', name: 'CompanyDrives', component: CompanyDrives },
          { path: 'applicants', name: 'CompanyApplicants', component: CompanyApplicants },
          { path: 'profile', name: 'CompanyProfile', component: CompanyProfile },
          { path: 'stats', name: 'CompanyStats', component: CompanyStats}
        ]
      },
      // --- ADMIN ROUTES ---
      {
        path: '/admin-dashboard',
        component: AdminDashboard,
        meta: { requiresAuth: true, role: 'admin' },
        children: [
          { path: '', name: 'AdminHome', component: AdminHome },
          { path: 'companies', name: 'AdminCompanies', component: AdminCompanies },
          { path: 'students', name: 'AdminStudents', component: AdminStudents },
          { path: 'drives', name: 'AdminDrives', component: AdminDrives }
        ]
      },

      { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound }
    ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  if (!authStore.isAuthReady) await authStore.checkAuth();

  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) return next('/');
    if (to.meta.role && to.meta.role !== authStore.userRole) return next(`/${authStore.userRole}-dashboard`);
  }

  if ((to.path === '/' || to.path === '/login' || to.path === '/reset_password') && authStore.isAuthenticated) {
     return next(`/${authStore.userRole}-dashboard`);
  }

  next();
});

export default router
