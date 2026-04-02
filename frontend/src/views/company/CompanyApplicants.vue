<template>
  <div>
    <PageHeaderFilters title="Applicant Tracking System">
      <template #actions>
        <button class="btn btn-outline-success rounded-pill fw-semibold shadow-sm px-4" @click="exportCSV" :disabled="isExporting || applicants.length === 0">
          <span v-if="isExporting" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-file-earmark-spreadsheet-fill me-2"></i> Export as CSV
        </button>
      </template>
    </PageHeaderFilters>

    <!-- ATS filters & sorting -->
    <div class="card bg-white border-0 shadow-sm rounded-4 p-4 mb-4">
      <div class="row g-3">
        <!-- search -->
        <div class="col-12 col-lg-3">
          <label class="form-label small text-muted fw-bold text-uppercase mb-2">Search Candidate</label>
          <div class="input-group">
            <span class="input-group-text bg-light border-0"><i class="bi bi-search"></i></span>
            <input type="text" class="form-control bg-light border-0 py-2" placeholder="Name or Email..." v-model="searchQuery">
          </div>
        </div>
        <!-- Role filter -->
        <div class="col-12 col-lg-3">
          <label class="form-label small text-muted fw-bold text-uppercase mb-2">Filter by Job Role</label>
          <select class="form-select bg-light border-0 py-2 fw-semibold" v-model="roleFilter">
            <option value="all">All Roles</option>
            <option v-for="role in uniqueRoles" :key="role" :value="role">{{ role }}</option>
          </select>
        </div>
        <!-- Status filter -->
        <div class="col-12 col-lg-3">
          <label class="form-label small text-muted fw-bold text-uppercase mb-2">Application Status</label>
          <select class="form-select bg-light border-0 py-2 fw-semibold" v-model="statusFilter">
            <option value="all">All Statuses</option>
            <option value="Applied">Applied</option>
            <option value="Shortlisted">Shortlisted</option>
            <option value="Interview">Interview</option>
            <option value="Selected">Selected</option>
            <option value="Rejected">Rejected</option>
          </select>
        </div>
        <!-- sorting -->
        <div class="col-12 col-lg-3">
          <label class="form-label small text-muted fw-bold text-uppercase mb-2">Sort By</label>
          <select class="form-select bg-light border-0 py-2 fw-semibold" v-model="sortOption">
            <option value="newest">Newest Applicants First</option>
            <option value="cgpa_desc">Highest CGPA First</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <DataTable v-else :headers="['Candidate Profile','Role Applied','Degree & Stream','CGPA','ATS Status','Resume']">
      <tr v-for="app in filteredAndSortedApplicants" :key="app.id" :class="{'table-danger bg-opacity-10': app.is_blacklisted}">
        <td class="py-3 px-5">
          <div class="fw-bold text-primary cursor-pointer d-flex align-items-center" @click="viewCandidateDetails(app)">
            {{ app.student_name }}
            <i class="bi bi-info-circle ms-2 small text-muted"></i>
            <span v-if="app.is_blacklisted" class="badge bg-danger ms-2" style="font-size: 0.65rem;"><i class="bi bi-slash-circle me-1"></i>Suspended</span>
          </div>
          <div class="small text-muted mt-1">{{ app.student_email }}</div>
        </td>

        <td class="py-3 px-5 fw-semibold text-dark">{{ app.drive_role }}</td>

        <td class="py-3 px-5">
          <span class="badge bg-secondary bg-opacity-10 text-dark border border-secondary border-opacity-25">{{ app.degree }}</span>
          <div class="small text-muted mt-2 fw-semibold">{{ app.stream }}</div>
        </td>

        <td class="py-3 px-5 fw-bold fs-5" :class="app.cgpa !== 'N/A' && parseFloat(app.cgpa) >= 8.0 ? 'text-success' : 'text-dark'">
          {{ app.cgpa !== 'N/A' ? app.cgpa : 'N/A' }}
        </td>

        <td class="py-py-3 px-5">
          <select class="form-select form-select-sm fw-bold d-inline-block w-auto rounded-pill shadow-sm border-0 bg-light ps-3 py-2"
                  :class="{
                    'text-primary': app.status === 'Applied',
                    'text-info': app.status === 'Shortlisted',
                    'text-warning ': app.status === 'Interview',
                    'text-success': app.status === 'Selected',
                    'text-danger': app.status === 'Rejected'
                  }"
                  v-model="app.status"
                  @change="updateStatus(app.id, app.status)"
                  :disabled="app.is_blacklisted">
            <option value="Applied" class="text-dark">Applied</option>
            <option value="Shortlisted" class="text-dark">Shortlisted</option>
            <option value="Interview" class="text-dark">Interview</option>
            <option value="Selected" class="text-dark">Selected</option>
            <option value="Rejected" class="text-dark">Rejected</option>
          </select>
        </td>

        <td class="py-3 px-5 text-center">
          <a :href="app.resume_url" target="_blank" class="btn btn-sm btn-outline-danger rounded-pill shadow-sm fw-bold px-3" :class="{'disabled': app.is_blacklisted}">
            <i class="bi bi-file-pdf-fill me-1"></i> View
          </a>
        </td>
      </tr>
    </DataTable>

    <BaseModal modalId="candidateDetailsModal" title="Candidate Dossier" icon="bi-briefcase-fill"
      :selectedObject="selectedApplicant" size="modal-lg">
      <template v-if="selectedApplicant">
        <div v-if="selectedApplicant.is_blacklisted" class="alert alert-danger py-3 mb-4 d-flex align-items-center rounded-3 shadow-sm border-0">
            <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
            <div>
              <strong>Action Required:</strong> This candidate's account has been suspended by the Institute Administration. You cannot update their recruitment status or proceed with hiring.
            </div>
        </div>

        <!-- Header Info -->
        <div class="d-flex align-items-center mb-4 pb-4 border-bottom">
          <div class="bg-primary text-white rounded-circle d-flex justify-content-center align-items-center me-4 fs-1 shadow-sm" style="width: 70px; height: 70px;">
              {{ selectedApplicant.student_name.charAt(0) }}
          </div>
          <div>
              <h2 class="fw-bold mb-1 fs-3 text-dark">{{ selectedApplicant.student_name }}</h2>
              <div class="text-muted fs-6 mb-2"><i class="bi bi-envelope-fill me-2"></i>{{ selectedApplicant.student_email }}</div>
              <span class="badge bg-light fw-medium text-primary border border-primary px-2 py-2 shadow-sm">
                <i class="bi bi-calendar-check me-1"></i> Applied for {{ selectedApplicant.drive_role }} on {{ selectedApplicant.applied_on }}
            </span>
          </div>
        </div>

        <!-- Academic Breakdown -->
        <h5 class="fw-bold text-dark mb-5"><i class="bi bi-mortarboard-fill me-2 text-primary"></i> Academic Profile</h5>

        <div class="row g-4 bg-light p-3 pb-5 rounded-4 mx-0 shadow-sm border ">
          <div class="col-lg-6">
            <label class="text-muted small fw-semibold text-uppercase mb-1">Candidate Age</label>
            <div class="fw-bold text-dark fs-5">{{ selectedApplicant.age ? selectedApplicant.age + ' Years' : 'Not Provided' }}</div>
          </div>
          <div class="col-lg-6">
            <label class="text-muted small fw-semibold text-uppercase mb-1">Current CGPA</label>
            <div class="fw-bold fs-4" :class="selectedApplicant.cgpa !== 'N/A' && parseFloat(selectedApplicant.cgpa) >= 8.0 ? 'text-success' : 'text-primary'">
              {{ selectedApplicant.cgpa !== 'N/A' ? selectedApplicant.cgpa : 'Not Provided' }}
            </div>
          </div>

          <div class="col-lg-6">
            <label class="text-muted small fw-semibold text-uppercase mb-1">Degree Program</label>
            <div class="fw-bold text-dark fs-6">{{ selectedApplicant.degree }}</div>
          </div>
          <div class="col-lg-6">
            <label class="text-muted small fw-semibold text-uppercase mb-1">Stream Specialization</label>
            <div class="fw-bold text-dark fs-6">{{ selectedApplicant.stream }}</div>
          </div>

          <div class="col-lg-6">
            <label class="text-muted small fw-semibold text-uppercase mb-1">Enrollment Date</label>
            <div class="fw-semibold text-dark"><i class="bi bi-calendar-event me-2"></i>{{ selectedApplicant.start_year }}</div>
          </div>
          <div class="col-lg-6">
            <label class="text-muted small fw-semibold text-uppercase mb-1">Expected Graduation</label>
            <div class="fw-semibold text-dark"><i class="bi bi-mortarboard me-2"></i>{{ selectedApplicant.end_year }}</div>
          </div>
        </div>
      </template>

      <template #footer>
        <div>
            <a :href="selectedApplicant.resume_url" target="_blank" class="btn btn-danger py-2 fs-6 fw-semibold rounded-pill shadow-lg" :class="{'disabled': selectedApplicant.is_blacklisted}">
              <i class="bi bi-file-earmark-pdf-fill me-2"></i> Open Resume Document
            </a>
        </div>
        <button type="button" class="btn btn-outline-secondary rounded-pill px-5"
          data-bs-dismiss="modal">Close</button>
      </template>
    </BaseModal>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';
import { Modal } from 'bootstrap';
import { useToastNotifications } from '@/composables/useToastNotification';
import BaseModal from '@/components/BaseModal.vue';
import DataTable from '@/components/DataTable.vue';
import PageHeaderFilters from '@/components/PageHeaderFilters.vue';
import { useExportCsv } from '@/composables/useExportCsv';
import { useFetchData } from '@/composables/useFetchData';

const { addToastNotifications } = useToastNotifications();
const { isExporting, exportCSV } = useExportCsv('/api/company/export-applicants')
const { data: applicants, isLoading, fetchData: fetchApplicants } = useFetchData('/api/company/applications','Failed to load applicant data.');

// filters state
const searchQuery = ref('');
const statusFilter = ref('all');
const roleFilter = ref('all');
const sortOption = ref('newest');

// Modal State
const selectedApplicant = ref(null);
let detailsModal = null;

// Unique roles for filter
const uniqueRoles = computed(() => {
  const roles = applicants.value.map(app => app.drive_role);
  return [...new Set(roles)];
});

// Computed filtering & sorting
const filteredAndSortedApplicants = computed(() => {
  let result = applicants.value;

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(app =>
      app.student_name.toLowerCase().includes(q) ||
      app.student_email.toLowerCase().includes(q)
    );
  }

  if (roleFilter.value !== 'all') {
    result = result.filter(app => app.drive_role === roleFilter.value);
  }

  if (statusFilter.value !== 'all') {
    result = result.filter(app => app.status === statusFilter.value);
  }

  result = [...result];
  if (sortOption.value === 'cgpa_desc') {
    result.sort((a, b) => {
      const cgpaA = a.cgpa === 'N/A' ? 0 : parseFloat(a.cgpa);
      const cgpaB = b.cgpa === 'N/A' ? 0 : parseFloat(b.cgpa);
      return cgpaB - cgpaA;
    });
  } else if (sortOption.value === 'newest') {
    result.sort((a, b) => b.id - a.id);
  }

  return result;
});

const viewCandidateDetails = (applicant) => {
  selectedApplicant.value = applicant;
  if (!detailsModal) {
    detailsModal = new Modal(document.getElementById('candidateDetailsModal'));
  }
  detailsModal.show();
};

const updateStatus = async (appId, newStatus) => {
  try {
    const res = await axios.put(`/api/company/applications/${appId}`, { status: newStatus });
    addToastNotifications(res.data.message, "success");
  } catch (err) {
    const errMsg = err.response?.data?.error || "Failed to update candidate status.";
    addToastNotifications(errMsg, "error");
    console.error("Status Update Error:", err);
    await fetchApplicants();
  }
};
</script>

<style scoped>
.cursor-pointer { cursor: pointer; transition: color 0.2s; }
.cursor-pointer:hover { color: #0a58ca !important; text-decoration: underline; }
</style>
