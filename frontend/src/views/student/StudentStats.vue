<template>
  <div class="pb-5">
    <h3 class="fw-bold text-dark mb-4">Placement Statistics</h3>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-else class="row g-4">

      <!-- Chart card -->
      <div class="col-12 col-xl-8">
        <div class="card bg-white border-0 shadow-sm rounded-4 h-100">
          <div class="card-header bg-white border-0 p-4 pb-0">
            <h5 class="fw-bold text-dark mb-0"><i class="bi bi-pie-chart-fill me-2 text-primary"></i> Application Outcomes</h5>
            <p class="text-muted small mb-0 mt-1">Status overview of your recent job applications.</p>
          </div>
          <div class="card-body p-4">
            <div v-if="hasData" style="height: 420px;">
              <Bar :data="chartData" :options="chartOptions" />
            </div>

            <div v-else class="text-center py-5 text-muted h-100 d-flex flex-column justify-content-center">
              <i class="bi bi-bar-chart text-muted opacity-50 mb-3" style="font-size: 3rem;"></i>
              <h6 class="fw-bold">No Data Available</h6>
              <p class="small">No application data to chart yet. Start applying!</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Info side panel -->
      <div class="col-12 col-xl-4">
        <div class="card bg-primary text-white border-0 shadow-sm rounded-4 h-100 p-4 d-flex flex-column justify-content-center text-center" style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);">
          <i class="bi bi-trophy display-1 text-warning mb-3"></i>
          <h4 class="fw-bold">Keep Going!</h4>
          <p class="mb-0 text-light mt-2">You have applied to <strong class="fs-5">{{ totalApplied }}</strong> companies. Students who apply to 10+ have a 60% higher chance of placement.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useFetchData } from '@/composables/useFetchData';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const { data:dashboardData, isLoading } = useFetchData('/api/student/applications','Failed to load analytics.');

const statusCounts = computed(() => {
  const counts = { 'Applied': 0, 'Shortlisted': 0, 'Interview': 0, 'Selected': 0, 'Rejected': 0 };
  if (dashboardData.value && dashboardData.value.application) {
    dashboardData.value.application.forEach(app => {
      if (counts[app.status] !== undefined) counts[app.status]++;
    });
  }
  return counts;
});

const totalApplied = computed(() => dashboardData.value ? dashboardData.value.application.length : 0);
const hasData = computed(() => totalApplied.value > 0);

const chartData = computed(() => ({
  labels: ['Applied', 'Shortlisted', 'Interview', 'Selected', 'Rejected'],
  datasets: [{
    label: 'Applications',
    data: [statusCounts.value.Applied, statusCounts.value.Shortlisted, statusCounts.value.Interview, statusCounts.value.Selected, statusCounts.value.Rejected],
    backgroundColor: [
      'rgba(13, 110, 253, 0.4)',
      'rgba(13, 202, 240, 0.4)',
      'rgba(255, 193, 7, 0.4)',
      'rgba(25, 135, 84, 0.4)',
      'rgba(220, 53, 69, 0.4)'
    ],
    borderColor: [
      '#0d6efd',
      '#0dcaf0',
      '#ffc107',
      '#198754',
      '#dc3545'
    ],
    borderWidth: 2,
    borderRadius: 4,
  }]
}));

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  layout: { padding: { bottom: 15 } },
  plugins: { legend: { display: false } },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { stepSize: 1 },
      grid: { color: 'rgba(0, 0, 0, 0.06)', drawBorder: false }
    },
    x: {
      ticks: { autoSkip: false, maxRotation: 25, minRotation: 25 },
      grid: { display: true, color: 'rgba(0, 0, 0, 0.06)', drawBorder: false }
    }
  }
};
</script>
