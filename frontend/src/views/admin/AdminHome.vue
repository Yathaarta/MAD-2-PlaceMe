<template>
  <div v-if="isLoading" class="text-center py-5"><div class="spinner-border text-danger"></div></div>
  <div v-else-if="dashboardData" class="container-fluid px-0">
    <h2 class="fw-bold text-dark mb-4">Institute Command Center</h2>

    <div class="row g-4 mb-4">
      <div class="col-12 col-md-4">
        <div class="card bg-white border-0 shadow-sm rounded-4 py-3 h-100 border-start border-danger border-4">
          <div class="card-body text-center">
            <h6 class="text-muted fw-bold text-uppercase">Total Students</h6>
            <h1 class="fw-bold text-danger">{{ dashboardData.stats.total_students }}</h1>
          </div>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="card bg-white border-0 shadow-sm rounded-4 py-3 h-100 border-start border-primary border-4">
          <div class="card-body text-center">
            <h6 class="text-muted fw-bold text-uppercase">Registered Companies</h6>
            <h1 class="fw-bold text-primary">{{ dashboardData.stats.total_companies }}</h1>
            <span v-if="dashboardData.stats.pending_companies > 0" class="badge bg-warning text-dark mt-2">{{ dashboardData.stats.pending_companies }} Pending Approval</span>
          </div>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="card bg-white border-0 shadow-sm rounded-4 py-3 h-100 border-start border-success border-4">
          <div class="card-body text-center">
            <h6 class="text-muted fw-bold text-uppercase">Placement Drives</h6>
            <h1 class="fw-bold text-success">{{ dashboardData.stats.total_drives }}</h1>
             <span v-if="dashboardData.stats.pending_drives > 0" class="badge bg-warning text-dark mt-2">{{ dashboardData.stats.pending_drives }} Pending Approval</span>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-12 col-lg-6">
        <div class="card bg-white border-0 shadow-sm rounded-4 h-100 p-4">
          <h5 class="fw-bold text-dark mb-4">Application Status Overview</h5>
          <canvas id="statusChart"></canvas>
        </div>
      </div>
      <div class="col-12 col-lg-6">
         <div class="card bg-white border-0 shadow-sm rounded-4 h-100 p-4">
           <h5 class="fw-bold text-dark mb-4">Quick Actions Needed</h5>
           <p class="text-muted" v-if="dashboardData.stats.pending_companies === 0 && dashboardData.stats.pending_drives === 0">
             All caught up! No pending approvals.
           </p>
           <router-link v-if="dashboardData.stats.pending_companies > 0" to="/admin-dashboard/companies" class="btn btn-outline-primary mb-3 text-start">
             Review {{dashboardData.stats.pending_companies}} Pending Companies <i class="bi bi-arrow-right float-end"></i>
           </router-link>
           <router-link v-if="dashboardData.stats.pending_drives > 0" to="/admin-dashboard/drives" class="btn btn-outline-success text-start">
             Review {{dashboardData.stats.pending_drives}} Pending Drives <i class="bi bi-arrow-right float-end"></i>
           </router-link>
         </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, nextTick } from 'vue';
import Chart from 'chart.js/auto';
import { useFetchData } from '@/composables/useFetchData';

const { data: dashboardData, isLoading, fetchData: fetchDashboardData } = useFetchData('/api/admin/dashboard','Failed to load Admin dashboard data.', true)

onMounted(async () => {
  await fetchDashboardData();
  if (dashboardData.value && dashboardData.value.charts) {
    nextTick(() => {
      const ctx = document.getElementById('statusChart');
      if (ctx) {
        new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: Object.keys(dashboardData.value.charts.application_status),
            datasets: [{
              data: Object.values(dashboardData.value.charts.application_status),

              backgroundColor: [
                'rgba(13, 202, 240, 0.4)',  // Cyan
                'rgba(255, 193, 7, 0.4)',   // Yellow
                'rgba(220, 53, 69, 0.4)',   // Red
                'rgba(25, 135, 84, 0.4)',   // Green
                'rgba(108, 117, 125, 0.4)',  // Gray
              ],
              borderColor: [
                '#0dcaf0',
                '#ffc107',
                '#dc3545',
                '#198754',
                '#6c757d',
              ],
              borderWidth: 2
            }]
          },
          options: {
              plugins: {
                legend: {
                  position: 'bottom'
                }
              }
            }
        });
      }
    });
  }
});
</script>
