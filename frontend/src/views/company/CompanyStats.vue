<template>
  <div class="pb-5">
    <h3 class="fw-bold text-dark mb-4">Recruitment Analytics</h3>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-else class="row g-4">

      <!-- Chart card -->
      <div class="col-12 col-xl-8">
        <div class="card bg-white border-0 shadow-sm rounded-4 h-100">
          <div class="card-header bg-white border-0 p-4 pb-0">
             <h5 class="fw-bold text-dark mb-0"><i class="bi bi-bar-chart-fill me-2 text-primary"></i> Applicants per Role</h5>
             <p class="text-muted small mb-0 mt-1">Applications recieved for different roles in your company.</p>
          </div>
          <div class="card-body p-4">
             <div v-if="hasChartData" style="height: 420px;">
               <Bar :data="chartData" :options="chartOptions" />
             </div>

             <div v-else class="text-center py-5 text-muted h-100 d-flex flex-column justify-content-center">
               <i class="bi bi-graph-down text-muted opacity-50 mb-3" style="font-size: 3rem;"></i>
               <h6 class="fw-bold">Insufficient Data</h6>
               <p class="small">Post a drive and receive applications to generate analytics.</p>
             </div>
          </div>
        </div>
      </div>

      <!-- Info side panel -->
      <div class="col-12 col-xl-4">
        <div class="card bg-primary text-white border-0 shadow-sm rounded-4 h-100 p-4" style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);">
           <h4 class="fw-bold mb-4"><i class="bi bi-lightbulb-fill text-warning me-2"></i> Insight Tips</h4>

           <div class="mb-4">
             <h6 class="fw-bold text-white mb-2">Drive Engagement</h6>
             <p class="text-white-50 small">If a job role has a low applicant volume, consider broadening your allowed streams or reducing the minimum CGPA requirement to cast a wider net.</p>
           </div>

           <hr class="border-white opacity-25">

           <div class="mt-4">
             <h6 class="fw-bold text-white mb-2">Resume Shortlisting</h6>
             <p class="text-white-50 small">Navigate to your Applicant Tracking System (ATS) to filter these candidates by CGPA and update their statuses from "Applied" to "Shortlisted".</p>
           </div>

           <router-link to="/company-dashboard/applicants" class="btn btn-light text-dark rounded-pill w-100 fw-bold mt-auto mt-4">
             Go to ATS <i class="bi bi-arrow-right ms-2"></i>
           </router-link>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
import { useFetchData } from '@/composables/useFetchData';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const { data: statsData, isLoading } = useFetchData('/api/dashboard/company','Failed to load analytics.')

const hasChartData = computed(() => {
  if (!statsData.value.charts || !statsData.value.charts.applicants_per_drive) return false;
  return Object.keys(statsData.value.charts.applicants_per_drive).length > 0;
});

const chartData = computed(() => {
  if (!hasChartData.value) return { labels: [], datasets: [] };

  const rawData = statsData.value.charts.applicants_per_drive;
  const dataKeys = Object.keys(rawData);

  const bgColors = [
    'rgba(178, 235, 242, 0.4)',
    'rgba(255, 249, 196, 0.4)',
    'rgba(225, 190, 231, 0.4)'
  ];
  const borderColors = [
    '#26c6da',
    '#fbc02d',
    '#ab47bc'
  ];

  return {
    labels: dataKeys,
    datasets: [
      {
        label: 'Total Applicants',
        backgroundColor: dataKeys.map((_, i) => bgColors[i % bgColors.length]),
        borderColor: dataKeys.map((_, i) => borderColors[i % borderColors.length]),
        borderWidth: 2,
        borderRadius: 4,
        data: Object.values(rawData)
      }
    ]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  layout: { padding: { bottom: 15 } },
  plugins: { legend: { display: false } },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { precision: 0 },
      grid: { color: 'rgba(0, 0, 0, 0.06)', drawBorder: false }
    },
    x: {
      ticks: { autoSkip: false, maxRotation: 25, minRotation: 25 },
      grid: { display: true, color: 'rgba(0, 0, 0, 0.06)', drawBorder: false }
    }
  }
};
</script>
