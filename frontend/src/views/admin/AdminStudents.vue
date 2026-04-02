<template>
  <div>
    <PageHeaderFilters title="Manage Students" searchPlaceholder="Search by name or email"
      v-model:searchQuery="searchQuery" v-model:filterValue="statusFilter" showSearch="true"
      :filterOptions="[
        { label: 'All Students', value: 'all' },
        { label: 'Needs Verification', value: 'unverified' },
        { label: 'Verified', value: 'verified' },
        { label: 'Blacklisted', value: 'blacklisted' }]"
    />

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <DataTable v-else :headers="['Student', 'Degree & Stream', 'CGPA', 'Edu Status', 'Actions']">
      <tr v-for="s in filteredStudents" :key="s.id" :class="{ 'table-danger bg-opacity-10': !s.is_active }">
        <td class="py-3 px-5 cursor-pointer" @click="viewStudentDetails(s)">
          <div class="fw-bold text-primary">{{ s.name }} <i class="bi bi-info-circle ms-1 small text-muted"></i></div>
          <div class="small text-muted fw-normal">{{ s.email }}</div>
        </td>
        <td class="py-3 px-5 text-muted">{{ s.degree }} ({{ s.stream }})</td>
        <td class="py-3 px-5 fw-bold">{{ s.cgpa !== null ? s.cgpa : 'N/A' }}</td>
        <td class="py-3 px-5">
          <span v-if="!s.is_active" class="badge bg-danger rounded-pill"><i class="bi bi-slash-circle me-1"></i>
            Blacklisted</span>
          <span v-else-if="!s.verified_edu" class="badge bg-warning text-dark rounded-pill">Unverified</span>
          <span v-else class="badge bg-success rounded-pill">Verified</span>
        </td>
        <td class="py-3 text-center">
          <button v-if="!s.verified_edu && s.is_active" class="btn btn-sm btn-primary rounded-pill me-2 fw-bold"
            @click.stop="verify(s.id)" :disabled="!s.is_profile_complete"
            :title="s.is_profile_complete ? 'Verify Education' : 'Cannot verify incomplete profile'">
            Verify Edu
          </button>
          <button class="btn btn-sm rounded-pill fw-bold"
            :class="s.is_active ? 'btn-outline-danger' : 'btn-outline-success'" @click.stop="toggleBlacklist(s)">
            {{ s.is_active ? 'Blacklist' : 'Restore' }}
          </button>
        </td>
      </tr>
      <template #empty v-if="filteredStudents.length === 0">
        <EmptyState icon="bi-person" title="No students found matching your filters." />
      </template>
    </DataTable>


    <BaseModal modalId="studentDetailsModal" title="Student Details" icon="bi-person-badge"
      :selectedObject="selectedStudent">
      <template v-if="selectedStudent">
        <div class="d-flex align-items-center mb-4">
          <div class="bg-primary text-white rounded-circle d-flex justify-content-center align-items-center me-3 fs-3"
            style="width: 60px; height: 60px;">
            {{ selectedStudent.name.charAt(0) }}
          </div>
          <div>
            <h4 class="fw-bold mb-0">{{ selectedStudent.name }}</h4>
            <div class="text-muted">{{ selectedStudent.email }}</div>
          </div>
        </div>

        <div class="row g-4 mb-4 bg-light p-3 rounded-3">
          <div class="col-6">
            <label class="text-muted small fw-semibold text-uppercase">Degree</label>
            <div class="fw-semibold">{{ selectedStudent.degree }}</div>
          </div>
          <div class="col-6">
            <label class="text-muted small fw-semibold text-uppercase">Stream</label>
            <div class="fw-semibold">{{ selectedStudent.stream }}</div>
          </div>
          <div class="col-6">
            <label class="text-muted small fw-semibold text-uppercase">CGPA</label>
            <div class="fw-bold text-primary">{{ selectedStudent.cgpa !== null ? selectedStudent.cgpa : 'Missing' }}
            </div>
          </div>
          <div class="col-6">
            <label class="text-muted small fw-semibold text-uppercase">Profile Status</label>
            <div>
              <span v-if="selectedStudent.is_profile_complete" class="text-success fw-bold"><i
                  class="bi bi-check-circle-fill"></i> Complete</span>
              <span v-else class="text-danger fw-bold"><i class="bi bi-x-circle-fill"></i> Incomplete</span>
            </div>
          </div>
        </div>

        <div v-if="!selectedStudent.is_profile_complete" class="alert alert-danger py-2 small">
          <i class="bi bi-exclamation-triangle-fill me-1"></i> You cannot verify this student until they completely fill
          out their profile, age, dates, and resume link.
        </div>
      </template>

      <template #footer>
        <button type="button" class="btn btn-light rounded-pill px-4 " data-bs-dismiss="modal">Close</button>
        <button v-if="!selectedStudent.verified_edu && selectedStudent.is_profile_complete && selectedStudent.is_active"
          type="button" class="btn btn-primary rounded-pill px-4 fw-semibold" @click="verify(selectedStudent.id)">
          Verify Education Now
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
import DataTable from '@/components/DataTable.vue';
import EmptyState from '@/components/EmptyState.vue';
import BaseModal from '@/components/BaseModal.vue';
import PageHeaderFilters from '@/components/PageHeaderFilters.vue';
import { useFetchData } from '@/composables/useFetchData';

const { addToastNotifications } = useToastNotifications();
const { data: students, isLoading, fetchData: fetchStudents } = useFetchData('/api/admin/students','Failed to load the student directory.');

const searchQuery = ref('');
const statusFilter = ref('all');

const selectedStudent = ref(null);
let detailsModal = null;

const filteredStudents = computed(() => {
  return students.value.filter(s => {
    // Search Filter
    const matchesSearch = s.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      s.email.toLowerCase().includes(searchQuery.value.toLowerCase());
    // Status Filter
    let matchesStatus = true;
    if (statusFilter.value === 'unverified') matchesStatus = !s.verified_edu && s.is_active;
    if (statusFilter.value === 'verified') matchesStatus = s.verified_edu && s.is_active;
    if (statusFilter.value === 'blacklisted') matchesStatus = !s.is_active;

    return matchesSearch && matchesStatus;
  });
});

const viewStudentDetails = (student) => {
  selectedStudent.value = student;
  if (!detailsModal) {
    detailsModal = new Modal(document.getElementById('studentDetailsModal'));
  }
  detailsModal.show();
};

const verify = async (id) => {
  try {
    await axios.put(`/api/admin/students/${id}/verify`);
    addToastNotifications("Education Verified Successfully!", "success");
    if (detailsModal) detailsModal.hide();
    fetchStudents();
  } catch (err) {
    addToastNotifications(err.response?.data?.error || "Error verifying student", "error");
  }
};

const toggleBlacklist = async (s) => {
  try {
    const res = await axios.put(`/api/admin/users/${s.user_id}/blacklist`);
    addToastNotifications(res.data.message, "success");
    fetchStudents();
  } catch (err) {
    console.log(err)
    addToastNotifications("Error updating user status", "error");
  }
};
</script>

<style scoped>
.cursor-pointer { cursor: pointer; }

.cursor-pointer .text-primary { transition: color 0.2s; }

.cursor-pointer:hover .text-primary {
  color: #0c54c0 !important;
  text-decoration: underline;
}
</style>
