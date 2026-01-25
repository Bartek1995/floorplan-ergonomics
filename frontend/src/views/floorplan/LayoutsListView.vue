<!-- src/views/floorplan/LayoutsListView.vue -->
<template>
    <div class="flex flex-col gap-4">
        <Toolbar>
            <template #start>
                <div class="flex flex-col gap-1">
                    <span>Layouty</span>
                    <span>Lista rzutow powiazanych z mieszkaniami</span>
                </div>
            </template>
            <template #end>
                <div class="flex gap-2">
                    <InputText v-model="searchQuery" placeholder="Szukaj po ID lub mieszkaniu" />
                    <Button icon="pi pi-refresh" @click="refreshLayouts" :loading="isLoading" />
                    <Button icon="pi pi-plus" label="Nowy layout" @click="showNewLayoutDialog = true" />
                </div>
            </template>
        </Toolbar>

        <DataTable :value="filteredLayouts" dataKey="id" :loading="isLoading">
            <Column field="id" header="ID" />
            <Column header="Mieszkanie">
                <template #body="{ data }">
                    <Tag v-if="data.flat" :value="`#${data.flat}`" severity="info" />
                    <Tag v-else value="Brak" severity="warning" />
                </template>
            </Column>
            <Column header="Skala">
                <template #body="{ data }">
                    <span>{{ formatScale(data.scale_cm_per_px) }}</span>
                </template>
            </Column>
            <Column header="Sciany">
                <template #body="{ data }">
                    <span>{{ getWallCount(data) }}</span>
                </template>
            </Column>
            <Column header="Punkty">
                <template #body="{ data }">
                    <span>{{ getPointCount(data) }}</span>
                </template>
            </Column>
            <Column header="Akcje">
                <template #body="{ data }">
                    <div class="flex gap-2">
                        <Button
                            icon="pi pi-eye"
                            label="Szczegoly"
                            size="small"
                            @click="openDetails(data)"
                        />
                        <Button
                            icon="pi pi-pencil"
                            label="Edytor"
                            size="small"
                            severity="info"
                            :disabled="!data.flat"
                            @click="openEditor(data)"
                        />
                        <Button
                            icon="pi pi-trash"
                            size="small"
                            severity="danger"
                            text
                            @click="confirmDeleteLayout(data)"
                        />
                    </div>
                </template>
            </Column>
            <template #empty>
                <Message severity="info">Brak layoutow</Message>
            </template>
        </DataTable>

        <Message v-if="error" severity="error" @close="clearError">
            {{ error }}
        </Message>

        <Dialog v-model:visible="showNewLayoutDialog" header="Nowy layout" modal>
            <div class="flex flex-col gap-3">
                <div class="flex flex-col gap-2">
                    <label for="layout-flat">Mieszkanie (opcjonalnie)</label>
                    <Dropdown
                        id="layout-flat"
                        v-model="selectedFlatId"
                        :options="flatOptions"
                        optionLabel="label"
                        optionValue="value"
                        placeholder="Wybierz mieszkanie"
                        showClear
                    />
                </div>
                <div class="flex gap-2">
                    <Button
                        label="Anuluj"
                        severity="secondary"
                        @click="showNewLayoutDialog = false"
                    />
                    <Button label="Utworz" @click="createNewLayout" :loading="isLoading" />
                </div>
            </div>
        </Dialog>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useLayoutStore } from '@/stores/layoutStore';
import { useRouter } from 'vue-router';
import { useConfirm } from 'primevue/useconfirm';
import Button from 'primevue/button';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Message from 'primevue/message';
import Tag from 'primevue/tag';
import Toolbar from 'primevue/toolbar';
import { flatApi, type Flat } from '@/api/flatApi';
import type { Layout } from '@/api/layoutApi';

const router = useRouter();
const confirm = useConfirm();
const layoutStore = useLayoutStore();

const searchQuery = ref('');
const showNewLayoutDialog = ref(false);
const selectedFlatId = ref<number | null>(null);
const flatOptions = ref<Array<{ label: string; value: number }>>([]);

const { layouts, isLoading, error } = layoutStore;

const filteredLayouts = computed(() => {
    const query = searchQuery.value.trim().toLowerCase();
    const list = Array.isArray(layouts.value) ? layouts.value : [];
    if (!query) {
        return list;
    }
    return list.filter((layout: Layout) => {
        const idText = String(layout.id);
        const flatText = layout.flat ? String(layout.flat) : '';
        return idText.includes(query) || flatText.includes(query);
    });
});

onMounted(() => {
    refreshLayouts();
    loadFlats();
});

const loadFlats = async () => {
    try {
        const response = await flatApi.listFlats();
        const data = Array.isArray(response.data)
            ? response.data
            : response.data.results || [];
        flatOptions.value = data.map((flat: Flat) => ({
            label: flat.name,
            value: flat.id
        }));
    } catch (err) {
        console.error('Flats load error:', err);
    }
};

const refreshLayouts = async () => {
    await layoutStore.fetchLayouts();
};

const openDetails = (layout: Layout) => {
    router.push({
        name: 'layout-detail',
        params: { id: layout.id }
    });
};

const openEditor = (layout: Layout) => {
    if (!layout.flat) return;
    router.push({
        name: 'floorplan-editor',
        params: { id: layout.flat }
    });
};

const createNewLayout = async () => {
    try {
        const created = await layoutStore.createLayout(selectedFlatId.value ?? null);
        showNewLayoutDialog.value = false;
        selectedFlatId.value = null;
        router.push({ name: 'layout-detail', params: { id: created.id } });
    } catch (err) {
        console.error(err);
    }
};

const confirmDeleteLayout = (layout: Layout) => {
    confirm.require({
        message: `Na pewno chcesz usunac layout #${layout.id}?`,
        header: 'Potwierdzenie',
        icon: 'pi pi-exclamation-triangle',
        accept: () => deleteLayout(layout.id),
        reject: () => {}
    });
};

const deleteLayout = async (id: number) => {
    await layoutStore.deleteLayout(id);
};

const getWallCount = (layout: Layout) => {
    return layout.layout_data.walls?.length || 0;
};

const getPointCount = (layout: Layout) => {
    return layout.layout_data.points?.length || 0;
};

const formatScale = (scale: number | null) => {
    if (scale === null || scale === undefined) return '-';
    return scale.toFixed(3);
};

const clearError = () => {
    layoutStore.clearError();
};
</script>
