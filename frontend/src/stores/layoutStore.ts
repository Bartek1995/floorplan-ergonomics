// src/stores/layoutStore.ts
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { layoutApi, type Layout, type LayoutData } from '@/api/layoutApi';

export const useLayoutStore = defineStore('layout', () => {
    const layouts = ref<Layout[]>([]);
    const currentLayout = ref<Layout | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);

    // Edytor state
    const editMode = ref<'select' | 'wall' | 'point'>('select');
    const scale = ref(1);
    const showGrid = ref(true);
    const gridSize = ref(50); // 50px na canvasie = 5cm w rzeczywistosci

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
            const data = Array.isArray(response.data)
                ? response.data
                : response.data?.results || [];
            layouts.value = data;
        } catch (err) {
            const message = err instanceof Error ? err.message : String(err);
            error.value = `Blad przy pobieraniu layoutow: ${message}`;
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
            error.value = `Blad przy pobieraniu layoutu: ${message}`;
            console.error(err);
        } finally {
            loading.value = false;
        }
    };

    const createLayout = async (flatId?: number | null, layoutData?: LayoutData) => {
        loading.value = true;
        error.value = null;
        try {
            const response = await layoutApi.createLayout({
                flat: flatId ?? null,
                layout_data: layoutData ?? {
                    walls: [],
                    points: [],
                    scale_cm_per_px: null
                }
            });
            layouts.value.push(response.data);
            currentLayout.value = response.data;
            return response.data;
        } catch (err) {
            const message = err instanceof Error ? err.message : String(err);
            error.value = `Blad przy tworzeniu layoutu: ${message}`;
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
            const response = await layoutApi.saveLayoutData(currentLayout.value.id, layoutData);
            currentLayout.value = response.data;
            const index = layouts.value.findIndex(l => l.id === response.data.id);
            if (index >= 0) {
                layouts.value[index] = response.data;
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : String(err);
            error.value = `Blad przy zapisywaniu layoutu: ${message}`;
            console.error(err);
            throw err;
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
            error.value = `Blad przy usuwaniu layoutu: ${message}`;
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
        deleteLayout,
        selectLayout,
        clearError
    };
});
