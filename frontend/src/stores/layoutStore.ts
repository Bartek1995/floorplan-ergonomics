// src/stores/layoutStore.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { layoutApi, type Layout, type LayoutData } from '@/api/layoutApi';

export const useLayoutStore = defineStore('layout', () => {
    const layouts = ref<Layout[]>([]);
    const currentLayout = ref<Layout | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);

    // Edytor state
    const editMode = ref<'select' | 'wall' | 'object' | 'door'>('select');
    const scale = ref(1);
    const showGrid = ref(true);
    const gridSize = ref(50); // 50px na canvasie = 5cm w rzeczywistości

    // Gettery
    const currentLayoutId = computed(() => currentLayout.value?.id);
    const isLoading = computed(() => loading.value);
    const hasError = computed(() => !!error.value);

    // Actions
    const fetchLayouts = async () => {
        loading.value = true;
        error.value = null;
        try {
            const response = await layoutApi.listLayouts();
            layouts.value = Array.isArray(response.data) ? response.data : [];
        } catch (err) {
            const message = err instanceof Error ? err.message : String(err);
            error.value = `Błąd przy pobieraniu planów: ${message}`;
            console.error(err);
            layouts.value = [];
        } finally {
            loading.value = false;
        }
    };

    const fetchLayout = async (id: number) => {
        loading.value = true;
        error.value = null;
        try {
            const response = await layoutApi.getLayout(id);
            currentLayout.value = response.data;
        } catch (err) {
            const message = err instanceof Error ? err.message : String(err);
            error.value = `Błąd przy pobieraniu planu: ${message}`;
            console.error(err);
        } finally {
            loading.value = false;
        }
    };

    const createLayout = async (name: string) => {
        loading.value = true;
        error.value = null;
        try {
            const response = await layoutApi.createLayout({
                name,
                layout_data: {
                    walls: [],
                    objects: [],
                    doors: []
                }
            });
            layouts.value.push(response.data);
            currentLayout.value = response.data;
            return response.data;
        } catch (err) {
            const message = err instanceof Error ? err.message : String(err);
            error.value = `Błąd przy tworzeniu planu: ${message}`;
            console.error(err);
            throw err;
        } finally {
            loading.value = false;
        }
    };

    const saveLayout = async (layoutData: LayoutData) => {
        if (!currentLayout.value) return;
        loading.value = true;
        error.value = null;
        try {
            const response = await layoutApi.updateLayout(currentLayout.value.id, {
                layout_data: layoutData
            });
            currentLayout.value = response.data;
            const index = layouts.value.findIndex(l => l.id === response.data.id);
            if (index >= 0) {
                layouts.value[index] = response.data;
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : String(err);
            error.value = `Błąd przy zapisywaniu planu: ${message}`;
            console.error(err);
            throw err;
        } finally {
            loading.value = false;
        }
    };

    const updateLayoutName = async (id: number, name: string) => {
        loading.value = true;
        error.value = null;
        try {
            const response = await layoutApi.updateLayout(id, { name });
            const index = layouts.value.findIndex(l => l.id === id);
            if (index >= 0) {
                layouts.value[index] = response.data;
            }
            if (currentLayout.value?.id === id) {
                currentLayout.value = response.data;
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : String(err);
            error.value = `Błąd przy aktualizacji nazwy: ${message}`;
            console.error(err);
        } finally {
            loading.value = false;
        }
    };

    const deleteLayout = async (id: number) => {
        loading.value = true;
        error.value = null;
        try {
            await layoutApi.deleteLayout(id);
            layouts.value = layouts.value.filter(l => l.id !== id);
            if (currentLayout.value?.id === id) {
                currentLayout.value = null;
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : String(err);
            error.value = `Błąd przy usuwaniu planu: ${message}`;
            console.error(err);
            throw err;
        } finally {
            loading.value = false;
        }
    };

    const selectLayout = (layout: Layout) => {
        currentLayout.value = layout;
    };

    const clearError = () => {
        error.value = null;
    };

    return {
        // State
        layouts,
        currentLayout,
        loading,
        error,
        editMode,
        scale,
        showGrid,
        gridSize,
        // Gettery
        currentLayoutId,
        isLoading,
        hasError,
        // Actions
        fetchLayouts,
        fetchLayout,
        createLayout,
        saveLayout,
        updateLayoutName,
        deleteLayout,
        selectLayout,
        clearError
    };
});
