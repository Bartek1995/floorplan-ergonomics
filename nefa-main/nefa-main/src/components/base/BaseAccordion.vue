<script setup>
import { ref } from 'vue'
import { mdiChevronUp, mdiChevronDown } from '@mdi/js'

defineProps({
  accordion: {
    type: Object,
    required: true,
  },
})

const selected = ref(false)
</script>

<template>
  <li class="relative border-b-2 border-gray-200">
    <button type="button" class="w-full py-4 text-left" @click="selected = !selected">
      <div class="flex items-center justify-between">
        <span class="font-medium">{{ accordion.title }}</span>
        <svg class="w-5 h-5" viewBox="0 0 24 24">
          <path fill="currentColor" :d="selected ? mdiChevronUp : mdiChevronDown" />
        </svg>
      </div>
    </button>

    <Transition name="slide">
      <div v-if="selected" class="relative overflow-hidden transition-all duration-700">
        <div class="py-2">
          <p class="text-sm text-gray-700 tracking-wide leading-relaxed">
            {{ accordion.description }}
          </p>
        </div>
      </div>
    </Transition>
  </li>
</template>
