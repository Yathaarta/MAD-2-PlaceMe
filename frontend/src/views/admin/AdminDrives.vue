<template>
  <div>
    <PageHeaderFilters title="Manage Placement Drives">
      <template #actions>
        <div class="d-flex gap-2">
          <input type="text" class="form-control bg-white shadow-sm border-0 rounded-pill px-3"
            placeholder="Search Role or Company..." v-model="searchQuery" style="max-width: 250px;">
          <select class="form-select bg-white shadow-sm border-0 rounded-pill" v-model="statusFilter"
            style="max-width: 220px;">
            <option value="all">All Drives</option>
            <optgroup label="Active Workflow" class="fw-semibold">
              <option value="pending">Action Required (Pending)</option>
              <option value="live">Live & Approved</option>
            </optgroup>
            <optgroup label="Historical" class="fw-semibold">
              <option value="closed">Inactive / Closed</option>
            </optgroup>
          </select>
        </div>
      </template>
    </PageHeaderFilters>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <DataTable v-else :headers="['Company', 'Job Role', 'Deadline', 'Status', 'Actions']">
      <tr v-for="d in filteredDrives" :key="d.id" :class="{ 'opacity-75': !d.is_active }">
        <td class="py-3 px-5 fw-bold text-primary">{{ d.company }}</td>
        <td class="py-3 px-5 cursor-pointer" @click="viewDriveDetails(d)">
          <span class="fw-semibold text-dark">{{ d.role }}</span>
          <i class="bi bi-info-circle ms-2 small text-muted"></i>
        </td>
        <td class="py-3 px-5 text-danger fw-semibold"><i class="bi bi-clock-history me-2"></i>{{ d.deadline }}</td>
        <td class="py-3 px-5">
          <span v-if="!d.is_approved" class="badge bg-warning text-dark rounded-pill shadow-sm">Pending</span>
          <span v-else-if="!d.is_active" class="badge bg-danger rounded-pill shadow-sm">Closed Early</span>
          <span v-else class="badge bg-success rounded-pill shadow-sm">Approved</span>
        </td>
        <td class="py-3 text-center">
          <button v-if="!d.is_approved" class="btn btn-sm btn-success rounded-pill fw-semibold shadow-sm"
            @click.stop="approve(d.id)">
            Approve Drive
          </button>
        </td>
      </tr>
      <template #empty v-if="filteredDrives.length === 0">
        <EmptyState icon="bi-briefcase" title="No placement drives found"></EmptyState>
      </template>
    </DataTable>


    <BaseModal modalId="driveDetailsModal" title="Placement Drive Verification" icon="bi-briefcase-fill"
      :selectedObject="selectedDrive" size="modal-lg">
      <template v-if="selectedDrive">

        <div class="d-flex justify-content-between align-items-start mb-4 pb-3 border-bottom">
          <div>
            <h2 class="fw-bold mb-1 fs-4 text-dark">{{ selectedDrive.role }}</h2>
            <div class="fs-6 text-primary fw-semibold"><i class="bi bi-building me-2"></i>{{ selectedDrive.company }}
            </div>
          </div>
          <span class="badge bg-light border text-dark fw-semibold shadow-sm">
            <i class="bi bi-calendar-x me-2 text-danger"></i>
            Due: {{ selectedDrive.deadline }}</span>
        </div>

        <div class="row g-3 mb-5 bg-light p-4 rounded-4 shadow-sm border mx-0">
          <div class="col-lg-4">
            <label class="text-muted small fw-semibold text-uppercase mb-1">Status</label>
            <div class="fw-bold fs-5" :class="selectedDrive.is_approved ? 'text-success' : 'text-warning text-dark'">
              <i v-if="selectedDrive.is_approved" class="bi bi-check-circle-fill me-1"></i>
              <i v-else class="bi bi-hourglass-split me-1"></i>
              {{ selectedDrive.is_approved ? 'Approved' : 'Pending Approval' }}
            </div>
          </div>
          <div class="col-lg-4">
            <label class="text-muted small fw-semibold text-uppercase mb-1">Min CGPA Required</label>
            <div class="fw-bold text-dark fs-5">{{ selectedDrive.min_cgpa }}</div>
          </div>

          <div class="col-12 mt-4 pt-3 border-top">
            <label class="text-muted small fw-semibold text-uppercase mb-2">Targeted Degrees</label>
            <div v-if="selectedDrive.degree_names && selectedDrive.degree_names.length > 0">
              <span v-for="deg in selectedDrive.degree_names" :key="deg"
                class="badge bg-primary bg-opacity-10 text-primary border border-primary me-2 px-3 py-2 mb-2 rounded-pill shadow-sm">
                {{ deg }}
              </span>
            </div>
            <div v-else class="text-muted fst-italic">No specific degrees targeted.</div>
          </div>

          <div class="col-12">
            <label class="text-muted small fw-semibold text-uppercase mb-2">Targeted Streams</label>
            <div v-if="selectedDrive.stream_names && selectedDrive.stream_names.length > 0">
              <span v-for="stream in selectedDrive.stream_names" :key="stream"
                class="badge bg-white text-secondary border border-secondary me-2 px-3 py-2 mb-2 rounded-pill shadow-sm">
                {{ stream }}
              </span>
            </div>
            <div v-else class="text-muted fst-italic">No specific streams targeted.</div>
          </div>
        </div>

        <!-- Job Description -->
        <div>
          <h5 class="fw-bold text-dark mb-3"><i class="bi bi-card-text me-1 text-primary"></i> Job Description &
            Details
          </h5>
          <div class="text-dark bg-white border p-4 rounded-4 shadow-sm" style="white-space: pre-wrap;">
            {{ selectedDrive.description || 'The company did not provide a detailed description.' }}
          </div>
        </div>

        <div class="alert alert-info py-3 mt-5 mb-0 rounded-3 shadow-sm border-0 d-flex align-items-center"
          v-if="!selectedDrive.is_approved">
          <i class="bi bi-info-circle-fill fs-3 me-3"></i>
          <div>
            <strong>Verification Required:</strong> Review the requirements and description to ensure this posting
            adheres to institute placement guidelines before approving.
          </div>
        </div>
      </template>

      <template #footer>
        <button type="button" class="btn btn-outline-secondary rounded-pill px-5 "
          data-bs-dismiss="modal">Close</button>
        <button v-if="!selectedDrive.is_approved" type="button"
          class="btn btn-success rounded-pill px-5 py-2 fw-semibold shadow-lg" @click="approve(selectedDrive.id)">
          <i class="bi bi-check-lg me-1"></i> Approve Drive for Students
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { Modal } from 'bootstrap';
import { useToastNotifications } from '@/composables/useToastNotification';
import DataTable from '@/components/DataTable.vue';
import EmptyState from '@/components/EmptyState.vue';
import BaseModal from '@/components/BaseModal.vue';
import PageHeaderFilters from '@/components/PageHeaderFilters.vue';

const { addToastNotifications } = useToastNotifications();
const drives = ref([]);
const isLoading = ref(true);
const searchQuery = ref('');
const statusFilter = ref('all');

const selectedDrive = ref(null);
let detailsModal = null;

const fetchDrives = async () => {
  isLoading.value = true;
  try {
    const res = await axios.get('/api/admin/drives');
    drives.value = res.data;
  } catch (err) {
    addToastNotifications("Failed to fetch placement drives. Please try again.", "error");
    console.error("Drives Fetch Error:", err);
  } finally {
    isLoading.value = false;
  }
};

const filteredDrives = computed(() => {
  return drives.value.filter(d => {

    const matchesSearch = d.role.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      d.company.toLowerCase().includes(searchQuery.value.toLowerCase());

    let matchesStatus = true;

    if (statusFilter.value === 'pending') {
      matchesStatus = !d.is_approved && d.is_active;
    }
    else if (statusFilter.value === 'live') {
      matchesStatus = d.is_approved && d.is_active;
    }
    else if (statusFilter.value === 'closed') {
      matchesStatus = !d.is_active;
    }

    return matchesSearch && matchesStatus;
  });
});

const viewDriveDetails = (drive) => {
  selectedDrive.value = drive;
  if (!detailsModal) detailsModal = new Modal(document.getElementById('driveDetailsModal'));
  detailsModal.show();
};

const approve = async (id) => {
  try {
    const res = await axios.put(`/api/admin/drives/${id}/approve`);
    addToastNotifications(res.data.message, "success");
    if (detailsModal) detailsModal.hide();
    await fetchDrives();
  } catch (err) {
    addToastNotifications(err.response?.data?.error || "Error approving the drive.", "error");
    console.error("Approve Drive Error:", err);
  }
};

onMounted(fetchDrives);
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
.cursor-pointer .fw-semibold {
  transition: color 0.2s;
}
.cursor-pointer:hover .fw-semibold {
  color: #0a58ca !important;
  text-decoration: underline;
}
</style>
