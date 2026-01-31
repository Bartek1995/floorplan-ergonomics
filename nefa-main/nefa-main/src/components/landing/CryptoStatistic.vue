<script setup>
import LineChart from '@/components/LineChart.vue'
import { mdiChevronRight, mdiPlusThick, mdiMinusThick } from '@mdi/js'

defineOptions({
  inheritAttrs: false,
})

defineProps({
  title: {
    type: String,
    default: '',
  },
  datasets: {
    type: Array,
    default: () => [],
  },
})

const getImageUrl = (name) => {
  return new URL(`../assets/img/crypto-icon/${name}`, import.meta.url).href
}
</script>

<template>
  <div class="w-full lg:w-1/3 mt-6 lg:mt-0 overflow-hidden space-y-6" v-bind="$attrs">
    <div class="w-full flex items-center justify-between">
      <span class="font-medium">{{ title }}</span>
      <button
        href="#"
        class="px-3 py-1 text-sm font-medium text-blue-500 flex items-center space-x-1 rounded-md hover:bg-blue-50 transition duration-300"
      >
        <span>More</span>
        <svg class="w-4 h-4" viewBox="0 0 24 24">
          <path fill="currentColor" :d="mdiChevronRight" />
        </svg>
      </button>
    </div>
    <div class="flex flex-col">
      <div class="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="px-2 sm:px-6 py-2 align-middle inline-block min-w-full overflow-hidden">
          <table class="min-w-full">
            <thead>
              <tr>
                <th class="text-left text-sm font-medium text-gray-500">Name</th>
                <th class="text-left text-sm font-medium text-gray-500">Price</th>
                <th class="hidden sm:block text-left text-sm font-medium text-gray-500">Chart</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="data in datasets" :key="data.id" class="border-b border-gray-200">
                <td class="py-4 whitespace-nowrap">
                  <div class="flex items-center space-x-2">
                    <img :src="getImageUrl(data.logo)" alt="" />
                    <span>{{ data.name }}</span>
                  </div>
                </td>
                <td class="py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <svg v-if="data.increase" class="w-3.5 h-3.5 text-emerald-500" viewBox="0 0 24 24">
                      <path fill="currentColor" :d="mdiPlusThick" />
                    </svg>
                    <svg v-else class="w-3.5 h-3.5 text-red-500" viewBox="0 0 24 24">
                      <path fill="currentColor" :d="mdiMinusThick" />
                    </svg>
                    <span>${{ data.price }}</span>
                  </div>
                </td>
                <td class="hidden sm:block whitespace-nowrap">
                  <div>
                    <LineChart class="w-28 h-12 -mx-2" :datasets="data.data" :increase="data.increase" />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
