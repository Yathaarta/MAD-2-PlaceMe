<template>
<RouterView></RouterView>

<ToastNotification />
</template>


<script setup>
import { RouterView } from 'vue-router';
import ToastNotification from '@/components/ToastNotification.vue';
</script>



<style scoped></style>
