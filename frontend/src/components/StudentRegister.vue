<template>
  <div class="student-slide d-flex align-items-center justify-content-center w-100 py-5">
    <div class="container">
      <div class="row align-items-center">

        <!-- LEFT SIDE: Info -->
        <div class="col-12 col-lg-6 pe-lg-5 mb-4 mb-lg-0">
          <h1 class="display-5 fw-bold text-lightgreen mb-3">
            Get Placed with <span class="text-light">Place</span><span class="text-lightblue">Me</span>
          </h1>
          <p class="lead text-light mb-4">
            Don't just graduate—launch your career. Build your profile, showcase your skills, and let top recruiters find you.
          </p>

          <ul class="list-unstyled text-light">
            <li class="mb-2 ms-2  d-flex align-items-center">
              <i class="bi bi-check-circle-fill text-info me-2"></i> Real-time Application Tracking
            </li>
            <li class="mb-2 ms-2  d-flex align-items-center">
              <i class="bi bi-check-circle-fill text-info me-2"></i> Exclusive Campus Drives
            </li>
            <li class="ms-2 d-flex align-items-center">
              <i class="bi bi-check-circle-fill text-info me-2"></i> Direct HR Communication
            </li>
          </ul>
        </div>

        <!-- RIGHT SIDE: Form -->
        <StudentRegisterForm />

      </div>
    </div>
  </div>
</template>


<script setup>

import StudentRegisterForm from '@/components/StudentRegisterForm.vue';
</script>


<style scoped>

.student-slide {
  background: linear-gradient(135deg, #306893 0%, #4c9472 100%);
  min-height: 85vh; 
}
</style>
