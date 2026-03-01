import { ref } from "vue";

const notifications = ref([])

const addToastNotifications = (message, type = 'success') => {
    const id = Date.now();
    notifications.value.push({
        id,
        message,
        type // 'success' or 'error'
    });

    setTimeout(() => removeToastNotification(id), 5000)
}

const removeToastNotification = (id) => {
    notifications.value = notifications.value.filter((n) => n.id != id)
}

export function useToastNotifications() {
    return {notifications, addToastNotifications, removeToastNotification}
}
