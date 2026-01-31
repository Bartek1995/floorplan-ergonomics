<script setup>
import { ref } from 'vue'
import NavLink from '@/components/NavLink.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import nefaLogo from '@/assets/img/logo/nefa.svg'

// MDI icons as SVG paths
import { mdiSegment, mdiClose, mdiChevronUp, mdiChevronDown } from '@mdi/js'

const open = ref(false)
const dropdownNavbar = ref(false)

const dropdownToggler = () => {
  dropdownNavbar.value = !dropdownNavbar.value
}
</script>

<template>
  <nav id="navbar" class="relative z-10 w-full text-neutral-800">
    <div class="flex flex-col max-w-screen-xl px-8 mx-auto lg:items-center lg:justify-between lg:flex-row py-4">
      <div class="flex flex-col lg:flex-row items-center space-x-4 xl:space-x-8">
        <div class="w-full flex flex-row items-center justify-between py-6">
          <div>
            <img :src="nefaLogo" class="w-24 xl:w-28" alt="Nefa Logo" />
          </div>
          <button class="rounded-lg lg:hidden focus:outline-none focus:shadow-outline" @click="open = !open">
            <svg v-if="!open" class="w-6 h-6" viewBox="0 0 24 24">
              <path fill="currentColor" :d="mdiSegment" />
            </svg>
            <svg v-else class="w-6 h-6" viewBox="0 0 24 24">
              <path fill="currentColor" :d="mdiClose" />
            </svg>
          </button>
        </div>
        <ul
          :class="[open ? 'flex' : 'hidden lg:flex']"
          class="w-full h-auto flex flex-col flex-grow lg:items-center pb-4 lg:pb-0 lg:justify-end lg:flex-row origin-top duration-300 xl:space-x-2 space-y-3 lg:space-y-0"
        >
          <NavLink name="Cryptocurrency" url="#" />
          <NavLink name="Exchanges" url="#" />
          <NavLink name="Watchlist" url="#" />
          <NavLink name="NFT" url="#" />
          <NavLink name="Portfolio" url="#" />
          <li class="relative group">
            <button
              class="md:px-4 py-2 text-sm bg-transparent rounded-lg text-[#666666] hover:text-gray-900 focus:outline-none focus:shadow-outline flex items-center"
              @click="dropdownToggler"
            >
              <span>Products</span>
              <svg class="w-4 h-4 ml-1" viewBox="0 0 24 24">
                <path fill="currentColor" :d="dropdownNavbar ? mdiChevronUp : mdiChevronDown" />
              </svg>
            </button>
            <Transition name="transform-fade-down">
              <ul
                v-if="dropdownNavbar"
                class="flex lg:absolute flex-col max-w-42 py-1 lg:bg-white rounded-md lg:shadow-md pl-2 lg:pl-0"
              >
                <li>
                  <a href="#" class="block py-2 px-4 text-sm text-gray-700 hover:bg-gray-100">Exchange</a>
                </li>
                <li>
                  <a href="#" class="block py-2 px-4 text-sm text-gray-700 hover:bg-gray-100">Wallet</a>
                </li>
                <li>
                  <a href="#" class="block py-2 px-4 text-sm text-gray-700 hover:bg-gray-100">Explorer</a>
                </li>
                <li>
                  <a href="#" class="block py-2 px-4 text-sm text-gray-700 hover:bg-gray-100">Charts</a>
                </li>
              </ul>
            </Transition>
          </li>
        </ul>
      </div>
      <div :class="[open ? 'flex' : 'hidden lg:flex']" class="space-x-3">
        <BaseButton class="px-8 xl:px-10 py-3 mt-2 bg-inherit text-gradient border border-[#0c66ee]">
          Login
        </BaseButton>
        <BaseButton class="px-8 xl:px-10 py-3 mt-2 bg-gradient-to-r from-[#468ef9] to-[#0c66ee] text-white">
          Sign Up
        </BaseButton>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.text-gradient {
  background: linear-gradient(136.91deg, #468ef9 -12.5%, #0c66ee 107.5%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>
