<template>
  <div id="carouselExampleIndicators" class="carousel slide carousel-fade" ref="carouselRef" data-bs-touch="false">
    <div class="carousel-indicators">
      <button
        type="button"
        data-bs-target="#carouselExampleIndicators"
        data-bs-slide-to="0"
        class="active"
        aria-current="true"
        aria-label="Slide 1"
      ></button>
      <button
        type="button"
        data-bs-target="#carouselExampleIndicators"
        data-bs-slide-to="1"
        aria-label="Slide 2"
      ></button>
    </div>
    <div class="carousel-inner">
      <div class="carousel-item active">
        <StudentRegister />
      </div>
      <div class="carousel-item">
        <CompanyRegister />
      </div>
    </div>
    <button
      class="carousel-control-prev"
      type="button"
      data-bs-target="#carouselExampleIndicators"
      data-bs-slide="prev"
    >
      <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Previous</span>
    </button>
    <button
      class="carousel-control-next"
      type="button"
      data-bs-target="#carouselExampleIndicators"
      data-bs-slide="next"
    >
      <span class="carousel-control-next-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Next</span>
    </button>
  </div>
</template>

<script setup>
import StudentRegister from '@/components/StudentRegister.vue'
import CompanyRegister from '@/components/CompanyRegister.vue'
import { useUIStore } from '@/stores/uiStore'
import { ref, onMounted, watch } from 'vue'
import { Carousel } from 'bootstrap'

const uiStore = useUIStore()

let carouselInstance = null
const carouselRef = ref(null)

onMounted(() => {
  // Initialize the Bootstrap Carousel
  if (carouselRef.value) {
    carouselInstance = new Carousel(carouselRef.value, {
      interval: false, // auto-slide off
      wrap: true,
    })

    carouselRef.value.addEventListener('slide.bs.carousel', (event) => {
      uiStore.activeSlideIndex = event.to
    })
  }
})

//  click Navbar button -> Store updates -> This runs -> Carousel moves.
watch(
  () => uiStore.activeSlideIndex,
  (newIndex) => {
    if (carouselInstance) {
      carouselInstance.to(newIndex)
    }
  },
)
</script>

<style scoped>
.carousel-control-next-icon,
.carousel-control-prev-icon {
  border: 2px solid black;
  border-radius: 8px;
  background-color: rgb(250, 249, 249);
  width: 2rem;
}

.carousel-control-prev,
.carousel-control-next {
    pointer-events: none;
}
.carousel-control-prev-icon,
.carousel-control-next-icon {
    pointer-events: auto;
}
</style>
