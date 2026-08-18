<template>
  <nav class="navbar navbar-expand-lg navbar-placeme" data-bs-theme="dark">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">
        <img src="/src/assets/images/logo.svg" alt="PlaceMe" height="45" />
      </a>

      <button
        class="navbar-toggler"
        type="button"
        @click="toggleMenu"
        aria-controls="navbarSupportedContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse align-middle" id="navbarSupportedContent" ref="collapseRef">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0 d-none d-lg-block">
          <slot>
            <img src="/src/assets/images/text.svg" alt="" height="45" class="mt-2" />
          </slot>
        </ul>
        <form class="d-flex flex-column flex-lg-row gap-2 m-3 m-lg-0 " role="login" data-bs-theme="light">
          <slot>
            <RouterLink to="/login" class="btn btn-success text-white" type="button" @close-nav="handleDelayedNav">Login</RouterLink>
            <button class="btn btn-primary" type="button" @click="handleNavClick('student')">Register</button>
            <button class="btn btn-outline-light d-lg-none" type="button" @click="handleNavClick('company')">Register company<ChevronRight /></button>
          </slot>
        </form>
        <div>
          <LoginModal @close-nav="handleDelayedNav()" />
        </div>
        <h1 class="text-secondary fw-light mx-4 d-none d-lg-block">|</h1>
        <a class="animated-underline text-decoration-none d-none d-lg-block" aria-current="page" @click="uiStore.triggerRegisterAction('company')">
          Register company<ChevronRight />
        </a>
      </div>
    </div>
  </nav>
</template>


<!--############################################################################################################-->


<script setup>
import { ref, onMounted } from 'vue';
import { ChevronRight } from 'lucide-vue-next'
import { useUIStore } from '@/stores/uiStore';
import { Collapse } from 'bootstrap';
import LoginModal from '@/components/LoginModal.vue';
import { RouterLink } from 'vue-router';

const uiStore = useUIStore();

const collapseRef = ref(null);
let bsCollapse = null;

onMounted(() => {
  if (collapseRef.value) {
    bsCollapse = new Collapse(collapseRef.value, {
      toggle: false
    });
  }
});

const toggleMenu = () => {
  if (bsCollapse) {
    bsCollapse.toggle();   // Using Bootstrap's smooth sliding toggle
  }
};

const handleNavClick = (target) => {
  uiStore.triggerRegisterAction(target);

  // 2. Auto-close the mobile menu smoothly if it is open
  if (collapseRef.value && collapseRef.value.classList.contains('show')) {
    if (bsCollapse) {
      bsCollapse.hide();
    }
  }
};

const handleDelayedNav = () => {
  setTimeout(() => { handleNavClick('fake');}, 200);
}
</script>


<!-- ########################################################################################################## -->


<style scoped>
.animated-underline {
  position: relative;
  display: inline-block;
  color: rgb(224, 214, 214);
  font-weight: 400;
}

.animated-underline::after {
  content: '';
  position: absolute;
  width: 92%;
  height: 3px;
  bottom: -4px;
  left: 0;
  background-color: currentColor;
  transform: scaleX(0);
  transform-origin: bottom left;
  transition: transform 0.3s ease-out;
}

.animated-underline:hover {
  color: rgb(255, 251, 251);
  cursor: pointer;
}
.animated-underline:hover::after {
  transform: scaleX(1);
}


.navbar-placeme {
  background: linear-gradient(160deg, #171616 0%, #474444 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  padding-left: 10rem;
  padding-right: 10rem;
}

@media (max-width: 1320px) {
  .navbar-placeme {
    padding-left: 0;
    padding-right: 0;
  }
}

.navbar-placeme .navbar-brand,
.navbar-placeme .nav-link {
  color: #ffffff !important;
}
</style>
