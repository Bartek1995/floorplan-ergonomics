<!-- src/views/floorplan/LayoutsListView.vue -->
<template>
    <div class="flex flex-col h-full gap-4 p-4">
        <!-- Header -->
        <div class="flex gap-2 items-center justify-between bg-surface-card rounded-lg p-3 shadow-sm">
            <div class="flex items-center gap-2">
                <i class="pi pi-building text-2xl text-primary" />
                <div>
                    <h1 class="text-xl font-bold">Plany pięter</h1>
                    <p class="text-sm text-surface-500">Zarządzaj planami pięter</p>
                </div>
            </div>

            <Button
                icon="pi pi-plus"
                label="Nowy plan"
                @click="showNewLayoutDialog = true"
                severity="success"
            />
        </div>

        <!-- Search & Filters -->
        <div class="flex gap-2">
            <InputGroup class="grow">
                <InputGroupAddon>
                    <i class="pi pi-search" />
                </InputGroupAddon>
                <InputText v-model="searchQuery" placeholder="Szukaj planu..." />
            </InputGroup>
            <Button
                icon="pi pi-refresh"
                @click="refreshLayouts"
                severity="secondary"
                :loading="isLoading"
            />
        </div>

        <!-- Layouts Grid -->
        <div class="grow overflow-auto">
            <ProgressSpinner v-if="isLoading && layouts.length === 0" class="mx-auto mt-8" />

            <div v-else-if="filteredLayouts.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <Card v-for="layout in filteredLayouts" :key="layout.id" class="cursor-pointer hover:shadow-lg transition-shadow">
                    <template #content>
                        <div class="flex flex-col gap-3">
                            <!-- Thumbnail -->
                            <div class="bg-surface-100 rounded h-40 flex items-center justify-center">
                                <i class="pi pi-image text-3xl text-surface-400" />
                            </div>

                            <!-- Name -->
                            <div>
                                <h3 class="font-semibold truncate">{{ layout.name }}</h3>
                                <p class="text-sm text-surface-500">
                                    {{ new Date(layout.updated_at).toLocaleDateString('pl-PL') }}
                                </p>
                            </div>

                            <!-- Info -->
                            <div class="grid grid-cols-2 gap-2 text-sm">
                                <div class="bg-surface-50 rounded p-2">
                                    <p class="text-surface-600">ID: {{ layout.id }}</p>
                                </div>
                                <div class="bg-surface-50 rounded p-2">
                                    <p class="text-surface-600">Obiekty: {{ getObjectCount(layout) }}</p>
                                </div>
                            </div>

                            <!-- Actions -->
                            <div class="flex gap-2">
                                <Button
                                    icon="pi pi-pencil"
                                    label="Edytuj"
                                    class="grow"
                                    @click="openEditor(layout)"
                                    severity="info"
                                    size="small"
                                />
                                <Button
                                    icon="pi pi-trash"
                                    @click="confirmDeleteLayout(layout)"
                                    severity="danger"
                                    size="small"
                                    text
                                />
                            </div>
                        </div>
                    </template>
                </Card>
            </div>

            <!-- Empty State -->
            <div v-else class="flex flex-col items-center justify-center h-64">
                <i class="pi pi-inbox text-5xl text-surface-400 mb-4" />
                <p class="text-surface-600 font-semibold">Brak planów</p>
                <p class="text-sm text-surface-500">Utwórz nowy plan aby zacząć</p>
            </div>
        </div>

        <!-- Error -->
        <Message v-if="error" severity="error" @close="clearError" class="w-full">
            {{ error }}
        </Message>

        <!-- New Layout Dialog -->
        <Dialog v-model:visible="showNewLayoutDialog" header="Nowy plan piętra" modal>
            <div class="flex flex-col gap-4">
                <div>
                    <label class="block text-sm font-semibold mb-2">Nazwa planu</label>
                    <InputText
                        v-model="newLayoutName"
                        placeholder="np. Salon, Sypialnia..."
                        class="w-full"
                        @keyup.enter="createNewLayout"
                    />
                </div>
                <div class="flex gap-2 justify-end">
                    <Button
                        label="Anuluj"
                        @click="showNewLayoutDialog = false"
                        severity="secondary"
                    />
                    <Button
                        label="Utwórz"
                        @click="createNewLayout"
                        :loading="isLoading"
                    />
                </div>
            </div>
        </Dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useLayoutStore } from '@/stores/layoutStore';
import { useRouter } from 'vue-router';
import { useConfirm } from 'primevue/useconfirm';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import InputGroup from 'primevue/inputgroup';
import InputGroupAddon from 'primevue/inputgroupaddon';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import type { Layout } from '@/api/layoutApi';

const router = useRouter();
const confirm = useConfirm();
const layoutStore = useLayoutStore();

const searchQuery = ref('');
const showNewLayoutDialog = ref(false);
const newLayoutName = ref('');

// Rozpakowuj store aby dostać reaktywne wartości
const { layouts, isLoading, error } = layoutStore;

const filteredLayouts = computed(() => {
    const query = searchQuery.value.toLowerCase();
    if (!Array.isArray(layouts)) {
        return [];
    }
    return layouts.filter((layout: Layout) =>
        layout.name.toLowerCase().includes(query)
    );
});

onMounted(() => {
    refreshLayouts();
});

const refreshLayouts = async () => {
    await layoutStore.fetchLayouts();
};

const openEditor = (layout: Layout) => {
    layoutStore.selectLayout(layout);
    router.push({
        name: 'floorplan-editor',
        query: { id: layout.id }
    });
};

const createNewLayout = async () => {
    if (!newLayoutName.value.trim()) return;
    try {
        await layoutStore.createLayout(newLayoutName.value);
        showNewLayoutDialog.value = false;
        newLayoutName.value = '';
    } catch (err) {
        console.error(err);
    }
};

const confirmDeleteLayout = (layout: Layout) => {
    confirm.require({
        message: `Na pewno chcesz usunąć plan "${layout.name}"?`,
        header: 'Potwierdzenie',
        icon: 'pi pi-exclamation-triangle',
        accept: () => deleteLayout(layout.id),
        reject: () => {}
    });
};

const deleteLayout = async (id: number) => {
    await layoutStore.deleteLayout(id);
};

const getObjectCount = (layout: Layout) => {
    const data = layout.layout_data;
    const count = (data.objects?.length || 0) + (data.doors?.length || 0);
    return count;
};

const clearError = () => {
    layoutStore.clearError();
};
</script>

<style scoped></style>
