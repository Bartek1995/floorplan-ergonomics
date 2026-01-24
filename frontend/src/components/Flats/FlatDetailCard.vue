<template>
  <div class="flex flex-col gap-6">
    <!-- Nagłówek z przyciskiem powrotu -->
    <div class="flex items-center gap-4">
      <Button
        icon="pi pi-arrow-left"
        severity="secondary"
        text
        rounded
        @click="goBack"
      />
      <h1 class="text-2xl font-semibold">{{ flat?.name || 'Szczegóły mieszkania' }}</h1>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-12">
      <ProgressSpinner />
    </div>

    <!-- Błąd -->
    <Message v-else-if="error" severity="error" class="w-full">
      {{ error }}
    </Message>

    <!-- Zawartość -->
    <div v-else-if="flat" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Lewa kolumna - obraz -->
      <div class="lg:col-span-2">
        <Card>
          <template #header>
            <div class="h-80 overflow-hidden">
              <img
                v-if="flat.layout?.image"
                :src="flat.layout.image"
                :alt="flat.name"
                class="w-full h-full object-contain"
              />
              <div v-else class="w-full h-full flex flex-col items-center justify-center bg-surface-100 gap-4">
                <i class="pi pi-image text-6xl text-surface-400" />
                <p class="text-surface-500">Brak rzutu mieszkania</p>
                <Button
                  label="Dodaj rzut"
                  icon="pi pi-upload"
                  outlined
                  @click="goToEditor"
                />
              </div>
            </div>
          </template>

          <template #title>
            {{ flat.name }}
          </template>

          <template #subtitle>
            <span v-if="flat.address" class="flex items-center gap-2">
              <i class="pi pi-map-marker" />
              {{ flat.address }}
            </span>
          </template>

          <template #content>
            <p v-if="flat.description" class="text-surface-600">
              {{ flat.description }}
            </p>
            <p v-else class="text-surface-400 italic">
              Brak opisu
            </p>
          </template>
        </Card>
      </div>

      <!-- Prawa kolumna - statystyki i akcje -->
      <div class="flex flex-col gap-4">
        <!-- Statystyki -->
        <Card>
          <template #title>
            <i class="pi pi-chart-bar" /> Informacje
          </template>
          <template #content>
            <div class="flex flex-col gap-4">
              <div class="flex items-center justify-between">
                <span class="text-surface-500">Pokoje</span>
                <span class="text-xl font-semibold">{{ flat.rooms || '—' }}</span>
              </div>
              <Divider />
              <div class="flex items-center justify-between">
                <span class="text-surface-500">Powierzchnia</span>
                <span class="text-xl font-semibold">{{ flat.area_sqm ? `${flat.area_sqm} m²` : '—' }}</span>
              </div>
              <Divider />
              <div class="flex items-center justify-between">
                <span class="text-surface-500">Status layoutu</span>
                <Tag 
                  :value="flat.layout ? 'Dodany' : 'Brak'" 
                  :severity="flat.layout ? 'success' : 'warning'"
                />
              </div>
            </div>
          </template>
        </Card>

        <!-- Akcje -->
        <Card>
          <template #title>
            <i class="pi pi-cog" /> Akcje
          </template>
          <template #content>
            <div class="flex flex-col gap-2">
              <Button
                label="Edytuj layout"
                icon="pi pi-pencil"
                class="w-full"
                @click="goToEditor"
              />
              <Button
                label="Analizuj ergonomię"
                icon="pi pi-chart-line"
                severity="success"
                class="w-full"
                :disabled="!flat.layout"
              />
              <Button
                label="Usuń mieszkanie"
                icon="pi pi-trash"
                severity="danger"
                outlined
                class="w-full"
                @click="confirmDelete"
              />
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import Divider from 'primevue/divider'
import Tag from 'primevue/tag'
import { flatApi, type Flat } from '@/api/flatApi'

const router = useRouter()
const route = useRoute()

const flat = ref<Flat | null>(null)
const isLoading = ref(false)
const error = ref('')

const flatId = parseInt(route.params.id as string)

const loadFlat = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const response = await flatApi.getFlat(flatId)
    flat.value = response.data
  } catch (err) {
    console.error('Error loading flat:', err)
    error.value = 'Nie udało się załadować danych mieszkania'
  } finally {
    isLoading.value = false
  }
}

const goBack = () => {
  router.push({ name: 'flats-list' })
}

const goToEditor = () => {
  router.push({ name: 'floorplan-editor', params: { id: flatId } })
}

const confirmDelete = async () => {
  if (!confirm('Czy na pewno chcesz usunąć to mieszkanie?')) {
    return
  }

  try {
    await flatApi.deleteFlat(flatId)
    router.push({ name: 'flats-list' })
  } catch (err) {
    console.error('Error deleting flat:', err)
    error.value = 'Nie udało się usunąć mieszkania'
  }
}

onMounted(() => {
  loadFlat()
})
</script>