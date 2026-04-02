import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useToastNotifications } from '@/composables/useToastNotification';

export function useFetchData(url, customErrorMessage = "Failed to load data. Please try again.") {
  const { addToastNotifications } = useToastNotifications();

  const data = ref([]);
  const isLoading = ref(true);

  const fetchData = async () => {
    isLoading.value = true;
    try {
      const response = await axios.get(url);
      data.value = response.data;
    } catch (error) {
      console.error(`Error fetching from ${url}:`, error);
      addToastNotifications(error.response?.data?.error || customErrorMessage, "error");
    } finally {
      isLoading.value = false;
    }
  };

  onMounted(() => {
    fetchData();
  });

  return { data, isLoading, fetchData };
}
