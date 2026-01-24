<template>
  <div>
    <Card>
      <template #title>🧪 Diagnostyka API</template>

      <div class="space-y-4">
        <!-- Test GETu flats -->
        <Card>
          <template #title>Test GET /api/flats</template>
          <Button label="Test GET /api/flats" @click="testGetFlats" />
          <pre v-if="testResult.get">{{ JSON.stringify(testResult.get, null, 2) }}</pre>
        </Card>

        <!-- Test POSTu -->
        <Card>
          <template #title>Test POST /api/flats</template>
          <div class="space-y-2 mb-2">
            <div>
              <label>Nazwa</label>
              <InputText v-model="testFlat.name" />
            </div>
            <div>
              <label>Adres</label>
              <InputText v-model="testFlat.address" />
            </div>
          </div>
          <Button label="Test POST /api/flats" @click="testCreateFlat" />
          <pre v-if="testResult.post">{{ JSON.stringify(testResult.post, null, 2) }}</pre>
        </Card>

        <!-- Błędy -->
        <Message v-if="testResult.error" severity="error" :text="testResult.error" />
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Card from 'primevue/card'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import { flatApi } from '@/api/flatApi'

const testFlat = ref({
  name: 'Test mieszkanie',
  address: 'ul. Testowa 1'
})

const testResult = ref({
  get: null as unknown,
  post: null as unknown,
  error: ''
})

const testGetFlats = async () => {
  testResult.value.error = ''
  try {
    const response = await flatApi.listFlats()
    testResult.value.get = response.data
    console.log('GET success:', response.data)
  } catch (error) {
    testResult.value.error = JSON.stringify(error)
    console.error('GET error:', error)
  }
}

const testCreateFlat = async () => {
  testResult.value.error = ''
  try {
    const response = await flatApi.createFlat(testFlat.value)
    testResult.value.post = response.data
    console.log('POST success:', response.data)
  } catch (error) {
    testResult.value.error = JSON.stringify(error)
    console.error('POST error:', error)
  }
}
</script>
