<template>
  <div>
    <PageHeaderFilters title="Manage Companies" searchPlaceholder="Search Company..."
      v-model:searchQuery="searchQuery" v-model:filterValue="statusFilter" showSearch="true"
      :filterOptions="[
        { label: 'All Statuses', value: 'all' },
        { label: 'Pending Approval', value: 'pending' },
        { label: 'Approved', value: 'approved' },
        { label: 'Blacklisted', value: 'blacklisted' }]"
    />

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <DataTable v-else :headers="['Company Name','Industry','Profile Info','Status','Actions']">
      <tr v-for="c in filteredCompanies" :key="c.id" :class="{'table-danger bg-opacity-10': !c.is_active}">
        <td class="py-3 px-5 fw-bold text-primary cursor-pointer" @click="viewCompanyDetails(c)">
          {{ c.name }} <i class="bi bi-info-circle ms-1 small text-muted"></i>
        </td>
        <td class="py-3 px-5 text-muted">{{ c.industry || 'N/A' }}</td>
        <td class="py-3 px-5">
          <span v-if="c.is_profile_complete" class="text-success small fw-bold"><i class="bi bi-check-circle-fill"></i> Complete</span>
          <span v-else class="text-danger small fw-bold"><i class="bi bi-x-circle-fill"></i> Missing Info</span>
        </td>
        <td class="py-3 px-5">
            <span v-if="!c.is_active" class="badge bg-danger rounded-pill"><i class="bi bi-slash-circle me-1"></i> Blacklisted</span>
            <span v-else-if="!c.is_approved" class="badge bg-warning text-dark rounded-pill">Pending Approval</span>
            <span v-else class="badge bg-success rounded-pill">Approved</span>
        </td>
        <td class="py-3 text-center">
          <button v-if="!c.is_approved && c.is_active" class="btn btn-sm btn-success rounded-pill me-2 fw-bold" @click.stop="approve(c.id)" :disabled="!c.is_profile_complete" :title="c.is_profile_complete ? 'Approve Company' : 'Cannot approve incomplete profile'">
            Approve
          </button>
          <button class="btn btn-sm rounded-pill fw-bold" :class="c.is_active ? 'btn-outline-danger' : 'btn-outline-success'" @click.stop="toggleBlacklist(c)">
            {{ c.is_active ? 'Blacklist' : 'Restore' }}
          </button>
        </td>
      </tr>
      <template #empty v-if="filteredCompanies.length === 0">
        <EmptyState icon="bi-building" title="No companies found."></EmptyState>
      </template>
    </DataTable>

    <BaseModal modalId="companyDetailsModal" title="Company Details" icon="bi-building" :selectedObject="selectedCompany" size="modal-lg">
      <template v-if="selectedCompany">
        <h4 class="fw-bold mb-1">{{ selectedCompany.name }}</h4>
        <p class="text-muted mb-4">{{ selectedCompany.industry || 'Industry not specified' }}</p>
        <div class="d-flex flex-lg-row flex-column gap-lg-5 gap-3 py-3 px-2">
          <div class="mb-4">
            <label class="text-muted small fw-semibold text-uppercase">HR Contact Email</label>
            <div class="fw-semibold">{{ selectedCompany.hr_contact || 'N/A' }}</div>
          </div>

          <div class="mb-4">
            <label class="text-muted small fw-semibold text-uppercase">Official Website</label>
            <div v-if="selectedCompany.website"><a :href="selectedCompany.website" target="_blank" class="text-decoration-none">{{ selectedCompany.website }}</a></div>
            <div v-else class="text-danger">Not Provided</div>
          </div>
        </div>

        <div class="mb-2">
          <label class="text-muted small fw-bold text-uppercase">Company Description</label>
          <p class="bg-light p-3 rounded-3 mt-1" style="white-space: pre-wrap;">{{ selectedCompany.description || 'No description provided.' }}</p>
        </div>
      </template>

      <template #footer>
        <button type="button" class="btn btn-light rounded-pill px-4" data-bs-dismiss="modal">Close</button>
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
import EmptyState from '@/components/EmptyState.vue';
import PageHeaderFilters from '@/components/PageHeaderFilters.vue';
import { useFetchData } from '@/composables/useFetchData';

const { addToastNotifications } = useToastNotifications();
const { data: companies, isLoading, fetchData: fetchCompanies } = useFetchData('/api/admin/companies','Failed to load the company directory.');

const searchQuery = ref('');
const statusFilter = ref('all');

const selectedCompany = ref(null);
let detailsModal = null;

const filteredCompanies = computed(() => {
  return companies.value.filter(c => {
    // Search Filter
    const matchesSearch = c.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                          (c.industry && c.industry.toLowerCase().includes(searchQuery.value.toLowerCase()));
    // Status Filter
    let matchesStatus = true;
    if (statusFilter.value === 'pending') matchesStatus = !c.is_approved && c.is_active;
    if (statusFilter.value === 'approved') matchesStatus = c.is_approved && c.is_active;
    if (statusFilter.value === 'blacklisted') matchesStatus = !c.is_active;

    return matchesSearch && matchesStatus;
  });
});

const viewCompanyDetails = (company) => {
  selectedCompany.value = company;
  if (!detailsModal) {
    detailsModal = new Modal(document.getElementById('companyDetailsModal'));
  }
  detailsModal.show();
};

const approve = async (id) => {
  try {
    await axios.put(`/api/admin/companies/${id}/approve`);
    addToastNotifications("Company Approved Successfully!", "success");
    fetchCompanies();
  } catch (err) {
    addToastNotifications(err.response?.data?.error || "Error approving company", "error");
  }
};

const toggleBlacklist = async (c) => {
  try {
    const res = await axios.put(`/api/admin/users/${c.user_id}/blacklist`);
    addToastNotifications(res.data.message, "success");
    fetchCompanies();
  } catch (err) {
    console.log(err)
    addToastNotifications("Error updating user status", "error");
  }
};
</script>

<style scoped>
.cursor-pointer { cursor: pointer; transition: color 0.2s; }
.cursor-pointer:hover { color: #0a58ca !important; text-decoration: underline; }
</style>
