<template>
  <Teleport to="body">
    <div class="toast-container position-fixed bottom-0 end-0 p-3 fw-semibold" style="z-index: 9999;">
      <TransitionGroup tag="div" name="toast" class="toast-container">
      <div
        v-for="notification in notifications" :key="notification.id"
        class="toast show align-items-center border-2 mb-2 bg-dark"
        :class="notification.type === 'error' ? 'text-lightred border-lightred' : 'text-lightgreen border-lightgreen'"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
        animation="true"
      >
        <div class="d-flex gap-4">
          <div class="toast-body d-flex align-items-center gap-2">
            <i :class="notification.type === 'error' ? 'bi bi-exclamation-triangle-fill' : 'bi bi-check-circle-fill'" class="me-2"></i>
            <div>{{ notification.message }}</div>
          </div>
          <button
            type="button"
            class="btn-close btn-close-white me-2 m-auto"
            @click="removeToastNotification(notification.id)"
            aria-label="Close"
          ></button>
        </div>
      </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>


<!--############################################################################################################-->


<script setup>
import { useToastNotifications } from '@/composables/useToastNotification';
const {notifications, removeToastNotification} = useToastNotifications();

</script>


<!--############################################################################################################-->


<style scoped>
.toast-container {
  position: fixed;
  bottom: 2vh;
  right: 1vw;
  display: flex;
  flex-direction: column;
  gap: 5px;
  z-index: 9999;
}

.toast-enter-active {
  animation: slide-in 0.4s ease-out;
}


.toast-leave-active {
  animation: slide-out 0.3s ease-in forwards;
  overflow: hidden;
}

@keyframes slide-in {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@keyframes slide-out {
  0% {
    opacity: 1;
    max-height: 100px;
    margin-bottom: 10px;
    transform: translateX(0);
  }
  50% {
    opacity: 0;
    transform: translateX(20px);
  }
  100% {
    opacity: 0;
    max-height: 0;
    margin-bottom: 0;
    padding-top: 0;
    padding-bottom: 0;
  }
}
</style>
