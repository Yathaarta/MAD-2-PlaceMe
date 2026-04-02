<template>
  <div class="row justify-content-center pb-5">
    <div class="col-12 col-xl-10">
      <PageHeaderFilters title="Company Profile">
        <template #actions>
        <button v-if="!isEditing" @click="isEditing = true" class="btn btn-outline-primary rounded-pill px-4 fw-bold shadow-sm">
          <i class="bi bi-pencil-square me-2"></i> Edit Profile
        </button>
        <button v-else @click="cancelEdit" class="btn btn-outline-secondary rounded-pill px-4 fw-bold shadow-sm">
          <i class="bi bi-x-circle me-2"></i> Cancel
        </button>
        </template>
      </PageHeaderFilters>


      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <div v-else class="card bg-white border-0 shadow-sm rounded-4 overflow-hidden">

        <div class="bg-primary text-white p-4 p-md-5 d-flex align-items-center" style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);">
          <div class="bg-white rounded-circle p-1 me-4 shadow-lg overflow-hidden d-flex justify-content-center align-items-center" style="width: 100px; height: 100px;">
            <img v-if="authStore.userUniquifier" :src="`https://api.dicebear.com/7.x/identicon/svg?seed=${authStore.userUniquifier}&backgroundColor=198754`" alt="Avatar" width="100" height="100" />
            <i v-else class="bi bi-person-fill display-1 text-secondary bg-light w-100 h-100 d-flex align-items-center justify-content-center"></i>
          </div>
          <div>
            <h2 class="fw-bold mb-2">{{ profile.name }}</h2>
            <div class="d-flex gap-2 align-items-center">
               <span class="badge bg-light text-dark shadow-sm">{{ profile.industry || 'Industry Pending' }}</span>
               <span v-if="profile.is_approved" class="badge bg-success shadow-sm"><i class="bi bi-shield-check me-1"></i> Institute Verified</span>
               <span v-else class="badge bg-warning text-dark shadow-sm"><i class="bi bi-hourglass me-1"></i> Pending Verification</span>
            </div>
          </div>
        </div>

        <div class="card-body p-4 p-lg-5">
          <form @submit.prevent="saveProfile">

            <h5 class="fw-bold text-dark mb-4 border-bottom pb-2"><i class="bi bi-building-fill me-2 text-primary"></i> Organization Details</h5>
            <div class="row g-4 mb-4">
              <div class="col-lg-6">
                <label class="form-label text-muted fw-semibold small text-uppercase">Company Name *</label>
                <div v-if="!isEditing" class="fs-5 text-dark fw-semibold">{{ profile.name }}</div>
                <input v-else type="text" class="form-control bg-light border-0 py-2" v-model="profile.name" required>
              </div>

              <div class="col-lg-6">
                <label class="form-label text-muted fw-semibold small text-uppercase">Industry *</label>
                <div v-if="!isEditing" class="fs-5 text-dark fw-semibold">{{ profile.industry || 'Not Provided' }}</div>
                <input v-else type="text" class="form-control bg-light border-0 py-2" v-model="profile.industry" required>
              </div>

              <div class="col-lg-6">
                <label class="form-label text-muted fw-semibold small text-uppercase">HR Contact Email *</label>
                <div v-if="!isEditing" class="fs-5 text-dark fw-semibold">{{ profile.hr_contact }}</div>
                <input v-else type="email" class="form-control bg-light border-0 py-2" v-model="profile.hr_contact" required>
              </div>

              <div class="col-lg-6">
                <label class="form-label text-muted fw-semibold small text-uppercase">Official Website *</label>
                <div v-if="!isEditing" class="fs-5 text-dark fw-semibold">
                  <a v-if="profile.website" :href="profile.website" target="_blank">{{ profile.website }}</a>
                  <span v-else class="text-danger">Mandatory for verification</span>
                </div>
                <input v-else type="url" class="form-control bg-light border-0 py-2" v-model="profile.website" placeholder="https://www.company.com" required>
              </div>

              <div class="col-12 mt-5">
                <label class="form-label text-muted fw-semibold small text-uppercase">Company Overview & Culture *</label>
                <div v-if="!isEditing" class="text-dark bg-light p-4 rounded-4" style="white-space: pre-wrap; font-size: 1.05rem;">{{ profile.description || 'No description provided.' }}</div>
                <textarea v-else class="form-control bg-light border-0 py-3" v-model="profile.description" rows="8" required placeholder="Describe your company, mission, and work environment..."></textarea>
              </div>
            </div>

            <div v-if="isEditing" class="text-end mt-5 border-top pt-4">
              <button type="submit" class="btn btn-primary rounded-pill px-4 py-2 fw-semibold shadow-lg" :disabled="isSaving">
                <span v-if="isSaving" class="spinner-border spinner-border-sm me-2"></span> Save Organization Profile
              </button>
            </div>

          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useToastNotifications } from '@/composables/useToastNotification';
import { useAuthStore } from '@/stores/authStore';
import PageHeaderFilters from '@/components/PageHeaderFilters.vue';

const authStore = useAuthStore();
const { addToastNotifications } = useToastNotifications();

const profile = ref({});
const originalProfile = ref({});
const isLoading = ref(true);
const isEditing = ref(false);
const isSaving = ref(false);

const loadProfile = async () => {
  isLoading.value = true;
  try {
    const res = await axios.get('/api/company/profile');
    profile.value = res.data;
    originalProfile.value = JSON.parse(JSON.stringify(res.data));
  } catch (error) {
    addToastNotifications("Failed to load company profile", "error");
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

const cancelEdit = () => {
  profile.value = JSON.parse(JSON.stringify(originalProfile.value));
  isEditing.value = false;
};

const saveProfile = async () => {
  isSaving.value = true;
  try {
    const res = await axios.put('/api/company/profile', profile.value);
    addToastNotifications(res.data.message, "success");
    authStore.userName = res.data.name;
    await loadProfile();
    isEditing.value = false;
  } catch (error) {
    addToastNotifications(error.response?.data?.error || "Error saving profile.", "error");
    console.error(error);
  } finally {
    isSaving.value = false;
  }
};

onMounted(loadProfile);
</script>
