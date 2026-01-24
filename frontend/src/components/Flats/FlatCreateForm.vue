<template>
  <form @submit.prevent="handleSubmit" class="flex flex-col gap-4">
    <div class="flex flex-col gap-2">
      <label for="name" class="font-medium">Nazwa mieszkania *</label>
      <InputText
        id="name"
        v-model="form.name"
        placeholder="np. Mieszkanie przy parku"
        class="w-full"
        required
      />
    </div>

    <div class="flex flex-col gap-2">
      <label for="address" class="font-medium">Adres</label>
      <InputText
        id="address"
        v-model="form.address"
        placeholder="ul. Przykładowa 10, Warszawa"
        class="w-full"
      />
    </div>

    <div class="grid grid-cols-2 gap-4">
      <div class="flex flex-col gap-2">
        <label for="rooms" class="font-medium">Liczba pokoi</label>
        <InputNumber
          id="rooms"
          v-model="form.rooms"
          :min="1"
          :max="10"
          class="w-full"
        />
      </div>

      <div class="flex flex-col gap-2">
        <label for="area" class="font-medium">Powierzchnia (m²)</label>
        <InputNumber
          id="area"
          v-model="form.area_sqm"
          :min="10"
          :max="500"
          class="w-full"
        />
      </div>
    </div>

    <div class="flex flex-col gap-2">
      <label for="description" class="font-medium">Opis</label>
      <Textarea
        id="description"
        v-model="form.description"
        placeholder="Dodatkowe informacje..."
        rows="3"
        class="w-full"
      />
    </div>

    <div class="flex flex-col gap-2">
      <label class="font-medium">Rzut mieszkania (opcjonalnie)</label>
      <FileUpload
        mode="basic"
        name="image"
        accept="image/*,.pdf"
        :auto="false"
        chooseLabel="Wybierz plik"
        @select="handleImageSelect"
        class="w-full"
      />
      <small v-if="selectedImage" class="text-surface-500">
        Wybrany plik: {{ selectedImage.name }}
      </small>
    </div>

    <Message v-if="successMessage" severity="success" class="w-full">
      {{ successMessage }}
    </Message>
    <Message v-if="errorMessage" severity="error" class="w-full">
      {{ errorMessage }}
    </Message>

    <div class="flex justify-end gap-2 pt-4">
      <Button
        type="button"
        label="Anuluj"
        severity="secondary"
        outlined
        @click="$emit('cancel')"
      />
      <Button
        type="submit"
        label="Utwórz mieszkanie"
        icon="pi pi-check"
        :loading="isLoading"
      />
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import FileUpload from 'primevue/fileupload'
import Message from 'primevue/message'
import { flatApi } from '@/api/flatApi'

const emit = defineEmits<{
  cancel: []
  'flat-created': []
}>()

const form = ref({
  name: '',
  address: '',
  rooms: null as number | null,
  area_sqm: null as number | null,
  description: ''
})

const selectedImage = ref<File | null>(null)
const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const handleImageSelect = (event: { files: File[] }) => {
  if (event.files && event.files.length > 0) {
    selectedImage.value = event.files[0]
  }
}

const handleSubmit = async () => {
  if (!form.value.name.trim()) {
    errorMessage.value = 'Nazwa mieszkania jest wymagana'
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await flatApi.createFlat({
      name: form.value.name,
      address: form.value.address || undefined,
      rooms: form.value.rooms || undefined,
      area_sqm: form.value.area_sqm || undefined,
      description: form.value.description || undefined
    })

    const flatId = response.data.id

    if (selectedImage.value) {
      await flatApi.uploadLayoutImage(flatId, selectedImage.value)
    }

    successMessage.value = 'Mieszkanie zostało utworzone!'
    
    form.value = {
      name: '',
      address: '',
      rooms: null,
      area_sqm: null,
      description: ''
    }
    selectedImage.value = null

    setTimeout(() => {
      emit('flat-created')
    }, 500)

  } catch (error) {
    console.error('Error creating flat:', error)
    errorMessage.value = 'Nie udało się utworzyć mieszkania. Spróbuj ponownie.'
  } finally {
    isLoading.value = false
  }
}
</script>