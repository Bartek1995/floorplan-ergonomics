<template>
  <div class="flex flex-col gap-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div class="flex items-center gap-2 text-2xl font-semibold">
        <i class="pi pi-building" />
        <span>Mieszkania</span>
      </div>

      <Button
        label="Dodaj mieszkanie"
        icon="pi pi-plus"
        @click="showCreateForm = true"
      />
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-12">
      <ProgressSpinner />
    </div>

    <!-- Error -->
    <Message v-else-if="errorMessage" severity="error" class="w-full">
      {{ errorMessage }}
    </Message>

    <!-- Grid -->
    <div
      v-else-if="flats.length"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      <Card
        v-for="flat in flats"
        :key="flat.id"
        class="cursor-pointer hover:shadow-lg transition-shadow"
        @click="viewFlat(flat.id)"
      >
        <template #header>
          <div class="h-48 overflow-hidden bg-surface-100">
            <img
              v-if="flat.layout?.image"
              :src="flat.layout.image"
              :alt="flat.name"
              class="w-full h-full object-cover"
            />
            <div v-else class="h-full flex items-center justify-center">
              <i class="pi pi-image text-5xl text-surface-400" />
            </div>
          </div>
        </template>

        <template #title>
          <span class="text-lg">{{ flat.name }}</span>
        </template>

        <template #subtitle>
          <span
            v-if="flat.address"
            class="flex items-center gap-1 text-sm text-surface-500"
          >
            <i class="pi pi-map-marker" />
            {{ flat.address }}
          </span>
        </template>

        <template #content>
          <div class="flex flex-wrap gap-3 text-sm">
            <span v-if="flat.rooms" class="flex items-center gap-1">
              <i class="pi pi-home" />
              {{ flat.rooms }} pokoi
            </span>
            <span v-if="flat.area_sqm" class="flex items-center gap-1">
              <i class="pi pi-square" />
              {{ flat.area_sqm }} m²
            </span>
          </div>
        </template>

        <template #footer>
          <div class="flex gap-2">
            <Button
              label="Edytuj"
              severity="info"
              size="small"
              outlined
              @click.stop="editFlat(flat.id)"
            />
            <Button
              icon="pi pi-trash"
              severity="danger"
              size="small"
              outlined
              :loading="deletingFlatId === flat.id"
              @click.stop="deleteFlat(flat.id)"
            />
          </div>
        </template>
      </Card>
    </div>

    <!-- Empty -->
    <div v-else class="flex flex-col items-center justify-center py-12 gap-3">
      <i class="pi pi-inbox text-5xl text-surface-400" />
      <p class="text-lg text-surface-500">Brak mieszkań</p>
      <Button
        label="Dodaj mieszkanie"
        icon="pi pi-plus"
        @click="showCreateForm = true"
      />
    </div>

    <!-- Dialog create -->
    <Dialog
      v-model:visible="showCreateForm"
      header="Nowe mieszkanie"
      :modal="true"
      :style="{ width: '600px' }"
    >
      <FlatCreateForm
        @cancel="showCreateForm = false"
        @flat-created="onFlatCreated"
      />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import Card from 'primevue/card'
import Button from 'primevue/button'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import Dialog from 'primevue/dialog'

import FlatCreateForm from './FlatCreateForm.vue'
import { flatApi, type Flat } from '@/api/flatApi'

const router = useRouter()

const flats = ref<Flat[]>([])
const isLoading = ref(false)
const errorMessage = ref('')
const showCreateForm = ref(false)

const deletingFlatId = ref<number | null>(null)

const loadFlats = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await flatApi.listFlats()
    flats.value = response.data.results
  } catch (error) {
    console.error('Error loading flats:', error)
    errorMessage.value =
      'Nie udało się załadować mieszkań. Sprawdź połączenie z serwerem.'
  } finally {
    isLoading.value = false
  }
}

const viewFlat = (flatId: number) => {
  router.push({ name: 'flat-detail', params: { id: flatId } })
}

const editFlat = (flatId: number) => {
  router.push({ name: 'floorplan-editor', params: { id: flatId } })
}

const deleteFlat = async (flatId: number) => {
  if (!confirm('Czy na pewno chcesz usunąć to mieszkanie?')) return

  deletingFlatId.value = flatId
  errorMessage.value = ''

  try {
    await flatApi.deleteFlat(flatId)
    flats.value = flats.value.filter(f => f.id !== flatId)
  } catch (error) {
    console.error('Error deleting flat:', error)
    errorMessage.value = 'Nie udało się usunąć mieszkania.'
  } finally {
    deletingFlatId.value = null
  }
}

const onFlatCreated = () => {
  showCreateForm.value = false
  loadFlats()
}

onMounted(loadFlats)
</script>
