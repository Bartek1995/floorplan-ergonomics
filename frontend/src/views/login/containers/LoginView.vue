<!-- src/views/containers/LoginView.vue -->

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useI18n } from 'vue-i18n';

/* PrimeVue */
import Card from 'primevue/card';
import Divider from 'primevue/divider';

import LoginForm from '@/views/login/components/LoginForm.vue';
import LanguageSwitcher from '@/core/LanguageSwitcher.vue';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const loginLoading = ref(false);
const error = ref<string | null>(null);

/* gdzie przekierować po logowaniu */
function resolveNext(): string {
    const q = route.query.next;
    return (Array.isArray(q) ? q[0] : q)?.toString() || '/';
}

async function handleLogin({ email, password }: { email: string; password: string }) {
    error.value = null;
    loginLoading.value = true;
    try {
        await auth.login(email, password);

        router.replace(resolveNext());
    } catch (e: any) {
        error.value = e.response?.data?.detail ?? e.message ?? 'Błąd logowania';
    } finally {
        loginLoading.value = false;
    }
}
</script>

<template>
    <div class="flex min-h-screen items-center justify-center bg-surface-200 p-4">
        <Card class="w-full max-w-sm shadow-lg">
            <template #title>
                <div class="flex items-center justify-between">
                    {{ t('form_login.title') }}
                    <LanguageSwitcher />
                </div>
            </template>

            <template #content>
                <LoginForm @submit="handleLogin" :error="error" :loading="loginLoading" />
            </template>

            <Divider class="mt-4" />
            <p class="text-xs text-center opacity-60">FatIT © {{ new Date().getFullYear() }}</p>
        </Card>
    </div>
</template>
