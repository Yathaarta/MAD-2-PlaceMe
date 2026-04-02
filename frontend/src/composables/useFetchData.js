import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useToastNotifications } from '@/composables/useToastNotification';

export function useFetchData(url, customErrorMessage = "Failed to load data. Please try again.", isnull=false) {
  const { addToastNotifications } = useToastNotifications();

  const data = ref(isnull ? null : []);
  const isLoading = ref(true);

  const fetchData = async () => {
    isLoading.value = true;
    try {
      const response = await axios.get(url);
      data.value = response.data;
    } catch (error) {
      console.error(error.response?.data?.error, error.response?.data?.status);
      addToastNotifications(customErrorMessage, "error");
    } finally {
      isLoading.value = false;
    }
  };

  onMounted(() => {
    fetchData();
  });

  return { data, isLoading, fetchData };
}
