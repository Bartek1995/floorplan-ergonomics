<!-- src/views/floorplan/LayoutDetailView.vue -->
<template>
    <div class="flex flex-col h-full gap-4 p-4">
        <ProgressSpinner v-if="isLoading" class="mx-auto" />

        <div v-else-if="currentLayout" class="flex flex-col h-full gap-4">
            <!-- Header -->
            <div class="flex gap-2 items-center justify-between bg-surface-card rounded-lg p-3 shadow-sm">
                <div class="flex items-center gap-3">
                    <Button
                        icon="pi pi-arrow-left"
                        severity="secondary"
                        text
                        rounded
                        @click="$router.back()"
                    />
                    <div>
                        <h1 class="text-xl font-bold">{{ currentLayout.name }}</h1>
                        <p class="text-sm text-surface-500">
                            Ostatnia edycja: {{ formatDate(currentLayout.updated_at) }}
                        </p>
                    </div>
                </div>

                <Button
                    icon="pi pi-pencil"
                    label="Edytuj"
                    @click="openEditor"
                    severity="info"
                />
            </div>

            <!-- Content -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 grow">
                <!-- Main Info -->
                <div class="lg:col-span-2">
                    <Card class="h-full">
                        <template #title>
                            <i class="pi pi-info-circle mr-2" />
                            Informacje o planie
                        </template>
                        <template #content>
                            <div class="space-y-4">
                                <div>
                                    <label class="block text-sm font-semibold mb-2">ID planu</label>
                                    <InputText :value="currentLayout.id" disabled class="w-full" />
                                </div>

                                <div>
                                    <label class="block text-sm font-semibold mb-2">Nazwa</label>
                                    <InputText
                                        v-model="editedName"
                                        @blur="updateName"
                                        class="w-full"
                                    />
                                </div>

                                <div>
                                    <label class="block text-sm font-semibold mb-2">Data utworzenia</label>
                                    <InputText :value="formatDate(currentLayout.created_at)" disabled class="w-full" />
                                </div>

                                <Divider />

                                <div class="grid grid-cols-2 gap-4">
                                    <div class="bg-primary-50 rounded-lg p-4">
                                        <p class="text-sm text-surface-600">Ściany</p>
                                        <p class="text-3xl font-bold text-primary">
                                            {{ getWallCount(currentLayout) }}
                                        </p>
                                    </div>
                                    <div class="bg-info-50 rounded-lg p-4">
                                        <p class="text-sm text-surface-600">Obiekty</p>
                                        <p class="text-3xl font-bold text-info">
                                            {{ getObjectCount(currentLayout) }}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </Card>
                </div>

                <!-- Actions -->
                <div class="space-y-4">
                    <Card>
                        <template #title>
                            <i class="pi pi-cog mr-2" />
                            Akcje
                        </template>
                        <template #content>
                            <div class="flex flex-col gap-2">
                                <Button
                                    icon="pi pi-download"
                                    label="Eksportuj JSON"
                                    @click="exportLayout"
                                    severity="info"
                                    text
                                />
                                <Button
                                    icon="pi pi-copy"
                                    label="Duplikuj"
                                    @click="duplicateLayout"
                                    severity="warning"
                                    text
                                    :loading="isLoading"
                                />
                                <Divider />
                                <Button
                                    icon="pi pi-trash"
                                    label="Usuń"
                                    @click="confirmDelete"
                                    severity="danger"
                                    text
                                />
                            </div>
                        </template>
                    </Card>

                    <Card>
                        <template #title>
                            <i class="pi pi-list mr-2" />
                            Szczegóły
                        </template>
                        <template #content>
                            <div class="space-y-2 text-sm">
                                <div class="flex justify-between">
                                    <span class="text-surface-600">Rozmiar JSON:</span>
                                    <span class="font-semibold">{{ getJsonSize(currentLayout) }}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-surface-600">Liczba pól:</span>
                                    <span class="font-semibold">{{ Object.keys(currentLayout.layout_data).length }}</span>
                                </div>
                            </div>
                        </template>
                    </Card>
                </div>
            </div>
        </div>

        <!-- Error -->
        <Message v-if="error" severity="error" @close="clearError" class="w-full">
            {{ error }}
        </Message>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useLayoutStore } from '@/stores/layoutStore';
import { useRouter, useRoute } from 'vue-router';
import { useConfirm } from 'primevue/useconfirm';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Divider from 'primevue/divider';
import InputText from 'primevue/inputtext';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import type { Layout } from '@/api/layoutApi';

const router = useRouter();
const route = useRoute();
const confirm = useConfirm();
const layoutStore = useLayoutStore();

const editedName = ref('');

const currentLayout = computed(() => layoutStore.currentLayout);
const isLoading = computed(() => layoutStore.isLoading);
const error = computed(() => layoutStore.error);

onMounted(async () => {
    const layoutId = Number(route.params.id);
    if (layoutId) {
        await layoutStore.fetchLayout(layoutId);
        if (currentLayout.value) {
            editedName.value = currentLayout.value.name;
        }
    }
});

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

const getObjectCount = (layout: Layout) => {
    const objects = (layout.layout_data.objects?.length || 0) + (layout.layout_data.doors?.length || 0);
    return objects;
};

const getJsonSize = (layout: Layout) => {
    const size = JSON.stringify(layout.layout_data).length;
    return size > 1024 ? `${(size / 1024).toFixed(2)} KB` : `${size} B`;
};

const updateName = async () => {
    if (currentLayout.value && editedName.value !== currentLayout.value.name) {
        await layoutStore.updateLayoutName(currentLayout.value.id, editedName.value);
    }
};

const openEditor = () => {
    router.push({
        name: 'floorplan-editor',
        query: { id: currentLayout.value?.id }
    });
};

const exportLayout = () => {
    if (currentLayout.value) {
        const data = JSON.stringify(currentLayout.value, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${currentLayout.value.name}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
};

const duplicateLayout = async () => {
    if (currentLayout.value) {
        try {
            const newName = `${currentLayout.value.name} (kopia)`;
            const layout = await layoutStore.createLayout(newName);
            router.push({
                name: 'layout-detail',
                params: { id: layout.id }
            });
        } catch (err) {
            console.error(err);
        }
    }
};

const confirmDelete = () => {
    confirm.require({
        message: `Na pewno chcesz usunąć plan "${currentLayout.value?.name}"?`,
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

<style scoped></style>
