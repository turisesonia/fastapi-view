<script setup>
const props = defineProps({
  items: {
    type: Array,
    default() {
      return []
    }
  },

})
</script>

<template>
  <div>
    <h1>Item</h1>

    <div v-for="item in items">
      <p>{{ item.name }}</p>
      <p>{{ item.description }}</p>
    </div>
  </div>
</template>