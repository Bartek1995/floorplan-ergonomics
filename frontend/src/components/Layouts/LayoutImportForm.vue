<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-col gap-2">
      <label for="layout-file">Plik layoutu (PDF/JPG)</label>
      <FileUpload
        id="layout-file"
        mode="basic"
        name="image"
        accept="image/*,.pdf"
        :auto="false"
        chooseLabel="Wybierz plik"
        @select="handleFileSelect"
      />
    </div>

    <div class="flex flex-col gap-2">
      <label for="layout-scale">Skala (cm/px)</label>
      <InputNumber
        id="layout-scale"
        v-model="scaleCmPerPx"
        :min="0"
        :step="0.01"
        :minFractionDigits="2"
        :maxFractionDigits="4"
        placeholder="np. 0.5"
      />
    </div>

    <Chip v-if="selectedFile" :label="selectedFile.name" icon="pi pi-paperclip" />

    <Message v-if="successMessage" severity="success">
      {{ successMessage }}
    </Message>
    <Message v-if="errorMessage" severity="error">
      {{ errorMessage }}
    </Message>

    <div class="flex gap-2">
      <Button
        v-if="showCancel"
        label="Anuluj"
        severity="secondary"
        outlined
        @click="$emit('cancel')"
      />
      <Button
        label="Importuj"
        icon="pi pi-upload"
        :loading="isUploading"
        :disabled="!selectedFile"
        @click="handleUpload"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import FileUpload from 'primevue/fileupload'
import InputNumber from 'primevue/inputnumber'
import Message from 'primevue/message'
import { flatApi, layoutApi as flatLayoutApi, type Layout } from '@/api/flatApi'

const props = withDefaults(defineProps<{
  flatId: number
  initialScale?: number | null
  showCancel?: boolean
}>(), {
  showCancel: true
})

const emit = defineEmits<{
  cancel: []
  uploaded: [Layout]
}>()

const selectedFile = ref<File | null>(null)
const scaleCmPerPx = ref<number | null>(props.initialScale ?? null)
const isUploading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

watch(
  () => props.initialScale,
  newValue => {
    if (newValue !== undefined) {
      scaleCmPerPx.value = newValue
    }
  }
)

const handleFileSelect = (event: { files: File[] }) => {
  if (event.files && event.files.length > 0) {
    selectedFile.value = event.files[0]
  }
}

const handleUpload = async () => {
  if (!selectedFile.value) {
    errorMessage.value = 'Wybierz plik przed importem.'
    return
  }

  isUploading.value = true
  successMessage.value = ''
  errorMessage.value = ''

  try {
    const response = await flatApi.uploadLayoutImage(props.flatId, selectedFile.value)
    let layout = response.data

    if (scaleCmPerPx.value !== null && scaleCmPerPx.value !== undefined) {
      const scaleResponse = await flatLayoutApi.setScale(layout.id, scaleCmPerPx.value)
      layout = scaleResponse.data
    }

    successMessage.value = 'Rzut zostal zaimportowany.'
    selectedFile.value = null
    emit('uploaded', layout)
  } catch (error) {
    console.error('Layout import error:', error)
    errorMessage.value = 'Nie udalo sie zaimportowac rzutu.'
  } finally {
    isUploading.value = false
  }
}
</script>
