<script setup>
import { mdiCheckCircle } from '@mdi/js'

defineProps({
  title: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <li class="space-y-2">
    <div class="flex items-center space-x-2">
      <svg class="w-5 h-5 text-[#0c66ee]" viewBox="0 0 24 24">
        <path fill="currentColor" :d="mdiCheckCircle" />
      </svg>
      <span>{{ title }}</span>
    </div>
    <slot></slot>
  </li>
</template>
