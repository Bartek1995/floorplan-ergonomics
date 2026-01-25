<!-- src/views/floorplan/LayoutDetailView.vue -->
<template>
    <div class="flex flex-col gap-4">
        <Toolbar>
            <template #start>
                <div class="flex flex-col gap-1">
                    <span>Layout #{{ currentLayout?.id ?? '-' }}</span>
                    <span v-if="currentLayout?.flat">Mieszkanie #{{ currentLayout.flat }}</span>
                </div>
            </template>
            <template #end>
                <div class="flex gap-2">
                    <Button icon="pi pi-arrow-left" label="Powrot" @click="goBack" />
                    <Button
                        v-if="currentLayout?.flat"
                        icon="pi pi-building"
                        label="Mieszkanie"
                        @click="openFlat"
                    />
                    <Button
                        v-if="currentLayout?.flat"
                        icon="pi pi-pencil"
                        label="Edytor"
                        severity="info"
                        @click="openEditor"
                    />
                    <Button
                        icon="pi pi-trash"
                        severity="danger"
                        @click="confirmDelete"
                    />
                </div>
            </template>
        </Toolbar>

        <ProgressSpinner v-if="isLoading" />

        <div v-else-if="currentLayout" class="flex flex-col gap-4">
            <Card>
                <template #title>Informacje</template>
                <template #content>
                    <DataTable :value="detailsRows" dataKey="label">
                        <Column field="label" header="Pole" />
                        <Column field="value" header="Wartosc" />
                    </DataTable>
                </template>
            </Card>

            <Card>
                <template #title>Import rzutu</template>
                <template #content>
                    <LayoutImportForm
                        v-if="currentLayout.flat"
                        :flatId="currentLayout.flat"
                        :initialScale="currentLayout.scale_cm_per_px ?? null"
                        :showCancel="false"
                        @uploaded="handleLayoutUploaded"
                    />
                    <Message v-else severity="warn">
                        Layout bez powiazania z mieszkaniem - import nie jest dostepny.
                    </Message>
                </template>
            </Card>
        </div>

        <Message v-if="error" severity="error" @close="clearError">
            {{ error }}
        </Message>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useLayoutStore } from '@/stores/layoutStore';
import { useRouter, useRoute } from 'vue-router';
import { useConfirm } from 'primevue/useconfirm';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import Toolbar from 'primevue/toolbar';
import LayoutImportForm from '@/components/Layouts/LayoutImportForm.vue';
import type { Layout } from '@/api/layoutApi';

const router = useRouter();
const route = useRoute();
const confirm = useConfirm();
const layoutStore = useLayoutStore();

const currentLayout = computed(() => layoutStore.currentLayout);
const isLoading = computed(() => layoutStore.isLoading);
const error = computed(() => layoutStore.error);

onMounted(async () => {
    const layoutId = Number(route.params.id);
    if (layoutId) {
        await layoutStore.fetchLayout(layoutId);
    }
});

const detailsRows = computed(() => {
    if (!currentLayout.value) return [];
    return [
        { label: 'ID', value: String(currentLayout.value.id) },
        { label: 'Mieszkanie', value: currentLayout.value.flat ? `#${currentLayout.value.flat}` : 'Brak' },
        { label: 'Skala (cm/px)', value: formatScale(currentLayout.value.scale_cm_per_px) },
        { label: 'Sciany', value: String(getWallCount(currentLayout.value)) },
        { label: 'Punkty', value: String(getPointCount(currentLayout.value)) },
        { label: 'Utworzono', value: formatDate(currentLayout.value.created_at) },
        { label: 'Zaktualizowano', value: formatDate(currentLayout.value.updated_at) }
    ];
});

const formatScale = (scale: number | null) => {
    if (scale === null || scale === undefined) return '-';
    return scale.toFixed(3);
};

const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pl-PL', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

const getWallCount = (layout: Layout) => {
    return layout.layout_data.walls?.length || 0;
};

const getPointCount = (layout: Layout) => {
    return layout.layout_data.points?.length || 0;
};

const goBack = () => {
    router.push({ name: 'layouts-list' });
};

const openFlat = () => {
    if (!currentLayout.value?.flat) return;
    router.push({ name: 'flat-detail', params: { id: currentLayout.value.flat } });
};

const openEditor = () => {
    if (!currentLayout.value?.flat) return;
    router.push({ name: 'floorplan-editor', params: { id: currentLayout.value.flat } });
};

const handleLayoutUploaded = (layout: Layout) => {
    layoutStore.selectLayout(layout);
};

const confirmDelete = () => {
    confirm.require({
        message: `Na pewno chcesz usunac layout #${currentLayout.value?.id}?`,
        header: 'Potwierdzenie',
        icon: 'pi pi-exclamation-triangle',
        accept: deleteLayout,
        reject: () => {}
    });
};

const deleteLayout = async () => {
    if (currentLayout.value) {
        await layoutStore.deleteLayout(currentLayout.value.id);
        router.push({ name: 'layouts-list' });
    }
};

const clearError = () => {
    layoutStore.clearError();
};
</script>
