import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useDataStore = defineStore('data', () => {
  const industries = ref([
  "IT & Software",
  "Fintech",
  "Telecommunications",

  "Automotive",
  "Manufacturing",
  "Electronics & Hardware",

  // infrastructure
  "Construction & Real Estate",
  "Energy, Oil & Gas",

  // management / business
  "Banking & Insurance",
  "Consulting",
  "Marketing & Sales",
  "Human Resources (HR)",
  "Supply Chain & Logistics",

  "EdTech",
  "E-Commerce",
  "Pharmaceuticals"
  ])

  return { industries }
})
