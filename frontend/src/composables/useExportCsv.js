import { ref } from 'vue';
import axios from 'axios';
import { useToastNotifications } from '@/composables/useToastNotification';

export function useExportCsv(route) {
  const { addToastNotifications } = useToastNotifications();

  const isExporting = ref(false);


  const exportCSV = async () => {

    isExporting.value = true;
    try {
      const res = await axios.post(route);
      addToastNotifications(res.data.message || "Export started! You will be notified when the CSV is ready.", "success");
    } catch (err) {
      if (err.response?.status === 404) {
        addToastNotifications("CSV Export task is currently being configured by the server admins.", "info");
      } else {
          const backendMessage = err.response?.data?.error || "Failed to trigger export.";
          addToastNotifications(backendMessage, "error");
      }
    } finally {
      isExporting.value = false;
    }
  }

  return { isExporting, exportCSV };
}
