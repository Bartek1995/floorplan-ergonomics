// src/api/flatApi.ts
import api from './apiService'

/**
 * TYPY DANYCH
 */

export interface LayoutData {
  walls?: Array<{ x1: number; y1: number; x2: number; y2: number }>
  points?: Array<{ id: string; x: number; y: number }>
  scale_cm_per_px?: number
  [key: string]: unknown
}

export interface Layout {
  id: number
  flat: number
  image: string | null
  scale_cm_per_px: number | null
  layout_data: LayoutData
  created_at: string
  updated_at: string
}

export interface Flat {
  id: number
  name: string
  address: string
  area_sqm: number | null
  rooms: number | null
  description: string
  layout: Layout | null
  created_at: string
  updated_at: string
}

export interface FlatCreateUpdate {
  name: string
  address?: string
  area_sqm?: number
  rooms?: number
  description?: string
}

/**
 * API ENDPOINTS DLA MIESZKAŃ
 */

export const flatApi = {
  /**
   * Pobierz listę wszystkich mieszkań
   * GET /api/flats/
   */
  listFlats: (params?: { page?: number; search?: string; rooms?: number }) =>
    api.get<{ results: Flat[]; count: number; next: string | null; previous: string | null }>(
      '/flats/',
      { params }
    ),

  /**
   * Pobierz szczegóły konkretnego mieszkania
   * GET /api/flats/:id/
   */
  getFlat: (id: number) => api.get<Flat>(`/flats/${id}/`),

  /**
   * Utwórz nowe mieszkanie
   * POST /api/flats/
   */
  createFlat: (data: FlatCreateUpdate) => api.post<Flat>('/flats/', data),

  /**
   * Zaktualizuj mieszkanie (całościowo)
   * PUT /api/flats/:id/
   */
  updateFlat: (id: number, data: FlatCreateUpdate) =>
    api.put<Flat>(`/flats/${id}/`, data),

  /**
   * Zaktualizuj mieszkanie (częściowo)
   * PATCH /api/flats/:id/
   */
  patchFlat: (id: number, data: Partial<FlatCreateUpdate>) =>
    api.patch<Flat>(`/flats/${id}/`, data),

  /**
   * Usuń mieszkanie
   * DELETE /api/flats/:id/
   */
  deleteFlat: (id: number) => api.delete(`/flats/${id}/`),

  /**
   * Wrzuć obraz layoutu do mieszkania
   * POST /api/flats/:id/upload_layout_image/
   */
  uploadLayoutImage: (flatId: number, image: File) => {
    const formData = new FormData()
    formData.append('image', image)
    return api.post<Layout>(`/flats/${flatId}/upload_layout_image/`, formData)
  }
}

/**
 * API ENDPOINTS DLA LAYOUTÓW
 */

export const layoutApi = {
  /**
   * Pobierz listę wszystkich layoutów
   * GET /api/layouts/
   */
  listLayouts: (params?: { flat?: number }) =>
    api.get<{ results: Layout[]; count: number; next: string | null; previous: string | null }>(
      '/layouts/',
      { params }
    ),

  /**
   * Pobierz szczegóły konkretnego layoutu
   * GET /api/layouts/:id/
   */
  getLayout: (id: number) => api.get<Layout>(`/layouts/${id}/`),

  /**
   * Utwórz nowy layout
   * POST /api/layouts/
   */
  createLayout: (data: { flat: number; layout_data?: LayoutData }) =>
    api.post<Layout>('/layouts/', data),

  /**
   * Zaktualizuj layout (całościowo)
   * PUT /api/layouts/:id/
   */
  updateLayout: (id: number, data: Partial<Layout>) =>
    api.put<Layout>(`/layouts/${id}/`, data),

  /**
   * Zaktualizuj layout (częściowo)
   * PATCH /api/layouts/:id/
   */
  patchLayout: (id: number, data: Partial<Layout>) =>
    api.patch<Layout>(`/layouts/${id}/`, data),

  /**
   * Usuń layout
   * DELETE /api/layouts/:id/
   */
  deleteLayout: (id: number) => api.delete(`/layouts/${id}/`),

  /**
   * Ustaw skalę layoutu
   * POST /api/layouts/:id/set_scale/
   */
  setScale: (id: number, scaleCmPerPx: number) =>
    api.post<Layout>(`/layouts/${id}/set_scale/`, { scale_cm_per_px: scaleCmPerPx }),

  /**
   * Zapisz dane layoutu (ściany, punkty, itp)
   * POST /api/layouts/:id/save_layout_data/
   */
  saveLayoutData: (id: number, layoutData: LayoutData) =>
    api.post<Layout>(`/layouts/${id}/save_layout_data/`, { layout_data: layoutData })
}
