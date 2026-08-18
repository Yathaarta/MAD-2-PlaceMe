<template>
  <div class="row justify-content-center pb-5">
    <div class="col-12 col-xl-10">
      <PageHeaderFilters title="My Profile Settings">
        <template #actions>
         <button v-if="!isEditingProfile" @click="enterEditMode" class="btn btn-outline-primary rounded-pill px-4 fw-bold shadow-sm">
            <i class="bi bi-pencil-square me-2"></i> Edit Profile
          </button>
          <button v-else @click="cancelEditMode" class="btn btn-outline-secondary rounded-pill px-4 fw-bold shadow-sm">
            <i class="bi bi-x-circle me-2"></i> Cancel Editing
          </button>
        </template>
      </PageHeaderFilters>

      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-success" role="status"></div>
      </div>

      <div v-else class="card bg-white border-0 shadow-sm rounded-4 overflow-hidden mb-4">
        <!-- DICEBEAR AVATAR BANNER -->
        <div class="bg-success text-white p-4 p-md-5 d-flex flex-column flex-md-row align-items-center text-center text-md-start" style="background: linear-gradient(135deg, #43a047 0%, #1de9b6 100%);">
          <div class="bg-white rounded-circle p-1 mb-3 mb-md-0 me-md-4 shadow-lg overflow-hidden d-flex justify-content-center align-items-center flex-shrink-0" style="width: 100px; height: 100px;">
            <img v-if="authStore.userUniquifier" :src="`https://api.dicebear.com/7.x/identicon/svg?seed=${authStore.userUniquifier}&backgroundColor=198754`" alt="Avatar" width="75" height="75" />
            <i v-else class="bi bi-person-fill display-1 text-secondary bg-light w-75 h-75 d-flex align-items-center justify-content-center"></i>
          </div>
          <div class="text-break" style="word-wrap: break-word; min-width: 0;">
            <h2 class="fw-bold mb-1">{{ profileForm.full_name }}</h2>
            <p class="mb-0 text-light fs-5"><i class="bi bi-envelope me-2 d-none d-md-inline"></i>{{ profileForm.email }}</p>
          </div>
        </div>

        <div class="card-body p-4 p-md-5">
          <form @submit.prevent="saveProfile">

            <!-- SECTION 1: Personal Details -->
            <h5 class="fw-bold text-success border-bottom pb-2 mb-4"><i class="bi bi-person-badge me-2"></i>Personal Details</h5>
            <div class="row g-4 mb-5">

              <div class="col-12 col-md-6">
                <label class="form-label text-muted">Full Name</label>
                <div v-if="!isEditingProfile" class="fs-5 text-dark fw-semibold">{{ profileForm.full_name }}</div>
                <div v-else>
                  <input type="text" class="form-control bg-light border-0 py-2" v-model="profileForm.full_name" required>
                  <small class="text-muted d-block mt-1">Must follow official registration format (No initials, max 4 words).</small>
                </div>
              </div>

              <div class="col-12 col-md-6">
                <label class="form-label text-muted">Age</label>
                <div v-if="!isEditingProfile" class="fs-5 text-dark fw-semibold">
                  <span v-if="profileForm.age">{{ profileForm.age }} years</span>
                  <span v-else class="badge bg-danger rounded-pill px-3 py-1 fw-normal shadow-sm"><i class="bi bi-exclamation-circle me-1"></i> Missing</span>
                </div>
                <input v-else type="number" class="form-control bg-light border-0 py-2" v-model="profileForm.age" min="16" max="100" placeholder="e.g. 21">
              </div>

            </div>

            <!-- SECTION 2: Academic Education -->
            <div class="d-flex justify-content-between align-items-end border-bottom pb-2 mb-4 mt-5">
               <h5 class="fw-bold text-success mb-0"><i class="bi bi-mortarboard me-2"></i>Academic Education</h5>
               <span v-if="profileForm.education.verified_edu" class="badge bg-success rounded-pill px-3 py-2 shadow-sm"><i class="bi bi-patch-check-fill me-1"></i> Verified</span>
               <span v-else class="badge bg-warning text-dark rounded-pill px-3 py-2 shadow-sm"><i class="bi bi-exclamation-circle-fill me-1"></i> Unverified</span>
            </div>

            <!-- Read-Only Education View -->
            <div v-if="!isEditingProfile" class="row g-4 mb-3">
              <div class="col-md-6">
                <label class="form-label text-muted">Degree</label>
                <div class="fs-5 text-dark fw-semibold">{{ profileForm.education.degree }}</div>
              </div>
              <div class="col-md-6">
                <label class="form-label text-muted">Stream</label>
                <div class="fs-5 text-dark fw-semibold">{{ profileForm.education.stream }}</div>
              </div>
              <div class="col-md-4">
                <label class="form-label text-muted">Current CGPA</label>
                <div class="fs-5 text-dark fw-semibold">
                  <span v-if="profileForm.education.cgpa">{{ profileForm.education.cgpa }}</span>
                  <span v-else class="badge bg-danger rounded-pill px-3 py-1 fw-normal shadow-sm"><i class="bi bi-exclamation-circle me-1"></i> Missing</span>
                </div>
              </div>
              <div class="col-md-4">
                <label class="form-label text-muted">Start Date</label>
                <div class="fs-5 text-dark fw-semibold">
                  <span v-if="profileForm.education.start_year">{{ formatMonthYear(profileForm.education.start_year) }}</span>
                  <span v-else class="badge bg-danger rounded-pill px-3 py-1 fw-normal shadow-sm"><i class="bi bi-exclamation-circle me-1"></i> Missing</span>
                </div>
              </div>
              <div class="col-md-4">
                <label class="form-label text-muted">End Date (Graduation)</label>
                <div class="fs-5 text-dark fw-semibold">
                  <span v-if="profileForm.education.end_year">{{ formatMonthYear(profileForm.education.end_year) }}</span>
                  <span v-else class="badge bg-danger rounded-pill px-3 py-1 fw-normal shadow-sm"><i class="bi bi-exclamation-circle me-1"></i> Missing</span>
                </div>
              </div>
            </div>

            <!-- Edit-Mode Education View (Dropdowns active) -->
            <div v-else class="row g-4 mb-3">
              <div class="col-md-6">
                <label class="form-label text-muted">Degree</label>
                <select v-model="profileForm.education.degree_id" @change="handleDegreeChange" class="form-select bg-light border-0 py-2" required>
                  <option value="" disabled>Select Degree</option>
                  <option v-for="deg in degreeOptions" :key="deg.id" :value="deg.id">{{ deg.name }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label text-muted">Stream</label>
                <select v-model="profileForm.education.stream_id" class="form-select bg-light border-0 py-2" required :disabled="!profileForm.education.degree_id || isStreamsLoading">
                  <option value="" disabled>{{ isStreamsLoading ? 'Loading...' : 'Select Stream' }}</option>
                  <option v-for="st in streamOptions" :key="st.id" :value="st.id">{{ st.name }}</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label text-muted">Current CGPA</label>
                <input type="number" class="form-control bg-light border-0 py-2" v-model="profileForm.education.cgpa" step="0.01" min="0" max="10" placeholder="e.g. 8.5">
              </div>
              <div class="col-md-4">
                <label class="form-label text-muted">Start Month/Year</label>
                <input type="month" class="form-control bg-light border-0 py-2" v-model="profileForm.education.start_year">
              </div>
              <div class="col-md-4">
                <label class="form-label text-muted">End Month/Year</label>
                <input type="month" class="form-control bg-light border-0 py-2" v-model="profileForm.education.end_year">
              </div>
            </div>

            <!-- SECTION 3: Resume -->
            <h5 class="fw-bold text-success border-bottom pb-2 mb-4 mt-5"><i class="bi bi-file-earmark-pdf me-2"></i>Resume & Links</h5>
            <div class="row g-4 mb-4">
              <div class="col-12">
                <label class="form-label text-muted">Resume URL</label>

                <div v-if="!isEditingProfile" class="fs-5 text-dark fw-semibold">
                  <a v-if="profileForm.resume_url" :href="profileForm.resume_url" target="_blank" class="text-primary text-decoration-none">
                    <i class="bi bi-link-45deg me-1"></i> {{ profileForm.resume_url }}
                  </a>
                  <span v-else class="badge bg-danger rounded-pill px-3 py-1 fw-normal shadow-sm"><i class="bi bi-exclamation-circle me-1"></i> Missing (Add to Apply for Drives)</span>
                </div>

                <input v-else type="url" class="form-control bg-light border-0 py-2" v-model="profileForm.resume_url" placeholder="https://drive.google.com/...">
              </div>
            </div>

            <!-- Save/Cancel Buttons (Only in Edit Mode) -->
            <div v-if="isEditingProfile" class="text-end mt-5 border-top pt-4">
              <button type="button" class="btn btn-light rounded-pill px-4 me-3 fw-bold shadow-sm" @click="cancelEditMode">Cancel</button>
              <button type="submit" class="btn btn-success rounded-pill px-5 py-2 fw-bold shadow-sm" :disabled="isSaving">
                <span v-if="isSaving" class="spinner-border spinner-border-sm me-2"></span>
                Save All Changes
              </button>
            </div>

          </form>
        </div>
      </div>

      <!-- DANGER ZONE -->
      <div class="card border-danger border-opacity-25 shadow-sm rounded-4 mt-5">
        <div class="card-body p-4 p-md-5">
           <h5 class="fw-bold text-danger mb-3"><i class="bi bi-exclamation-triangle-fill me-2"></i> Danger Zone</h5>
           <p class="text-muted mb-4">Permanently delete your account. This will erase your profile, education history, and withdraw all your existing job applications. This action cannot be undone.</p>
           <button class="btn btn-outline-danger fw-bold rounded-pill px-4" data-bs-toggle="modal" data-bs-target="#deleteModal">Delete Account</button>
        </div>
      </div>

    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg rounded-4">
          <div class="modal-header bg-danger text-white border-0 py-3 rounded-top-4">
            <h5 class="modal-title fw-bold"><i class="bi bi-trash3-fill me-2"></i> Confirm Deletion</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-4">
            <p class="mb-0 fw-semibold text-dark">Are you absolutely sure you want to delete your account?</p>
            <p class="small text-danger mt-2 mb-0">All applications will be instantly withdrawn and data permanently wiped.</p>
          </div>
          <div class="modal-footer border-0 pb-4 pe-4">
            <button type="button" class="btn btn-light rounded-pill px-4" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger rounded-pill px-4 fw-bold" @click="confirmDelete" :disabled="isDeleting">
              <span v-if="isDeleting" class="spinner-border spinner-border-sm me-2" role="status"></span>
              Yes, Delete My Account
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { Modal } from 'bootstrap';
import { useToastNotifications } from '@/composables/useToastNotification';
import { useAuthStore } from '@/stores/authStore';
import PageHeaderFilters from '@/components/PageHeaderFilters.vue';

const router = useRouter();
const authStore = useAuthStore();
const { addToastNotifications } = useToastNotifications();

const isLoading = ref(true);
const isSaving = ref(false);
const isDeleting = ref(false);
const isEditingProfile = ref(false);

const originalProfileData = ref(null);
const profileForm = ref({
  full_name: '', resume_url: '', email: '', age: '',
  education: { degree: '', degree_id: '', stream: '', stream_id: '', cgpa: '', start_year: '', end_year: '', verified_edu: false }
});

const degreeOptions = ref([]);
const streamOptions = ref([]);
const isStreamsLoading = ref(false);


const formatMonthYear = (val) => {
  if (!val) return '';
  const [year, month] = val.split('-');
  const date = new Date(year, month - 1);
  return date.toLocaleString('default', { month: 'short', year: 'numeric' });
};


const fetchDegrees = async () => {
  try {
    const res = await axios.get('/api/degrees');
    degreeOptions.value = res.data;
  } catch (e) {
    console.error(e);
  }
};

const fetchStreams = async (degId) => {
  isStreamsLoading.value = true;
  try {
    const res = await axios.get(`/api/streams/${degId}`);
    streamOptions.value = res.data;
  } catch (error) {
    console.error(error);
  } finally {
    isStreamsLoading.value = false;
  }
};

const handleDegreeChange = async () => {
  profileForm.value.education.stream_id = '';
  if (profileForm.value.education.degree_id) {
    await fetchStreams(profileForm.value.education.degree_id);
  }
};

const loadProfile = async () => {
  isLoading.value = true;
  try {
    const res = await axios.get('/api/student/profile');
    profileForm.value = res.data;
    originalProfileData.value = JSON.parse(JSON.stringify(res.data));
  } catch (error) {
    addToastNotifications("Failed to load profile details", "error");
    console.error(error)
  } finally {
    isLoading.value = false;
  }
};

const enterEditMode = async () => {
  isEditingProfile.value = true;
  if (degreeOptions.value.length === 0) await fetchDegrees();
  if (profileForm.value.education.degree_id) await fetchStreams(profileForm.value.education.degree_id);
};

const cancelEditMode = () => {
  profileForm.value = JSON.parse(JSON.stringify(originalProfileData.value));
  isEditingProfile.value = false;
};

const saveProfile = async () => {
  isSaving.value = true;
  try {
    const res = await axios.put('/api/student/profile', profileForm.value);
    addToastNotifications(res.data.message, "success");

    authStore.userName = res.data.full_name;

    await loadProfile();
    isEditingProfile.value = false;

    if (!res.data.verified_edu && originalProfileData.value.education.verified_edu) {
        addToastNotifications("Academic details changed. Your verification has been revoked.", "error");
    }
  } catch (error) {
    addToastNotifications(error.response?.data?.error || "Failed to save profile", "error");
  } finally {
    isSaving.value = false;
  }
};

const confirmDelete = async () => {
  isDeleting.value = true;
  try {
    await axios.delete('/api/student/profile');

    const modalEl = document.getElementById('deleteModal');
    const modalInstance = Modal.getInstance(modalEl);
    if(modalInstance) modalInstance.hide();
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => backdrop.remove());
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';

    authStore.logout();
    addToastNotifications("Account deleted permanently.", "success");
    router.push('/');
  } catch (error) {
    addToastNotifications(error.response?.data?.error || "Failed to delete account.", "error");
    isDeleting.value = false;
  }
};

onMounted(loadProfile);
</script>
