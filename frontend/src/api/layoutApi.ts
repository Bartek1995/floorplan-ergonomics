// src/api/layoutApi.ts
import api from './apiService';

export interface LayoutData {
    walls?: Array<{ x1: number; y1: number; x2: number; y2: number }>;
    objects?: Array<{ x: number; y: number; w: number; h: number; type: string }>;
    doors?: Array<{ x: number; y: number; width: number; height: number }>;
    [key: string]: unknown;
}

export interface Layout {
    id: number;
    name: string;
    layout_data: LayoutData;
    created_at: string;
    updated_at: string;
}

export const layoutApi = {
    /**
     * Pobierz wszystkie plany piętra
     */
    listLayouts: () => api.get<Layout[]>('/layouts/'),

    /**
     * Pobierz konkretny plan
     */
    getLayout: (id: number) => api.get<Layout>(`/layouts/${id}/`),

    /**
     * Utwórz nowy plan
     */
    createLayout: (data: { name: string; layout_data?: LayoutData }) =>
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
    deleteLayout: (id: number) => api.delete(`/layouts/${id}/`)
};
