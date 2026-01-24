// src/router/index.ts

/// <reference types="vite/client" />

import type { RouteRecordRaw } from 'vue-router';
import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes: Array<RouteRecordRaw> = [
    {
        path: '/',
        component: () => import('@/layout/AppLayout.vue'),
        children: [
            {
                path: '',
                name: 'flats-list',
                component: () => import('@/views/floorplan/FlatsListView.vue'),
                meta: { requiresAuth: true, title: 'Mieszkania' }
            },
            {
                path: 'flats',
                name: 'flats-list-alt',
                component: () => import('@/views/floorplan/FlatsListView.vue'),
                meta: { requiresAuth: true, title: 'Mieszkania' }
            },
            {
                path: 'flats/:id',
                name: 'flat-detail',
                component: () => import('@/views/floorplan/FlatDetailView.vue'),
                meta: { requiresAuth: true, title: 'Szczegóły mieszkania' }
            },
            {
                path: 'diagnostics',
                name: 'diagnostics',
                component: () => import('@/views/floorplan/DiagnosticsView.vue'),
                meta: { requiresAuth: true, title: 'Diagnostyka' }
            },
            {
                path: 'debug',
                name: 'debug',
                component: () => import('@/views/floorplan/DebugView.vue'),
                meta: { requiresAuth: true, title: 'Debug' }
            },
            {
                path: 'editor',
                name: 'floorplan-editor',
                component: () => import('@/views/floorplan/EditorView.vue'),
                meta: { requiresAuth: true, title: 'Edytor planu piętra' }
            },
            {
                path: 'layouts',
                name: 'layouts-list',
                component: () => import('@/views/floorplan/LayoutsListView.vue'),
                meta: { requiresAuth: true, title: 'Plany pięter' }
            },
            {
                path: 'layouts/:id',
                name: 'layout-detail',
                component: () => import('@/views/floorplan/LayoutDetailView.vue'),
                meta: { requiresAuth: true, title: 'Szczegóły planu' }
            },
            {
                path: 'settings',
                name: 'settings',
                component: () => import('@/views/general/containers/SettingsView.vue'),
                meta: { requiresAuth: true, title: 'Ustawienia' }
            }
        ]
    },
    {
        path: '/auth/login',
        name: 'login',
        component: () => import('@/views/login/containers/LoginView.vue'),
        meta: { title: 'Logowanie' }
    },
    {
        path: '/auth/access',
        name: 'accessDenied',
        component: () => import('@/views/general/AuthAccessDenied.vue'),
        meta: { title: 'Brak dostępu' }
    },
    {
        path: '/auth/error',
        name: 'error',
        component: () => import('@/views/general/AuthError.vue'),
        meta: { title: 'Błąd uwierzytelniania' }
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'notfound',
        component: () => import('@/views/general/NotFound.vue'),
        meta: { title: '404' }
    }
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
});

// recovery dla błędów dynamicznych importów
router.onError((err, to) => {
    if (err?.message?.includes?.('Failed to fetch dynamically imported module')) {
        if (localStorage.getItem('vuetify:dynamic-reload')) {
            console.error('Dynamic import error, reload nie pomógł', err);
        } else {
            console.log('Przeładowanie strony w celu naprawy dynamic import error');
            localStorage.setItem('vuetify:dynamic-reload', 'true');
            location.assign(to.fullPath);
        }
    } else {
        console.error(err);
    }
});

router.isReady().then(() => {
    localStorage.removeItem('vuetify:dynamic-reload');
});

router.beforeEach(async (to) => {
    const auth = useAuthStore();
    if (!auth.isAuthReady) await auth.initialize();

    if (to.meta.requiresAuth && !auth.isLoggedIn) {
        return { name: 'login', query: { next: to.fullPath } };
    }
    if (to.name === 'login' && auth.isLoggedIn) {
        return { name: 'flats-list', replace: true };
    }
});

router.afterEach((to) => {
    const defaultTitle = 'Construction Manager';
    document.title = (to.meta.title as string) || defaultTitle;
});

export default router;
