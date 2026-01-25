<!-- src/views/floorplan/EditorView.vue -->
<template>
    <div class="flex flex-col gap-4">
        <Toolbar>
            <template #start>
                <div class="flex flex-col gap-1">
                    <span>Edytor layoutu</span>
                    <span v-if="flat">Mieszkanie: {{ flat.name }}</span>
                </div>
            </template>
            <template #end>
                <div class="flex gap-2">
                    <Button icon="pi pi-arrow-left" label="Powrot" @click="goBack" />
                    <Button
                        v-if="flat"
                        icon="pi pi-building"
                        label="Mieszkanie"
                        @click="openFlat"
                    />
                    <Button icon="pi pi-refresh" @click="loadFlat" :loading="isLoading" />
                </div>
            </template>
        </Toolbar>

        <ProgressSpinner v-if="isLoading" />

        <Splitter v-else>
            <SplitterPanel :size="70">
                <Card>
                    <template #title>Podglad rzutu</template>
                    <template #content>
                        <Image
                            v-if="layout?.image"
                            :src="layout.image"
                            :alt="flat?.name || 'Layout'"
                            preview
                        />
                        <Message v-else severity="info">
                            Brak rzutu - zaimportuj plik, aby zaczac.
                        </Message>
                    </template>
                </Card>
            </SplitterPanel>
            <SplitterPanel :size="30">
                <div class="flex flex-col gap-4">
                    <Card>
                        <template #title>Import rzutu</template>
                        <template #content>
                            <LayoutImportForm
                                v-if="flat"
                                :flatId="flat.id"
                                :initialScale="layout?.scale_cm_per_px ?? null"
                                :showCancel="false"
                                @uploaded="handleLayoutUploaded"
                            />
                            <Message v-else severity="warn">
                                Brak danych mieszkania.
                            </Message>
                        </template>
                    </Card>

                    <Card>
                        <template #title>Podsumowanie</template>
                        <template #content>
                            <DataTable :value="summaryRows" dataKey="label">
                                <Column field="label" header="Pole" />
                                <Column field="value" header="Wartosc" />
                            </DataTable>
                        </template>
                    </Card>
                </div>
            </SplitterPanel>
        </Splitter>

        <Message v-if="error" severity="error">
            {{ error }}
        </Message>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Image from 'primevue/image';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import Splitter from 'primevue/splitter';
import SplitterPanel from 'primevue/splitterpanel';
import Toolbar from 'primevue/toolbar';
import { flatApi, type Flat, type Layout } from '@/api/flatApi';
import LayoutImportForm from '@/components/Layouts/LayoutImportForm.vue';

const router = useRouter();
const route = useRoute();

const flat = ref<Flat | null>(null);
const isLoading = ref(false);
const error = ref('');

const flatId = computed(() => Number(route.params.id));
const layout = computed(() => flat.value?.layout ?? null);

const loadFlat = async () => {
    if (!flatId.value) return;
    isLoading.value = true;
    error.value = '';
    try {
        const response = await flatApi.getFlat(flatId.value);
        flat.value = response.data;
    } catch (err) {
        console.error('Flat load error:', err);
        error.value = 'Nie udalo sie pobrac danych mieszkania.';
    } finally {
        isLoading.value = false;
    }
};

const summaryRows = computed(() => {
    return [
        { label: 'Status', value: layout.value ? 'Dodany' : 'Brak' },
        { label: 'Skala (cm/px)', value: formatScale(layout.value?.scale_cm_per_px ?? null) },
        { label: 'Sciany', value: String(layout.value?.layout_data.walls?.length || 0) },
        { label: 'Punkty', value: String(layout.value?.layout_data.points?.length || 0) }
    ];
});

const formatScale = (scale: number | null) => {
    if (scale === null || scale === undefined) return '-';
    return scale.toFixed(3);
};

const handleLayoutUploaded = (newLayout: Layout) => {
    if (flat.value) {
        flat.value.layout = newLayout;
    }
};

const goBack = () => {
    if (flatId.value) {
        router.push({ name: 'flat-detail', params: { id: flatId.value } });
        return;
    }
    router.push({ name: 'flats-list' });
};

const openFlat = () => {
    if (!flatId.value) return;
    router.push({ name: 'flat-detail', params: { id: flatId.value } });
};

onMounted(loadFlat);
</script>
