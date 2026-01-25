// src/api/layoutApi.ts
import api from './apiService';

export interface LayoutData {
    walls?: Array<{ x1: number; y1: number; x2: number; y2: number }>;
    points?: Array<{ id: string; x: number; y: number }>;
    scale_cm_per_px?: number;
    [key: string]: unknown;
}

export interface Layout {
    id: number;
    flat: number | null;
    image: string | null;
    scale_cm_per_px: number | null;
    layout_data: LayoutData;
    created_at: string;
    updated_at: string;
}

export const layoutApi = {
    /**
     * Pobierz wszystkie plany piętra
     */
    listLayouts: () => api.get<Layout[] | { results: Layout[] }>('/layouts/'),

    /**
     * Pobierz konkretny plan
     */
    getLayout: (id: number) => api.get<Layout>(`/layouts/${id}/`),

    /**
     * Utwórz nowy plan
     */
    createLayout: (data: { flat?: number | null; layout_data?: LayoutData }) =>
        api.post<Layout>('/layouts/', data),

    /**
     * Zaktualizuj plan (całościowo)
     */
    updateLayout: (id: number, data: Partial<Layout>) =>
        api.put<Layout>(`/layouts/${id}/`, data),

    /**
     * Zaktualizuj plan (częściowo)
     */
    patchLayout: (id: number, data: Partial<Layout>) =>
        api.patch<Layout>(`/layouts/${id}/`, data),

    /**
     * Usuń plan
     */
    deleteLayout: (id: number) => api.delete(`/layouts/${id}/`),

    setScale: (id: number, scaleCmPerPx: number) =>
        api.post<Layout>(`/layouts/${id}/set_scale/`, { scale_cm_per_px: scaleCmPerPx }),

    saveLayoutData: (id: number, layoutData: LayoutData) =>
        api.post<Layout>(`/layouts/${id}/save_layout_data/`, { layout_data: layoutData })
};
