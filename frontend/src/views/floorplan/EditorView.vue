<!-- src/views/floorplan/EditorView.vue -->
<template>
    <div class="flex flex-col h-full gap-4 p-4">
        <!-- Toolbar -->
        <div class="flex gap-2 items-center bg-surface-card rounded-lg p-3 shadow-sm">
            <Button
                icon="pi pi-home"
                severity="secondary"
                text
                rounded
                @click="$router.push({ name: 'layouts-list' })"
                v-tooltip="'Powrót do listy planów'"
            />
            <Divider layout="vertical" />

            <span class="text-sm font-semibold" v-if="currentLayout">
                {{ currentLayout.name }}
            </span>
            <span class="text-sm text-surface-500" v-else>Nowy plan</span>

            <div class="grow" />

            <InputGroup class="w-64">
                <InputText
                    v-model="layoutName"
                    placeholder="Nazwa planu..."
                    @blur="saveName"
                />
            </InputGroup>

            <Button
                icon="pi pi-save"
                severity="success"
                rounded
                @click="saveLayout"
                :loading="isLoading"
                v-tooltip="'Zapisz plan (Ctrl+S)'"
            />

            <Button
                icon="pi pi-download"
                severity="info"
                rounded
                @click="exportLayout"
                v-tooltip="'Eksportuj plan'"
            />

            <Button
                icon="pi pi-trash"
                severity="danger"
                rounded
                @click="confirmDelete"
                v-if="currentLayout"
                v-tooltip="'Usuń plan'"
            />
        </div>

        <!-- Editor Canvas -->
        <div class="grow bg-surface-ground rounded-lg overflow-hidden shadow-sm border border-surface-border">
            <div class="w-full h-full flex items-center justify-center bg-surface-50">
                <div class="text-center">
                    <i class="pi pi-pencil text-6xl text-surface-400 mb-4" />
                    <p class="text-surface-600">Edytor planu piętra (w trakcie implementacji)</p>
                    <p class="text-surface-500 text-sm mt-2">Tutaj będzie kanvas z edytorem</p>
                </div>
            </div>
        </div>

        <!-- Info -->
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
import Divider from 'primevue/divider';
import InputGroup from 'primevue/inputgroup';
import InputText from 'primevue/inputtext';
import Message from 'primevue/message';

const router = useRouter();
const route = useRoute();
const confirm = useConfirm();
const layoutStore = useLayoutStore();

const layoutName = ref('');

const currentLayout = computed(() => layoutStore.currentLayout);
const isLoading = computed(() => layoutStore.isLoading);
const error = computed(() => layoutStore.error);

onMounted(async () => {
    const layoutId = route.query.id;
    if (layoutId) {
        await layoutStore.fetchLayout(Number(layoutId));
        if (currentLayout.value) {
            layoutName.value = currentLayout.value.name;
        }
    }
});

const saveName = async () => {
    if (currentLayout.value && layoutName.value !== currentLayout.value.name) {
        await layoutStore.updateLayoutName(currentLayout.value.id, layoutName.value);
    }
};

const saveLayout = async () => {
    if (currentLayout.value) {
        await layoutStore.saveLayout(currentLayout.value.layout_data);
    }
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
        await router.push({ name: 'layouts-list' });
    }
};

const clearError = () => {
    layoutStore.clearError();
};
</script>

<style scoped></style>
