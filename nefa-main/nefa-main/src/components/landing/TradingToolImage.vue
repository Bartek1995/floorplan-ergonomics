<script setup>
import advancedToolsImg from '@/assets/img/advanced-trading-tools.webp'

defineOptions({
  inheritAttrs: false,
})
</script>

<template>
  <div class="col-span-12 lg:col-span-6" v-bind="$attrs">
    <div class="w-full sm:mt-20 xl:mt-0">
      <img :src="advancedToolsImg" class="w-full" alt="" />
    </div>
  </div>
</template>
