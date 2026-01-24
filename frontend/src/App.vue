// src/App.vue
<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import router from '@/router';

const auth = useAuthStore();

const handleStorageChange = (event: StorageEvent) => {
  if (event.key === 'access_token' && !event.newValue) {
    auth.logout();
    router.replace({ name: 'login' });
  }
};

onMounted(() => {
  window.addEventListener('storage', handleStorageChange);
});

onUnmounted(() => {
  window.removeEventListener('storage', handleStorageChange);
});
</script>

<template>
  <div
    v-if="!auth.isAuthReady"
    class="flex items-center justify-center h-screen bg-surface-100"
  >
    <div class="w-full max-w-md text-center px-6">
      <ProgressBar mode="indeterminate" style="height: 6px" class="mb-4" />
      <div class="text-gray-600 text-lg">Ładowanie…</div>
    </div>
  </div>
  <div>
    <router-view />
  </div>
</template>

<style>
  body {
    scrollbar-width: thin; 
    scrollbar-color: rgba(141, 139, 139, 0.2) transparent;
  }
</style>
