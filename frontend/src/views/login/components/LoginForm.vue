<!-- src/views/components/LoginForm.vue -->

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToggle } from '@vueuse/core';
import { z } from 'zod';

/* PrimeVue Forms (zgodnie z dokumentacją) */
import { Form, type FormInstance, type FormSubmitEvent } from '@primevue/forms';
import { zodResolver } from '@primevue/forms/resolvers/zod';

import { useFormRevalidateOnLocale } from '@/core/composables/useFormRevalidateOnLocale';

const { t, locale } = useI18n();

interface LoginFormData {
    email: string;
    password: string;
}

const initialFormData = reactive<LoginFormData>({
    email: '',
    password: ''
});

/* props / emits */
const props = defineProps<{
    loading?: boolean;
    error: string | null;
}>();

const emit = defineEmits<{
    (e: 'submit', payload: LoginFormData): void;
}>();

const resolver = computed(() =>
    zodResolver(
        z.object({
            email: z.string().nonempty(t('form_login.required_email')),
            password: z.string().nonempty(t('form_login.required_password'))
        })
    )
);
const onFormSubmit = (event: FormSubmitEvent<Record<string, any>>) => {
    if (event.valid) {
        emit('submit', event.values as LoginFormData);
    }
};

/* state */
const formRef = ref<FormInstance | null>(null);
const [showPw, togglePw] = useToggle(false);

/* rewalidacja po zmianie języka */
useFormRevalidateOnLocale(formRef);
</script>

<template>
    <Form v-slot="$form" :initialValues="initialFormData" ref="formRef" :resolver="resolver" @submit="onFormSubmit" class="flex flex-col gap-4">
        <div class="flex flex-col gap-1">
            <InputText name="email" type="text" :placeholder="t('form_login.email')" autofocus @keyup.enter="formRef?.submit()" />
            <Message v-if="$form.email?.invalid" severity="error" size="small" variant="simple">{{ $form.email.error?.message }}</Message>
        </div>

        <div class="flex flex-col gap-1 relative">
            <Password name="password" :toggleMask="true" :feedback="false" :showToggleIcon="true" :mask="showPw ? false : true" :placeholder="t('form_login.password')" @keyup.enter="formRef?.submit()" @toggleMask="togglePw()" />

            <Message v-if="$form.password?.invalid" severity="error" size="small" variant="simple">
                {{ $form.password.error?.message }}
            </Message>
        </div>

        <!-- SUBMIT -->
        <Button type="submit" :label="t('form_login.button')" :loading="props.loading" icon="pi pi-sign-in" class="w-full mt-2" />

        <!-- GLOBAL ERROR -->
        <Message v-if="props.error" severity="error" class="mt-3">
            {{ props.error }}
        </Message>
    </Form>
</template>
