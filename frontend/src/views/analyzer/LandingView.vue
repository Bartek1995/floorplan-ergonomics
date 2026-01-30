<script setup lang="ts">
/**
 * Loktis - Landing View - strona główna z formularzem analizy lokalizacji
 * loktis.pl - Analiza ryzyka zakupu mieszkania
 * 
 * NOWY MODEL: User wskazuje lokalizację + podaje cenę/metraż
 * Link do ogłoszenia jest OPCJONALNY (tylko referencja)
 */
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { analyzerApi, getErrorMessage, type HistoryItem } from '@/api/analyzerApi';
import LocationPicker from '@/components/LocationPicker.vue';

const router = useRouter();
const toast = useToast();

// State - location first approach
const selectedLocation = ref<{ lat: number; lng: number; address: string } | null>(null);
const price = ref<number | null>(null);
const areaSqm = ref<number | null>(null);
const referenceUrl = ref('');
const radius = ref(500);

// UI State
const isLoading = ref(false);
const loadingStatus = ref('');
const loadingProgress = ref(0);
const recentAnalyses = ref<HistoryItem[]>([]);
const isLoadingRecent = ref(false);
const showAdvanced = ref(false);

const radiusOptions = [
  { label: '500m', value: 500 },
  { label: '1000m', value: 1000 },
];

// Loading steps for progress animation
const loadingSteps = [
  { status: 'Inicjalizacja...', progress: 10 },
  { status: 'Pobieranie danych...', progress: 25 },
  { status: 'Analizowanie okolicy...', progress: 50 },
  { status: 'Sprawdzanie POI...', progress: 75 },
  { status: 'Generowanie raportu...', progress: 90 },
];

// Computed
const canSubmit = computed(() => {
  return selectedLocation.value !== null && price.value !== null && areaSqm.value !== null && !isLoading.value;
});

const pricePerSqm = computed(() => {
  if (price.value && areaSqm.value && areaSqm.value > 0) {
    return Math.round(price.value / areaSqm.value);
  }
  return null;
});

// Methods
function handleLocationSelected(data: { lat: number; lng: number; address: string }) {
  selectedLocation.value = data;
}

function clearLocation() {
  selectedLocation.value = null;
}

async function handleAnalyze() {
  if (!canSubmit.value || !selectedLocation.value) return;
  
  isLoading.value = true;
  loadingStatus.value = 'Inicjalizacja...';
  loadingProgress.value = 10;
  
  try {
    // Analiza strumieniowa z lokalizacją
    const report = await analyzerApi.analyzeLocationStream(
      selectedLocation.value.lat,
      selectedLocation.value.lng,
      price.value!,
      areaSqm.value!,
      selectedLocation.value.address,
      radius.value,
      referenceUrl.value || undefined,
      (event) => {
        if (event.message) {
          loadingStatus.value = event.message;
          const step = loadingSteps.find(s => event.message?.includes(s.status.split('...')[0]));
          if (step) loadingProgress.value = step.progress;
          else loadingProgress.value = Math.min(loadingProgress.value + 10, 95);
        }
      }
    );
    
    loadingProgress.value = 100;
    
    if (!report) {
      throw new Error('Brak raportu w odpowiedzi');
    }
    
    // Zapisz raport w sessionStorage i przekieruj
    sessionStorage.setItem('lastReport', JSON.stringify(report));
    sessionStorage.setItem('lastReportUrl', referenceUrl.value || selectedLocation.value.address);
    
    router.push({
      name: 'report',
      query: { fromAnalysis: 'true' },
    });
    
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Błąd analizy',
      detail: getErrorMessage(error),
      life: 5000,
    });
  } finally {
    isLoading.value = false;
    loadingStatus.value = '';
    loadingProgress.value = 0;
  }
}

async function loadRecentAnalyses() {
  isLoadingRecent.value = true;
  try {
    recentAnalyses.value = await analyzerApi.getRecentHistory();
  } catch (error) {
    console.warn('Nie udało się pobrać historii:', error);
  } finally {
    isLoadingRecent.value = false;
  }
}

function openHistoryItem(item: HistoryItem) {
  router.push({ name: 'history-detail', params: { id: item.id } });
}

function formatPrice(price: number | null): string {
  if (!price) return '-';
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN',
    maximumFractionDigits: 0,
  }).format(price);
}

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('pl-PL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function getScoreColor(score: number | null): string {
  if (score === null) return '#6B7280';
  if (score >= 70) return '#10B981';
  if (score >= 50) return '#F59E0B';
  if (score >= 30) return '#F97316';
  return '#EF4444';
}

// Load recent on mount
loadRecentAnalyses();
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-surface-50 via-white to-primary-50 dark:from-surface-900 dark:via-surface-800 dark:to-surface-900">
    <!-- Hero Section -->
    <div class="flex-1 flex items-center justify-center p-6 py-12">
      <div class="w-full max-w-5xl">
        <!-- Logo/Title with gradient -->
        <div class="text-center mb-10">
          <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-400 to-primary-600 shadow-xl mb-6">
            <i class="pi pi-map-marker text-4xl text-white"></i>
          </div>
          <h1 class="text-5xl font-extrabold mb-4 bg-gradient-to-r from-primary-600 via-primary-500 to-primary-400 bg-clip-text text-transparent">
            Loktis
          </h1>
          <p class="text-lg text-surface-600 dark:text-surface-300 font-medium mb-2">
            Analiza ryzyka zakupu mieszkania
          </p>
          <p class="text-base text-surface-500 max-w-2xl mx-auto">
            Wskaż lokalizację, podaj cenę i metraż – otrzymasz szczegółową ocenę okolicy i ryzyk zakupu
          </p>
        </div>
        
        <!-- Main Form Card - Glassmorphism -->
        <div class="relative mb-10">
          <!-- Glow effect -->
          <div class="absolute -inset-1 bg-gradient-to-r from-primary-400 via-primary-500 to-primary-600 rounded-3xl blur-xl opacity-20"></div>
          
          <div class="relative bg-white/80 dark:bg-surface-800/80 backdrop-blur-xl rounded-2xl shadow-2xl p-8 border border-white/20">
            <div class="flex flex-col gap-6">
              
              <!-- Step 1: Location -->
              <div>
                <div class="flex items-center gap-2 mb-3">
                  <span class="inline-flex items-center justify-center w-7 h-7 rounded-full bg-primary-500 text-white text-sm font-bold">1</span>
                  <h3 class="font-semibold text-surface-800 dark:text-surface-100">Wskaż lokalizację</h3>
                  <span class="text-red-500">*</span>
                </div>
                
                <!-- Selected location display or picker -->
                <div v-if="selectedLocation" class="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-700 rounded-xl p-4">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center">
                        <i class="pi pi-check text-white"></i>
                      </div>
                      <div>
                        <p class="font-medium text-surface-800 dark:text-surface-100">{{ selectedLocation.address }}</p>
                        <p class="text-sm text-surface-500">{{ selectedLocation.lat.toFixed(5) }}, {{ selectedLocation.lng.toFixed(5) }}</p>
                      </div>
                    </div>
                    <Button 
                      icon="pi pi-times" 
                      severity="secondary" 
                      text 
                      rounded 
                      @click="clearLocation"
                      v-tooltip="'Zmień lokalizację'"
                    />
                  </div>
                </div>
                
                <div v-else class="border-2 border-dashed border-surface-200 dark:border-surface-600 rounded-xl p-4">
                  <LocationPicker
                    @location-selected="handleLocationSelected"
                    :show-cancel="false"
                  />
                </div>
              </div>
              
              <!-- Step 2: Price & Area -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div class="flex items-center gap-2 mb-3">
                    <span class="inline-flex items-center justify-center w-7 h-7 rounded-full bg-primary-500 text-white text-sm font-bold">2</span>
                    <h3 class="font-semibold text-surface-800 dark:text-surface-100">Cena</h3>
                    <span class="text-red-500">*</span>
                  </div>
                  <div class="relative">
                    <InputNumber 
                      v-model="price"
                      placeholder="np. 650 000"
                      :min="0"
                      :max="50000000"
                      locale="pl-PL"
                      class="w-full"
                      inputClass="!py-3 !text-lg"
                      :disabled="isLoading"
                    />
                    <span class="absolute right-4 top-1/2 -translate-y-1/2 text-surface-400 font-medium">PLN</span>
                  </div>
                </div>
                
                <div>
                  <div class="flex items-center gap-2 mb-3">
                    <span class="inline-flex items-center justify-center w-7 h-7 rounded-full bg-primary-500 text-white text-sm font-bold">3</span>
                    <h3 class="font-semibold text-surface-800 dark:text-surface-100">Metraż</h3>
                    <span class="text-red-500">*</span>
                  </div>
                  <div class="relative">
                    <InputNumber 
                      v-model="areaSqm"
                      placeholder="np. 54"
                      :min="1"
                      :max="1000"
                      :minFractionDigits="0"
                      :maxFractionDigits="1"
                      class="w-full"
                      inputClass="!py-3 !text-lg"
                      :disabled="isLoading"
                    />
                    <span class="absolute right-4 top-1/2 -translate-y-1/2 text-surface-400 font-medium">m²</span>
                  </div>
                </div>
              </div>
              
              <!-- Price per sqm display -->
              <div v-if="pricePerSqm" class="bg-surface-50 dark:bg-surface-700/50 rounded-xl p-3 flex items-center justify-center gap-2">
                <span class="text-surface-500">Cena za m²:</span>
                <span class="font-bold text-primary-600 dark:text-primary-400">{{ formatPrice(pricePerSqm) }}/m²</span>
              </div>
              
              <!-- Advanced Options Toggle -->
              <div>
                <button 
                  @click="showAdvanced = !showAdvanced"
                  class="flex items-center gap-2 text-sm text-surface-500 hover:text-primary-500 transition-colors"
                >
                  <i :class="showAdvanced ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"></i>
                  Opcje zaawansowane
                </button>
                
                <Transition name="slide">
                  <div v-if="showAdvanced" class="mt-4 space-y-4">
                    <!-- Reference URL (optional) -->
                    <div>
                      <label class="block text-sm font-medium text-surface-600 dark:text-surface-300 mb-2">
                        <i class="pi pi-link mr-1"></i>
                        Link do ogłoszenia (opcjonalnie)
                      </label>
                      <InputText 
                        v-model="referenceUrl"
                        placeholder="https://www.otodom.pl/pl/oferta/..."
                        class="w-full"
                        :disabled="isLoading"
                      />
                      <p class="text-xs text-surface-400 mt-1">Zapisany jako referencja w raporcie</p>
                    </div>
                    
                    <!-- Radius -->
                    <div class="flex items-center gap-3">
                      <span class="text-sm font-medium text-surface-600 dark:text-surface-300">
                        <i class="pi pi-compass mr-1"></i>
                        Zasięg analizy:
                      </span>
                      <SelectButton 
                        v-model="radius" 
                        :options="radiusOptions" 
                        optionLabel="label" 
                        optionValue="value" 
                        :allowEmpty="false"
                        class="!shadow-sm"
                      />
                    </div>
                  </div>
                </Transition>
              </div>
              
              <!-- Submit Button -->
              <div class="flex justify-end">
                <Button
                  :label="isLoading ? 'Analizuję...' : 'Analizuj lokalizację'"
                  :icon="isLoading ? 'pi pi-spin pi-spinner' : 'pi pi-search'"
                  :disabled="!canSubmit"
                  @click="handleAnalyze"
                  class="!py-3 !px-8 !text-lg !font-semibold !rounded-xl !shadow-lg hover:!shadow-xl !transition-all"
                  :class="{ '!bg-gradient-to-r !from-primary-500 !to-primary-600': !isLoading }"
                />
              </div>

              <!-- Modern Loading Status -->
              <Transition name="fade">
                <div v-if="isLoading" class="mt-2">
                  <div class="relative overflow-hidden bg-gradient-to-br from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-700 rounded-2xl p-6">
                    <!-- Animated background -->
                    <div class="absolute inset-0 overflow-hidden">
                      <div class="absolute -inset-[10px] opacity-30">
                        <div class="absolute top-0 left-0 w-40 h-40 bg-primary-400 rounded-full mix-blend-multiply filter blur-xl animate-blob"></div>
                        <div class="absolute top-0 right-0 w-40 h-40 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-2000"></div>
                        <div class="absolute bottom-0 left-1/2 w-40 h-40 bg-pink-400 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-4000"></div>
                      </div>
                    </div>
                    
                    <!-- Content -->
                    <div class="relative">
                      <div class="flex items-center gap-4 mb-4">
                        <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center shadow-lg">
                          <ProgressSpinner style="width: 28px; height: 28px" strokeWidth="4" fill="transparent" animationDuration=".7s" />
                        </div>
                        <div class="flex-1">
                          <p class="font-bold text-lg text-surface-800 dark:text-surface-100">{{ loadingStatus }}</p>
                          <p class="text-sm text-surface-500">Proszę czekać...</p>
                        </div>
                        <span class="text-2xl font-bold text-primary-500">{{ loadingProgress }}%</span>
                      </div>
                      
                      <!-- Modern Progress bar with glow -->
                      <div class="relative">
                        <div class="h-3 bg-surface-200 dark:bg-surface-600 rounded-full overflow-hidden shadow-inner">
                          <div 
                            class="h-full bg-gradient-to-r from-primary-400 via-primary-500 to-primary-600 rounded-full transition-all duration-500 ease-out relative"
                            :style="{ width: `${loadingProgress}%` }"
                          >
                            <!-- Shimmer effect -->
                            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Transition>
            </div>
          </div>
        </div>
        
        <!-- Features - Modern Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div class="group bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-surface-100 dark:border-surface-700 hover:-translate-y-1">
            <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-red-400 to-rose-500 flex items-center justify-center shadow-lg mb-4 group-hover:scale-110 transition-transform">
              <i class="pi pi-exclamation-triangle text-2xl text-white"></i>
            </div>
            <h3 class="font-bold text-lg mb-2 text-surface-800 dark:text-surface-100">Czerwone Flagi</h3>
            <p class="text-surface-500">
              Wykrywamy ryzykowne czynniki: hałas, bliskość dróg, brak zieleni
            </p>
          </div>
          
          <div class="group bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-surface-100 dark:border-surface-700 hover:-translate-y-1">
            <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center shadow-lg mb-4 group-hover:scale-110 transition-transform">
              <i class="pi pi-chart-bar text-2xl text-white"></i>
            </div>
            <h3 class="font-bold text-lg mb-2 text-surface-800 dark:text-surface-100">Cena vs Rynek</h3>
            <p class="text-surface-500">
              Porównujemy Twoją cenę ze średnią dzielnicy: tanio / ok / drogo
            </p>
          </div>
          
          <div class="group bg-white dark:bg-surface-800 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-surface-100 dark:border-surface-700 hover:-translate-y-1">
            <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-lg mb-4 group-hover:scale-110 transition-transform">
              <i class="pi pi-check-circle text-2xl text-white"></i>
            </div>
            <h3 class="font-bold text-lg mb-2 text-surface-800 dark:text-surface-100">Werdykt Zakupu</h3>
            <p class="text-surface-500">
              Jasna rekomendacja: POLECAM / UWAŻAJ / ODRADZAM z uzasadnieniem
            </p>
          </div>
        </div>
        
        <!-- Recent analyses - Modern Table -->
        <div v-if="recentAnalyses.length > 0" class="bg-white/80 dark:bg-surface-800/80 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-white/20">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center">
              <i class="pi pi-history text-white"></i>
            </div>
            <h2 class="text-xl font-bold text-surface-800 dark:text-surface-100">Ostatnie analizy</h2>
          </div>
          
          <div class="space-y-3">
            <div 
              v-for="item in recentAnalyses.slice(0, 5)" 
              :key="item.id"
              @click="openHistoryItem(item)"
              class="group flex items-center gap-4 p-4 bg-surface-50 dark:bg-surface-700/50 rounded-xl cursor-pointer hover:bg-surface-100 dark:hover:bg-surface-700 transition-all hover:shadow-md"
            >
              <!-- Score Badge -->
              <div 
                class="w-12 h-12 rounded-xl flex items-center justify-center font-bold text-white shadow-md"
                :style="{ background: getScoreColor(item.neighborhood_score) }"
              >
                {{ item.neighborhood_score !== null ? Math.round(item.neighborhood_score) : '?' }}
              </div>
              
              <!-- Info -->
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-surface-800 dark:text-surface-100 truncate">
                  {{ item.title || item.location || 'Bez tytułu' }}
                </p>
                <div class="flex items-center gap-3 text-sm text-surface-500">
                  <span v-if="item.price">{{ formatPrice(item.price) }}</span>
                  <span v-if="item.area_sqm">{{ item.area_sqm }} m²</span>
                  <span v-if="item.rooms">{{ item.rooms }} pok.</span>
                </div>
              </div>
              
              <!-- Date -->
              <div class="text-sm text-surface-400 hidden md:block">
                {{ formatDate(item.created_at) }}
              </div>
              
              <i class="pi pi-chevron-right text-surface-300 group-hover:text-primary-500 transition-colors"></i>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Footer -->
    <div class="text-center p-6 text-sm text-surface-400">
      <p class="font-medium text-primary-500">loktis.pl</p>
      <p class="mt-1">Dane pochodzą z OpenStreetMap • Analiza ma charakter poglądowy</p>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
  overflow: hidden;
}

.slide-enter-to,
.slide-leave-from {
  max-height: 200px;
}

@keyframes blob {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(20px, -30px) scale(1.1); }
  50% { transform: translate(-20px, 20px) scale(0.9); }
  75% { transform: translate(30px, 10px) scale(1.05); }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.animate-shimmer {
  animation: shimmer 1.5s infinite;
}
</style>
