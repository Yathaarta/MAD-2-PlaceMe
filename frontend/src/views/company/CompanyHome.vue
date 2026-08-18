<template>
  <div class="pb-5">

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-else-if="dashboardData" class="container-fluid px-0">
      <h2 class="fw-bold text-dark mb-4">Company Overview</h2>

      <!-- Account Status Alert -->
      <div v-if="!dashboardData.company.is_approved" class="alert alert-warning border-0 shadow-sm rounded-4 p-4 d-flex align-items-center mb-4">
        <i class="bi bi-hourglass-split fs-2 me-3 text-warning"></i>
        <div>
          <h5 class="fw-bold mb-1 text-dark">Account Pending Verification</h5>
          <p class="mb-0 text-muted small">You can create placement drives, but they will not be visible to students until the Institute Admin verifies your company profile.</p>
        </div>
      </div>
      <div v-else>
        <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-4">
          <div class="p-4 p-md-5 text-white position-relative"
            style="background: linear-gradient(to right, #2b32b2, #0f70a7);">
            <div class="row align-items-center position-relative z-1">
              <div class="col-md-8">
                <span class="badge bg-white text-primary fw-bold mb-3 shadow-sm px-3 py-2 rounded-pill">
                  {{ dashboardData.company.industry || 'Industry Pending' }}
                </span>
                <h2 class="fw-bold mb-2">Welcome back, {{ dashboardData.company.name }}!</h2>
                <p class="text-white-50 fs-5 mb-0">Manage your recruitment drives and discover top campus talent.</p>
              </div>
              <!-- Quick Action Buttons -->
              <div class="col-md-4 text-md-end mt-4 mt-md-0">
                <router-link to="/company-dashboard/drives"
                  class="btn btn-light text-primary rounded-pill px-4 py-2 fw-bold shadow-sm me-2 mb-2">
                  <i class="bi bi-plus-lg me-2"></i> Post New Drive
                </router-link>
                <router-link to="/company-dashboard/applicants"
                  class="btn btn-outline-light rounded-pill px-4 py-2 fw-bold mb-2">
                  <i class="bi bi-people-fill me-2"></i> View Candidates
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Row -->
      <div class="row g-4 mb-5">
        <div class="col-lg-4">
          <div class="card bg-white border-0 shadow-sm rounded-4 h-100 p-4 d-flex flex-row align-items-center">
            <div class="bg-primary bg-opacity-10 text-primary rounded-circle d-flex justify-content-center align-items-center me-4" style="width: 60px; height: 60px;">
              <i class="bi bi-briefcase-fill fs-3"></i>
            </div>
            <div>
              <h2 class="fw-bold text-dark mb-0">{{ dashboardData.stats.total_drives }}</h2>
              <span class="text-muted small fw-bold text-uppercase">Total Drives Posted</span>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card bg-white border-0 shadow-sm rounded-4 h-100 p-4 d-flex flex-row align-items-center">
            <div class="bg-success bg-opacity-10 text-success rounded-circle d-flex justify-content-center align-items-center me-4" style="width: 60px; height: 60px;">
              <i class="bi bi-broadcast fs-3"></i>
            </div>
            <div>
              <h2 class="fw-bold text-dark mb-0">{{ dashboardData.stats.active_drives }}</h2>
              <span class="text-muted small fw-bold text-uppercase">Active / Open Drives</span>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card bg-white border-0 shadow-sm rounded-4 h-100 p-4 d-flex flex-row align-items-center">
            <div class="bg-info bg-opacity-10 text-info rounded-circle d-flex justify-content-center align-items-center me-4" style="width: 60px; height: 60px;">
              <i class="bi bi-person-lines-fill fs-3"></i>
            </div>
            <div>
              <h2 class="fw-bold text-dark mb-0">{{ dashboardData.stats.total_applicants }}</h2>
              <span class="text-muted small fw-bold text-uppercase">Total Applications</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Drives Overview -->
      <div class="card bg-white border-0 shadow-sm rounded-4">
        <div class="card-header bg-white border-0 p-4 d-flex justify-content-between align-items-center">
          <h5 class="fw-bold text-dark mb-0"><i class="bi bi-clock-history me-2 text-primary"></i> Recently Posted Drives</h5>
          <router-link to="/company-dashboard/drives" class="btn btn-sm btn-outline-primary rounded-pill px-3 fw-bold">View All</router-link>
        </div>

        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th class="py-3 px-4 text-uppercase small fw-bold">Job Role</th>
                <th class="py-3 text-uppercase small fw-bold">Deadline</th>
                <th class="py-3 text-uppercase small fw-bold">Applicants</th>
                <th class="py-3 text-uppercase small fw-bold">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="drive in dashboardData.recent_drives" :key="drive.id">
                <td class="px-4 py-3 fw-bold text-dark">{{ drive.role }}</td>
                <td class="py-3 text-danger fw-semibold"><i class="bi bi-calendar-x me-1"></i> {{ drive.deadline }}</td>
                <td class="py-3 fw-bold text-primary">{{ drive.applicants }}</td>
                <td class="py-3">
                  <span v-if="!drive.is_active" class="badge bg-danger text-light rounded-pill">{{ getClosedStatus(drive) }}</span>
                  <span v-else-if="!drive.is_approved" class="badge bg-warning text-dark rounded-pill">Pending</span>
                  <span v-else class="badge bg-success rounded-pill">Approved</span>
                </td>
              </tr>
              <tr v-if="dashboardData.recent_drives.length === 0">
                <td colspan="4" class="text-center py-5 text-muted">
                  <i class="bi bi-inbox fs-2 mb-2 d-block"></i> No drives posted yet.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>

import { useFetchData } from '@/composables/useFetchData';
const { data:dashboardData, isLoading } = useFetchData('/api/dashboard/company','Failed to load Company dashboard data.', true);
import { useGetDriveStatus } from '@/composables/useGetDriveStatus';

const { getClosedStatus } = useGetDriveStatus()
</script>
