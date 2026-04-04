<template>
  <div v-if="isLoading" class="d-flex justify-content-center align-items-center" style="height: 60vh;">
    <div class="spinner-border text-success" role="status" style="width: 3rem; height: 3rem;"></div>
  </div>

  <div v-else-if="dashboardData" class="container-fluid px-0">
    <h2 class="fw-bold text-dark mb-4">Student Overview</h2>

    <!-- Stats Row -->
      <div class="row g-4 mb-5">
        <div class="col-lg-4">
          <div class="card bg-white border-0 shadow-sm rounded-4 h-100 p-4 d-flex flex-row align-items-center">
            <div class="bg-primary bg-opacity-10 text-primary rounded-circle d-flex justify-content-center align-items-center me-4" style="width: 60px; height: 60px;">
              <i class="bi bi-send-fill fs-3"></i>
            </div>
            <div>
              <h2 class="fw-bold text-dark mb-0">{{  dashboardData.stats.active_applications  }}</h2>
              <span class="text-muted small fw-bold text-uppercase">Total Drives Posted</span>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card bg-white border-0 shadow-sm rounded-4 h-100 p-4 d-flex flex-row align-items-center">
            <div class="bg-success bg-opacity-10 text-success rounded-circle d-flex justify-content-center align-items-center me-4" style="width: 60px; height: 60px;">
              <i class="bi bi-calendar-event-fill fs-3"></i>
            </div>
            <div>
              <h2 class="fw-bold text-dark mb-0">{{ dashboardData.stats.upcoming_interviews }}</h2>
              <span class="text-muted small fw-bold text-uppercase">Active / Open Drives</span>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card bg-white border-0 shadow-sm rounded-4 h-100 p-3 d-flex flex-row align-items-center">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-end mb-2">
              <h6 class="text-muted fw-bold mb-0 text-uppercase small">Profile Strength</h6>
              <span class="fw-bold text-success fs-5">{{ dashboardData.stats.profile_completion }}%</span>
            </div>
            <div class="progress mt-3 rounded-pill" style="height: 10px;">
              <div class="progress-bar bg-success" :style="`width: ${dashboardData.stats.profile_completion}%`"></div>
            </div>
          </div>
          </div>
        </div>
      </div>

    <!-- Content Row -->
    <div class="row g-4">
      <div class="col-12 col-xl-7">
        <div class="card bg-white border-0 shadow-sm rounded-4 h-100">
          <div class="card-header bg-white border-0 pt-4 px-4 pb-0 d-flex justify-content-between align-items-center">
            <h5 class="fw-bold mb-0">Recommended Drives</h5>
            <router-link to="/student-dashboard/drives" class="btn btn-sm btn-light rounded-pill px-3 fw-bold">View All</router-link>
          </div>
          <div class="card-body p-4">
            <div v-if="dashboardData.ongoing_drives.length === 0" class="text-center text-muted py-4">
              <i class="bi bi-emoji-frown fs-1 d-block mb-2"></i> No active drives available right now.
            </div>
            <div v-else class="list-group list-group-flush gap-2">
              <div v-for="drive in dashboardData.ongoing_drives.slice(0, 3)" :key="drive.id" class="list-group-item bg-light border-0 rounded-3 p-3 d-flex flex-column flex-sm-row justify-content-between align-items-sm-center">
                <div class="mb-3 mb-sm-0">
                  <h6 class="fw-bold mb-1">{{ drive.role }}</h6>
                  <p class="text-muted mb-0 small"><i class="bi bi-building me-1"></i> {{ drive.company }}</p>
                </div>
                <div class="text-sm-end">
                  <span class="d-inline-block bg-white text-danger border border-danger rounded px-2 py-1 small fw-bold mb-2 mb-sm-0 me-sm-3">
                    <i class="bi bi-clock"></i> Ends {{ drive.deadline }}
                  </span>
                  <router-link to="/student-dashboard/drives" class="btn btn-sm btn-success rounded-pill px-4 fw-bold shadow-sm">View Details</router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-xl-5">
        <div class="card bg-white border-0 shadow-sm rounded-4 h-100">
          <div class="card-header bg-white border-0 pt-4 px-4 pb-0 d-flex justify-content-between align-items-center">
            <h5 class="fw-bold mb-0">Recent Applications</h5>
            <router-link to="/student-dashboard/applications" class="btn btn-sm btn-light rounded-pill px-3 fw-bold">Track</router-link>
          </div>
          <div class="card-body p-4">
            <div v-if="dashboardData.recent_applications.length === 0" class="text-center text-muted py-4">
              <i class="bi bi-folder-x fs-1 d-block mb-2"></i> You haven't applied anywhere yet.
            </div>
            <ul v-else class="list-unstyled mb-0">
              <li v-for="app in dashboardData.recent_applications.slice(0, 3)" :key="app.id" class="mb-3 p-3 border rounded-3 position-relative overflow-hidden">
                <div class="position-absolute top-0 start-0 h-100" style="width: 4px;" :class="app.status === 'Shortlisted' ? 'bg-success' : 'bg-primary'"></div>
                <div class="d-flex justify-content-between align-items-center ps-2">
                  <div>
                    <h6 class="fw-bold mb-1">{{ app.company }}</h6>
                    <small class="text-muted">{{ app.role }}</small>
                  </div>
                  <span class="badge rounded-pill fw-bold p-2 px-3 shadow-sm"
                        :class="{'bg-primary': app.status === 'Applied', 'bg-success': app.status === 'Shortlisted', 'bg-warning text-dark': app.status === 'Interview', 'bg-danger': app.status === 'Rejected'}">
                    {{ app.status }}
                  </span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useFetchData } from '@/composables/useFetchData';

const { data:dashboardData, isLoading } = useFetchData('/api/dashboard/student','Failed to load Company dashboard data.', true);

</script>
