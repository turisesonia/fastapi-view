<script setup>
import Navbar from '@/js/Components/Navbar.vue'

const props = defineProps({

})
</script>

<template>
  <div class="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
    <Navbar></Navbar>
    <slot name="body"></slot>
  </div>
</template>