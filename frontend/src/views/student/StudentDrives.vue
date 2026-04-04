<template>
  <div>
    <PageHeaderFilters title="Campus Placement Drives" searchPlaceholder="Search Role or Company"
      v-model:searchQuery="searchQuery" showSearch="true" />

    <!-- If Resume Missing -->
    <div v-if="!isLoading && !hasResume" class="alert alert-danger d-flex align-items-center rounded-3 shadow-sm mb-4">
      <i class="bi bi-exclamation-octagon-fill fs-3 me-3"></i>
      <div>
        <strong>Action Required:</strong> You cannot apply to any drives until you update your Profile with a valid Resume URL.
      </div>
    </div>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <!-- Drives Grid -->
    <div v-else class="row g-4">
      <div v-for="drive in filteredDrives" :key="drive.id" class="col-12 col-lg-6 col-xl-4">
        <DriveCard :isActive="true" :minCgpa="drive.eligibility" statLabel="Industry"
          :statValue="drive.industry" statValueClass="text-secondary"
        >
          <template #header-left>
            <span class="badge bg-primary bg-opacity-10 text-primary border border-primary rounded-pill px-3 py-1">
               {{ drive.company }}
            </span>
          </template>

          <template #header-right>
            <span class="text-danger fw-bold small"><i class="bi bi-clock-history me-1"></i>{{ drive.deadline }}</span>
          </template>

          <template #title-section>
            <h4 class="fw-bold mb-1 text-dark">{{ drive.role }}</h4>
            <p class="text-muted small mb-3 line-clamp-2" :title="drive.description">{{ drive.description || 'No description provided.' }}</p>
          </template>

          <template #actions>
            <!-- If Already Applied -->
            <button v-if="drive.has_applied" class="btn btn-outline-success w-100 rounded-pill fw-bold shadow-sm py-2" @click="openDriveDetails(drive)">
              <i class="bi bi-check-circle-fill me-2"></i> Applied - View Details
            </button>
            <!-- If Eligible to Apply -->
            <button v-else-if="drive.is_eligible" class="btn btn-outline-primary w-100 rounded-pill fw-bold shadow-sm py-2" @click="openDriveDetails(drive)">
              <i class="bi bi-info-circle me-2"></i> View Details & Apply
            </button>
            <!-- If Not Eligible -->
            <button v-else class="btn btn-outline-danger w-100 rounded-pill fw-bold shadow-sm py-2" @click="openDriveDetails(drive)">
              <i class="bi bi-lock-fill me-2"></i> Not Eligible
            </button>
          </template>
        </DriveCard>
      </div>
      <EmptyState v-if="filteredDrives.length === 0"  icon="bi-briefcase" title="No placement drives available right now."/>
    </div>

    <BaseModal modalId="studentDriveDetailsModal" title="Placement Drive Details" icon="bi-building" :selectedObject="selectedDrive" size="modal-xl">
      <template v-if="selectedDrive">
            <div class="border-bottom">
              <div class="d-flex justify-content-between align-items-start mb-1">
                <h3 class="fw-bold text-dark mb-0">{{ selectedDrive.role }}</h3>
                <span class="badge bg-danger fw-semibold rounded-pill fs-6"><i class="bi bi-clock me-1"></i> Due: {{ selectedDrive.deadline }}</span>
              </div>
              <div class="fs-5 text-primary fw-semibold"><i class="bi bi-building me-2"></i>{{ selectedDrive.company }}</div>
            </div>

            <div class="pt-4">
              <!-- Job Desc -->
              <h6 class="fw-bold text-muted text-uppercase mb-3">Role Overview</h6>
              <p class="mb-4 text-dark small bg-light p-2 rounded-2" style="white-space: pre-wrap; max-height: 300px; overflow-y: auto;">
                {{ selectedDrive.description || 'No detailed description provided by the company.' }}
              </p>

              <hr class="text-muted opacity-25">

              <!-- Eligibility -->
              <h6 class="fw-bold text-muted text-uppercase mb-3 mt-4">Eligibility Requirements</h6>
              <div class="row g-3 p-3 rounded-3 mx-0">
                 <div class="col-md-6">
                   <div class="small fw-bold text-muted">Minimum CGPA required:</div>
                   <div class="fw-bold text-dark fs-5">{{ selectedDrive.eligibility }}</div>
                 </div>
                 <div class="col-md-6">
                   <div class="small fw-bold text-muted">Your Status:</div>
                   <div v-if="selectedDrive.is_eligible" class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i> Eligible to Apply</div>
                   <div v-else class="text-danger fw-bold"><i class="bi bi-x-circle-fill me-1"></i> {{ selectedDrive.ineligibility_reason }}</div>
                 </div>
              </div>

              <hr class="text-muted opacity-50">

              <!-- Company Profile -->
              <h6 class="fw-bold text-uppercase mb-1 mt-4">About {{ selectedDrive.company }}</h6>
              <div class="mb-4">
                <span class="badge fw-semibold bg-secondary mb-3">{{ selectedDrive.industry }}</span>
                <p class="text-dark p-2 small bg-light rounded-2" style="white-space: pre-wrap; max-height: 300px; overflow-y: auto;">{{ selectedDrive.company_desc || 'No company overview provided.' }}</p>
              </div>
              <div class="small fw-semibold text-primary" v-if="selectedDrive.hr_contact">
                 <span class="text-dark fw-bold"><i class="bi bi-envelope-fill me-1"></i> HR Contact:</span> {{ selectedDrive.hr_contact }}
              </div>
            </div>
      </template>
      <template #footer>
            <button type="button" class="btn btn-outline-secondary rounded-pill px-4 fw-semibold" data-bs-dismiss="modal">Close</button>

            <!--Apply Buttons -->
            <button v-if="selectedDrive.has_applied" class="btn btn-success rounded-pill px-5 fw-semibold shadow-sm disabled">
               <i class="bi bi-check-circle-fill me-2"></i> Already Applied
            </button>

            <button v-else-if="selectedDrive.is_eligible" class="btn btn-primary rounded-pill px-5 fw-semibold shadow-sm" @click="apply(selectedDrive.id)" :disabled="applyingId === selectedDrive.id">
               <span v-if="applyingId === selectedDrive.id" class="spinner-border spinner-border-sm me-2"></span>
               <span v-else><i class="bi bi-send-fill me-2"></i> Apply Now</span>
            </button>

            <button v-else class="btn btn-danger rounded-pill px-5 fw-semibold shadow-sm disabled" title="You do not meet the criteria">
               <i class="bi bi-lock-fill me-2"></i> Not Eligible
            </button>
      </template>
    </BaseModal>


  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';
import { Modal } from 'bootstrap';
import { useToastNotifications } from '@/composables/useToastNotification';
import DriveCard from '@/components/DriveCard.vue';
import EmptyState from '@/components/EmptyState.vue';
import PageHeaderFilters from '@/components/PageHeaderFilters.vue';
import BaseModal from '@/components/BaseModal.vue';
import { useFetchData } from '@/composables/useFetchData';

const { addToastNotifications } = useToastNotifications();
const { data: apiResponse, isLoading, fetchData: fetchDrives } = useFetchData(
  '/api/student/drives',
  'Failed to fetch placement drives. Please try again.'
);

const drives = computed(() => apiResponse.value.drives || []);
const hasResume = computed(() => apiResponse.value.has_resume || false);

const applyingId = ref(null);
const searchQuery = ref('');

const selectedDrive = ref(null);
let driveModalInstance = null;

const filteredDrives = computed(() => {
  if (!searchQuery.value) return drives.value;
  const q = searchQuery.value.toLowerCase();
  return drives.value.filter(d =>
    d.role.toLowerCase().includes(q) ||
    d.company.toLowerCase().includes(q)
  );
});

const openDriveDetails = (drive) => {
  selectedDrive.value = drive;
  if (!driveModalInstance) {
    driveModalInstance = new Modal(document.getElementById('studentDriveDetailsModal'));
  }
  driveModalInstance.show();
};

const apply = async (id) => {
  applyingId.value = id;
  try {
    const res = await axios.post(`/api/student/apply/${id}`);
    addToastNotifications(res.data.message, "success");
    if (driveModalInstance) {
       driveModalInstance.hide();
    }
    fetchDrives();
  } catch (err) {
    addToastNotifications(err.response?.data?.error || "Failed to submit application.", "error");
  } finally {
    applyingId.value = null;
  }
};
</script>

<style scoped>
.line-clamp-2 {
  display: block;
  overflow: hidden;
  line-height: 1.5em;
  max-height: calc(2 * 1.5em);
}
</style>
