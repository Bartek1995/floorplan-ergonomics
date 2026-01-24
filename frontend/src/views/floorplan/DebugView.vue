<template>
  <div>
    <Card>
      <template #title>🧪 TEST RENDEROWANIA</template>

      <div class="space-y-4">
        <!-- Test 1: Plain HTML -->
        <Card>
          <template #title>Test 1: Plain HTML</template>
          <button>TEST BUTTON</button>
        </Card>

        <!-- Test 2: PrimeVue Button (bez importu) -->
        <Card>
          <template #title>Test 2: PrimeVue Button</template>
          <Button label="PrimeVue Button" />
        </Card>

        <!-- Test 3: PrimeVue Card (bez importu) -->
        <Card>
          <template #title>Test 3: PrimeVue Card</template>
          <p>Card content</p>
        </Card>

        <!-- Test 4: Dane mieszkań -->
        <Card>
          <template #title>Test 4: Dane mieszkań (raw)</template>
          <pre>{{ flats }}</pre>
        </Card>

        <!-- Test 5: V-for loop -->
        <Card>
          <template #title>Test 5: V-for loop na mieszkaniach</template>
          <div v-if="flats.length > 0">
            <p>✅ Mieszkań: {{ flats.length }}</p>
            <div v-for="flat in flats" :key="flat.id">
              <Card>
                <template #title>{{ flat.name }}</template>
                <p>Adres: {{ flat.address }}</p>
                <p>Pokoje: {{ flat.rooms }}, M²: {{ flat.area_sqm }}</p>
              </Card>
            </div>
          </div>
          <div v-else>
            ❌ Brak mieszkań (flats.length = 0)
          </div>
        </Card>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import { flatApi, type Flat } from '@/api/flatApi'

const flats = ref<Flat[]>([])

onMounted(async () => {
  try {
    const response = await flatApi.listFlats()
    flats.value = response.data.results
    console.log('Loaded flats:', flats.value)
  } catch (error) {
    console.error('Error:', error)
  }
})
</script>
