<template>
  <div class="modal fade" ref="modalRef" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-fullscreen">
      <div class="modal-content">
        <div class="modal-header" style="background: linear-gradient(135deg, #4d84ae 0%, #388863 100%);">
          <h1 class="modal-title fs-4 text-white">
             {{ isResetMode ? 'Reset Password' : 'User Login' }}
          </h1>
          <button type="button" class="btn-close" aria-label="Close" @click="closeModal(); $emit('close-nav')"></button>
        </div>

        <div class="modal-body d-lg-flex justify-content-center">
          <Transition :name="transitionName" mode="out-in">
            <component
                :is="activeComponent"
                @request-reset="switchToReset"
                @back-to-login="switchToLogin"
             />
          </Transition>
        </div>
        <div class="modal-footer"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Modal } from 'bootstrap';
import LoginForm from '@/components/LoginForm.vue';
import ResetPassFrom from '@/components/ResetPassFrom.vue';

const route = useRoute();
const router = useRouter();

// --- DOM & Bootstrap Refs ---
const modalRef = ref(null);
let bsModal = null;

const transitionName = ref('slide-next');

const isResetMode = computed(() => route.path === '/reset_password');

// Computed Component
const activeComponent = computed(() => {
  return isResetMode.value ? ResetPassFrom : LoginForm;
});

// --- Actions ---

// Instead of changing state directly, we change the Route.
const switchToReset = () => {
  transitionName.value = 'slide-next';
  router.push('/reset_password');
};

const switchToLogin = () => {
  transitionName.value = 'slide-back';
  router.push('/login');
};

const closeModal = () => {
  router.push('/');
};

// --- Lifecycle & Watchers ---
onMounted(() => {
  if (modalRef.value) {
    // Initialize Bootstrap Modal
    bsModal = new Modal(modalRef.value);

    // Listen for native Bootstrap close events (e.g. hitting ESC)
    modalRef.value.addEventListener('hide.bs.modal', () => {
      if (route.path === '/login' || route.path === '/reset_password') {
        router.push('/');
      }
    });

    // Initial check (in case user refreshes page on /login)
    handleRouteCheck(route.path);
  }
});

onUnmounted(() => {
  // Cleanup listener
  if (modalRef.value) {
    modalRef.value.removeEventListener('hide.bs.modal', closeModal);
  }
});


watch(
  () => route.path,
  (newPath) => {
    handleRouteCheck(newPath);
  }
);

function handleRouteCheck(path) {
  if (!bsModal) return;

  if (path === '/login' || path === '/reset_password') {
    bsModal.show();
  } else {
    bsModal.hide();
  }
}

defineEmits(['close-nav'])
</script>

<style scoped>
@media (min-width: 992px) {
  form {
    border: 0.5px solid gainsboro
  }
  .modal-content {
    background-color: rgb(29, 29, 29);
  }
}

/* Transitions */
.slide-next-enter-active, .slide-next-leave-active,
.slide-back-enter-active, .slide-back-leave-active {
  transition: all 0.4s ease;
}

.slide-next-enter-from { opacity: 0; transform: translateX(50px); }
.slide-next-leave-to { opacity: 0; transform: translateX(-50px); }

.slide-back-enter-from { opacity: 0; transform: translateX(-50px); }
.slide-back-leave-to { opacity: 0; transform: translateX(50px); }
</style>
