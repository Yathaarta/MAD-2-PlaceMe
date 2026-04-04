<template>
  <div>
    <PageHeaderFilters title="My Applications">
      <template #actions>
        <button class="btn btn-outline-success rounded-pill fw-semibold shadow-sm px-4" @click="exportCSV" :disabled="isExporting || applications.length === 0">
          <span v-if="isExporting" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-file-earmark-spreadsheet-fill me-2"></i> Export as CSV
        </button>
      </template>
    </PageHeaderFilters>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <DataTable v-else :headers="['Company','Job Role','Date Applied','Current Status']">
        <tr v-for="app in applications.application" :key="app.id">
          <td class="px-5 py-3 cursor-pointer" @click="viewDriveDetails(app, 'CompanyDetailsModal', CompanydetailsModal)">
            <span class="fw-bold text-dark">{{ app.company }}</span>
            <i class="bi bi-info-circle ms-2 small text-muted"></i>
          </td>
          <td class="px-5 py-3 cursor-pointer" @click="viewDriveDetails(app, 'JobDetailsModal', JobdetailsModal)">
            <span class="fw-semibold text-muted">{{ app.role }}</span>
            <i class="bi bi-info-circle ms-2 small text-muted"></i>
          </td>
          <td class="px-5 py-3 text-muted"><i class="bi bi-calendar-event me-1"></i> {{ app.applied_on || 'Recent' }}</td>
          <td class="py-3 text-center">
            <span class="badge rounded-pill px-3 py-2 fw-bold"
                  :class="{
                    'bg-primary bg-opacity-10 text-primary border border-primary': app.status === 'Applied',
                    'bg-info bg-opacity-10 text-info border border-info': app.status === 'Shortlisted',
                    'bg-warning bg-opacity-10 text-warning border border-warning': app.status === 'Interview',
                    'bg-success text-white shadow-sm': app.status === 'Selected',
                    'bg-danger text-white shadow-sm': app.status === 'Rejected'
                  }">
              {{ app.status }}
            </span>
          </td>
        </tr>

        <template #empty v-if="applications.application.length === 0">
          <EmptyState title="You haven't applied to any drives yet." icon="bi-file-earmark-x">
            <router-link to="/student-dashboard/drives" class="btn btn-primary rounded-pill mt-3 px-4 fw-semibold shadow-sm">
              View Available Drives
           </router-link>
          </EmptyState>
        </template>
    </DataTable>

    <BaseModal modalId="JobDetailsModal" title="Job Role Details" icon="bi-briefcase-fill"
      :selectedObject="selectedJob" size="modal-lg">
      <template v-if="selectedJob">

        <div class="d-flex justify-content-between align-items-start mb-4 pb-3 border-bottom">
          <div>
            <h2 class="fw-bold mb-1 fs-4 text-dark">{{ selectedJob.role }}</h2>
            <div class="fs-6 text-primary fw-semibold"><i class="bi bi-building me-2"></i>{{ selectedJob.company }}
            </div>
          </div>
          <span class="badge bg-light border text-dark fw-semibold shadow-sm">
            <i class="bi bi-calendar-x me-2 text-danger"></i>
            Original Deadline: {{ selectedJob.drive_details.deadline }}</span>
        </div>
        <!-- Job Description -->
        <div>
          <label class="text-muted small fw-bold mb-2 text-uppercase">Job Description & Details</label>

          <p class="bg-light p-3 rounded-3 mt-1" style="white-space: pre-wrap;">
            {{ selectedJob.drive_details.description || 'The company did not provide a detailed description.' }}
          </p>
        </div>
      </template>
      <template #footer>
        <button type="button" class="btn btn-outline-secondary rounded-pill px-5" data-bs-dismiss="modal">Close</button>
      </template>
    </BaseModal>

    <BaseModal modalId="CompanyDetailsModal" title="Company Details" icon="bi-building" :selectedObject="selectedJob" size="modal-lg">
      <template v-if="selectedJob">
        <h4 class="fw-bold mb-1">{{ selectedJob.company_details.name }}</h4>
        <p class="text-muted mb-4">{{ selectedJob.company_details.industry || 'Industry not specified' }}</p>
        <div class="d-flex flex-lg-row flex-column gap-lg-5 gap-3 py-3 px-2">
          <div class="mb-4">
            <label class="text-muted small fw-semibold text-uppercase">HR Contact Email</label>
            <div class="fw-semibold">{{ selectedJob.company_details.hr_contact || 'N/A' }}</div>
          </div>

          <div class="mb-4">
            <label class="text-muted small fw-semibold text-uppercase">Official Website</label>
            <div v-if="selectedJob.company_details.website"><a :href="selectedJob.company_details.website" target="_blank" class="text-decoration-none">{{ selectedJob.company_details.website }}</a></div>
            <div v-else class="text-danger">Not Provided</div>
          </div>
        </div>

        <div class="mb-2">
          <label class="text-muted small fw-bold mb-2 text-uppercase">Company Description</label>
          <p class="bg-light p-3 rounded-3 mt-1" style="white-space: pre-wrap;">{{ selectedJob.company_details.description || 'No description provided.' }}</p>
        </div>
      </template>

      <template #footer>
        <button type="button" class="btn btn-outline-secondary rounded-pill px-5" data-bs-dismiss="modal">Close</button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Modal } from 'bootstrap';
import DataTable from '@/components/DataTable.vue';
import EmptyState from '@/components/EmptyState.vue';
import PageHeaderFilters from '@/components/PageHeaderFilters.vue';
import { useExportCsv } from '@/composables/useExportCsv';
import { useFetchData } from '@/composables/useFetchData';
import BaseModal from '@/components/BaseModal.vue';

const { isExporting, exportCSV } = useExportCsv('/api/student/export-applications')
const { data: applications, isLoading } = useFetchData('/api/student/applications','Failed to load your applications.');
const selectedJob = ref(null);
let JobdetailsModal = null;
let CompanydetailsModal = null;

const viewDriveDetails = (drive, modalID, modal) => {
  selectedJob.value = drive;
  if (!modal) modal = new Modal(document.getElementById(modalID));
  modal.show();
};
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
.cursor-pointer > :is(.fw-semibold,.fw-bold) {
  transition: color 0.2s;
}
.cursor-pointer:hover > :is(.fw-semibold,.fw-bold) {
  color: #0a58ca !important;
  text-decoration: underline;
}
</style>
