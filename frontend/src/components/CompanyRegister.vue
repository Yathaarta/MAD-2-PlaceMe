<template>
  <div class="company-slide d-flex align-items-center justify-content-center w-100 py-5">
    <div class="container">
      <div class="row align-items-center">

        <!-- LEFT SIDE -->
        <div class="col-12 col-lg-6 pe-lg-5 mb-5 mb-lg-0">
          <h1 class="display-5 fw-bold text-lightblue mb-3">
            Hire Talent on <span class="text-light">Place</span><span class="text-lightgreen">Me</span>
          </h1>
          <p class="lead text-light mb-4">
            Simplify your campus recruitment. Access verified student profiles, automate shortlisting, and close positions faster.
          </p>

          <div class="d-flex gap-3 mt-4">
            <div class="p-3 bg-white rounded shadow-sm border border-light">
              <h4 class="fw-bold text-primary mb-0">500+</h4>
              <small class="text-muted">Verified Students</small>
            </div>
            <div class="p-3 bg-white rounded shadow-sm border border-light">
              <h4 class="fw-bold text-dark mb-0">Zero</h4>
              <small class="text-muted">Paperwork</small>
            </div>
          </div>
        </div>

        <!-- RIGHT SIDE -->
        <CompanyRegisterForm />

      </div>
    </div>
  </div>
</template>



<script setup>
import CompanyRegisterForm from '@/components/CompanyRegisterForm.vue';
</script>


<style scoped>

.company-slide {
  background: linear-gradient(135deg, #4c9472 0%, #306893 100%);
  min-height: 85vh;
}

</style>
