<script setup>
defineProps({
  img: {
    type: String,
    default: '',
  },
})

const getImageUrl = (name) => {
  return new URL(`../../assets/img/partner/${name}`, import.meta.url).href
}
</script>

<template>
  <div>
    <img :src="getImageUrl(img)" class="sm:w-1/2 lg:w-72 mx-auto" alt="" />
  </div>
</template>
