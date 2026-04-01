import { ref } from 'vue';
import axios from 'axios';

export function useAdminDashboard() {
  const dashboardData = ref(null);
  const isLoading = ref(true);

  const fetchDashboardData = async () => {
    isLoading.value = true;
    try {
      const response = await axios.get('/api/admin/dashboard');
      dashboardData.value = response.data;
    } catch (error) { console.error("Failed to fetch dashboard data", error); }
    finally { isLoading.value = false; }
  };

  return { dashboardData, isLoading, fetchDashboardData };
}
