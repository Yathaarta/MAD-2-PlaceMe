<template>
  <div>
    <PageHeaderFilters title="Placement Drives">
      <template #actions>
        <button class="btn btn-primary rounded-pill shadow-sm fw-semibold px-4" @click="openCreateModal"
        :disabled="(dashboardData && !dashboardData.company.is_approved) || !dashboardData">
          <i class="bi bi-plus-lg me-2"></i> Post New Drive
        </button>
      </template>
    </PageHeaderFilters>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <!-- Drives Grid -->
    <div v-else class="row g-4">
      <div v-for="drive in drives" :key="drive.id" class="col-12 col-lg-6 col-xl-4">
        <DriveCard :isActive="drive.is_active" :minCgpa="drive.min_cgpa || 'No minimum'" statLabel="Applicants"
          :statValue="drive.applicants" statValueClass="text-primary"
        >
          <template #header-left>
            <span v-if="!drive.is_approved" class="badge bg-warning text-dark">Pending Admin</span>
            <span v-else-if="!drive.is_active" class="badge bg-danger">Closed Early</span>
            <span v-else class="badge bg-success">Approved & Active</span>
          </template>

          <template #header-right>
            <div class="dropdown position-relative">
              <button class="btn btn-sm btn-light rounded-circle" type="button" @click.stop="toggleDropdown(drive.id)">
                <i class="bi bi-three-dots-vertical"></i>
              </button>
              <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0 position-absolute"
                  :class="{ 'show d-block': activeDropdown === drive.id }"
                  style="right: 0; top: 100%; z-index: 1000;">
                <li>
                  <button class="dropdown-item py-2 fw-semibold text-primary" @click.stop="openEditModal(drive)">
                    <i class="bi bi-info-circle me-2"></i> View/Edit Details
                  </button>
                </li>
                <li v-if="drive.is_active">
                  <button class="dropdown-item py-2 fw-semibold text-danger" @click.stop="endDriveEarly(drive.id)">
                    <i class="bi bi-stop-circle-fill me-2"></i> Close Drive Early
                  </button>
                </li>
              </ul>
            </div>
          </template>

          <template #title-section>
            <h4 class="fw-bold mb-1 text-truncate" :title="drive.role">{{ drive.role }}</h4>
            <div class="text-danger fw-bold small mb-3"><i class="bi bi-clock-history me-1"></i> Deadline: {{ drive.deadline }}</div>
          </template>

          <template #actions>
            <router-link to="/company-dashboard/applicants" class="btn btn-outline-primary w-100 rounded-pill fw-bold shadow-sm py-2">
              Manage Candidates
            </router-link>
          </template>
        </DriveCard>
      </div>

      <EmptyState v-if="drives.length === 0" icon="bi-briefcase" title="No placement drives created yet."
      message="Click 'Post New Drive' to start recruiting." />
    </div>

    <BaseModal modalId="createDriveModal" title="Create Placement Drive" icon="bi-briefcase-fill"
     :selectedObject="{}" size="modal-lg">
        <form @submit.prevent="createDrive">
          <div class="row g-3">
            <div class="col-lg-8">
              <label class="form-label fw-bold">Job Title *</label>
              <input type="text" class="form-control bg-light border-0 py-2" v-model="form.job_title" required placeholder="e.g. Graduate Software Engineer">
            </div>
            <div class="col-lg-4">
              <label class="form-label fw-bold">Deadline *</label>
              <input type="date" class="form-control bg-light border-0 py-2" :min="todayDate" v-model="form.deadline" required>
            </div>
            <div class="col-12">
              <label class="form-label fw-bold">Job Description</label>
              <textarea class="form-control bg-light border-0 py-2" v-model="form.job_description" rows="5" placeholder="Describe the role, responsibilities, and package..."></textarea>
            </div>
            <div class="col-lg-4">
              <label class="form-label fw-bold">Minimum CGPA Requirement</label>
              <input type="number" step="0.1" min="0" max="10" class="form-control bg-light border-0 py-2" v-model="form.min_cgpa" placeholder="e.g. 7.5">
            </div>

            <!-- Degrees & Streams -->
            <div class="col-12 mt-4">
              <div class="d-flex justify-content-between align-items-center border-bottom pb-2 mb-3">
                  <label class="form-label fw-bold text-primary mb-0">Eligibility Criteria (Degrees & Streams)</label>
                  <button type="button" class="btn btn-sm btn-outline-primary rounded-pill fw-semibold" @click="addCriteriaBlock">
                    <i class="bi bi-plus-lg"></i> Add Degree Group
                  </button>
              </div>

              <div v-for="(block, index) in form.criteriaBlocks" :key="index" class="bg-light p-3 rounded-4 mb-3 border">
                  <div class="d-flex justify-content-between mb-2">
                    <div class="flex-grow-1 me-3">
                      <label class="small text-muted fw-semibold">Select Degree:</label>
                      <select class="form-select fw-semibold border-0 bg-white" v-model="block.degree_id" required>
                          <option disabled value="">Choose a Degree...</option>
                          <option v-for="deg in degrees" :key="deg.id" :value="deg.id">{{ deg.name }}</option>
                      </select>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-danger align-self-end mb-1" @click="removeCriteriaBlock(index)" v-if="form.criteriaBlocks.length > 1">
                        <i class="bi bi-trash"></i>
                    </button>
                  </div>

                  <div v-if="block.degree_id" class="mt-3">
                    <label class="small text-muted fw-semibold text-uppercase mb-2">Applicable Streams for this Degree:</label>
                    <div class="d-flex flex-wrap gap-3 p-2 bg-white rounded-3">
                        <div class="form-check" v-for="stream in getStreamsForDegree(block.degree_id)" :key="stream.id">
                          <input class="form-check-input" type="checkbox" :value="stream.id" v-model="block.streams" :id="`st_${index}_${stream.id}`">
                          <label class="form-check-label" :for="`st_${index}_${stream.id}`">{{ stream.name }}</label>
                        </div>
                    </div>
                  </div>
              </div>
            </div>
          </div>
          <div class="text-end mt-4 pt-3 border-top">
            <button type="button" class="btn btn-light rounded-pill px-4 me-2 fw-semibold" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary rounded-pill px-5 fw-semibold shadow-sm" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span> Post Drive
            </button>
          </div>
        </form>
    </BaseModal>

    <BaseModal modalId="editDriveModal" title="View & Edit Drive Details" icon="bi-pencil-square" :selectedObject="{}" headerClass="bg-dark text-white" size="modal-lg">
      <div class="alert alert-info py-2 small d-flex align-items-center rounded-3 mb-4 border-0">
          <i class="bi bi-shield-lock-fill fs-4 me-3 text-info"></i>
          <div><strong>Integrity Lock Active:</strong> Core criteria (Title, Min CGPA, Degrees) are locked to maintain application fairness. You may extend the deadline or update the description (interview links, package updates).</div>
      </div>

      <form @submit.prevent="updateDrive">
        <div class="row g-3">
          <!-- Locked feilds -->
          <div class="col-md-8">
            <label class="form-label fw-bold text-muted small">Job Title <i class="bi bi-lock-fill"></i></label>
            <div class="fs-5 fw-bold text-dark mb-2">{{ editForm.job_title }}</div>
          </div>
          <div class="col-md-4">
            <label class="form-label fw-bold text-muted small">Min CGPA <i class="bi bi-lock-fill"></i></label>
            <div class="fs-5 fw-bold text-dark mb-2">{{ editForm.min_cgpa }}</div>
          </div>

          <div class="col-12 mt-2">
            <label class="form-label fw-bold text-muted small">Targeted Criteria <i class="bi bi-lock-fill"></i></label>
            <div class="mb-3">
              <span v-for="deg in editForm.degree_names" :key="deg" class="badge bg-secondary me-2 py-2 px-3 rounded-pill">{{ deg }}</span>
            </div>
            <div>
              <span v-for="st in editForm.stream_names" :key="st" class="badge border border-secondary text-secondary me-2 py-2 px-3 rounded-pill">{{ st }}</span>
            </div>
          </div>

          <!-- Editable feilds -->
          <div class="col-12 mt-4"><h6 class="fw-bold border-bottom pb-2 text-dark">Updateable Information</h6></div>

          <div class="col-md-4">
            <label class="form-label fw-bold">Extend Application Deadline *</label>
            <input type="date" class="form-control bg-light border-0 py-2" :min="todayDate" v-model="editForm.deadline" required :disabled="!editForm.is_active">
          </div>
          <div class="col-12">
            <label class="form-label fw-bold">Update Job Description & Instructions</label>
            <textarea class="form-control bg-light border-0 py-2" v-model="editForm.job_description" rows="8" style="white-space: pre-wrap;" :disabled="!editForm.is_active"></textarea>
            <small class="text-muted">Preserves paragraphs and line breaks.</small>
          </div>
        </div>

        <div class="text-end mt-4 pt-3 border-top">
          <button type="button" class="btn btn-light rounded-pill px-4 me-2 fw-semibold" data-bs-dismiss="modal">Close</button>
          <button v-if="editForm.is_active" type="submit" class="btn btn-dark rounded-pill px-5 fw-semibold shadow-sm" :disabled="isUpdating">
            <span v-if="isUpdating" class="spinner-border spinner-border-sm me-2"></span> Save Changes
          </button>
        </div>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import axios from 'axios';
import { Modal } from 'bootstrap';
import { useToastNotifications } from '@/composables/useToastNotification';
import EmptyState from '@/components/EmptyState.vue';
import BaseModal from '@/components/BaseModal.vue';
import DriveCard from '@/components/DriveCard.vue';
import PageHeaderFilters from '@/components/PageHeaderFilters.vue';
import { useFetchData } from '@/composables/useFetchData';

const { addToastNotifications } = useToastNotifications();
const { data:dashboardData, fetchData:fetchDashboardData } = useFetchData('/api/dashboard/company','Failed to load company data', true);
const { data: drives, isLoading, fetchData: fetchDrives } = useFetchData('/api/company/drives','Failed to load your placement drives. Please refresh.');

const degrees = ref([]);
const streams = ref([]);

const activeDropdown = ref(null);
const toggleDropdown = (id) => { activeDropdown.value = activeDropdown.value === id ? null : id; };
const closeDropdown = () => { activeDropdown.value = null; };

const isSubmitting = ref(false);
let createModalInstance = null;
const form = ref({
  job_title: '', job_description: '', min_cgpa: '', deadline: '',
  criteriaBlocks: [{ degree_id: '', streams: [] }]
});

const addCriteriaBlock = () => { form.value.criteriaBlocks.push({ degree_id: '', streams: [] }); };
const removeCriteriaBlock = (index) => { form.value.criteriaBlocks.splice(index, 1); };

const getStreamsForDegree = (degId) => {
  return streams.value.filter(s => s.degree_id === degId);
};

// Edit Drive State
const isUpdating = ref(false);
let editModalInstance = null;
const editingDriveId = ref(null);
const editForm = ref({
  job_title: '', job_description: '', min_cgpa: '', deadline: '',
  is_active: true, degree_names: [], stream_names: []
});

const todayDate = computed(() => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
});

const fetchOptions = async () => {
  try {
    const degRes = await axios.get('/api/degrees');
    degrees.value = degRes.data;
    let allStreams = [];
    for (let deg of degrees.value) {
       const streamRes = await axios.get(`/api/streams/${deg.id}`);
       allStreams = [...allStreams, ...streamRes.data];
    }
    streams.value = Array.from(new Map(allStreams.map(item => [item.id, item])).values());
  } catch(e) {
    console.error("Error loading degree/stream data:", e);
  }
};

const openCreateModal = () => {
  form.value = {
    job_title: '', job_description: '', min_cgpa: '', deadline: '',
    criteriaBlocks: [{ degree_id: '', streams: [] }]
  };
  if (!createModalInstance) createModalInstance = new Modal(document.getElementById('createDriveModal'));
  createModalInstance.show();
};

const createDrive = async () => {
  const selectedDegrees = form.value.criteriaBlocks.map(b => b.degree_id).filter(id => id).join(',');
  const selectedStreams = form.value.criteriaBlocks.map(b => b.streams).flat().join(',');

  if (!selectedDegrees || !selectedStreams) {
     addToastNotifications("Incomplete criteria: Please select at least one Degree and its Stream.", "error");
     return;
  }

  isSubmitting.value = true;
  try {
    const payload = {
      job_title: form.value.job_title,
      job_description: form.value.job_description,
      min_cgpa: form.value.min_cgpa,
      deadline: form.value.deadline,
      allowed_degrees: selectedDegrees,
      allowed_streams: selectedStreams
    };
    const res = await axios.post('/api/company/drives', payload);
    addToastNotifications(res.data.message, "success");
    createModalInstance.hide();
    await fetchDrives();
    await fetchDashboardData();
  } catch (err) {
    addToastNotifications(err.response?.data?.error || "Failed to post drive.", "error");
    console.error(err);
  } finally {
    isSubmitting.value = false;
  }
};

const openEditModal = (drive) => {
  activeDropdown.value = null;
  editingDriveId.value = drive.id;

  let rawDate = "";
  if (drive.deadline && drive.deadline !== 'TBD') {
     const d = new Date(drive.deadline);
     rawDate = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  }

  editForm.value = {
    job_title: drive.role,
    job_description: drive.description,
    min_cgpa: drive.min_cgpa || 'None',
    deadline: rawDate,
    is_active: drive.is_active,
    degree_names: drive.degree_names || [],
    stream_names: drive.stream_names || []
  };

  if (!editModalInstance) editModalInstance = new Modal(document.getElementById('editDriveModal'));
  editModalInstance.show();
};

const updateDrive = async () => {
  isUpdating.value = true;
  try {
    const res = await axios.put(`/api/company/drives/${editingDriveId.value}`, {
      job_description: editForm.value.job_description,
      deadline: editForm.value.deadline
    });
    addToastNotifications(res.data.message, "success");
    editModalInstance.hide();
    await fetchDrives();
  } catch (err) {
    addToastNotifications(err.response?.data?.error || "Update failed.", "error");
    console.error(err);
  } finally {
    isUpdating.value = false;
  }
};

const endDriveEarly = async (id) => {
  activeDropdown.value = null;
  if (!confirm("Are you sure you want to end this drive early? This action will prevent any new students from applying.")) return;

  try {
    const res = await axios.put(`/api/company/drives/${id}`, { is_active: false });
    addToastNotifications(res.data.message, "success");
    await fetchDrives();
    await fetchDashboardData();
  } catch(e) {
    addToastNotifications("Could not close the drive. Please try again.", "error");
    console.error(e);
  }
};

onMounted(() => {
  fetchOptions();
  document.addEventListener('click', closeDropdown);
});
onUnmounted(() => {
  document.removeEventListener('click', closeDropdown);
});
</script>

<style scoped>
.dropdown-menu { border-radius: 0.75rem; border: none; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.dropdown-item { transition: background-color 0.2s; }
.dropdown-item:hover { background-color: #f8f9fa; }
</style>
