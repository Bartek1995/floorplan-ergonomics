<template>
    <Form :key="formKey" ref="formRef" :resolver="resolver" :initialValues="initialValues" @submit="onSubmit" class="flex flex-col gap-4 w-fit min-w-[200px]">
        <FormField v-slot="$field" name="id" class="flex flex-col gap-1" hidden>
            <label for="id" class="fw-bold">id</label>
            <InputText v-bind="$field.props" id="id" placeholder="id" :disabled="true" />
            <Message v-if="$field.invalid" severity="error" size="small" variant="simple">
                {{ $field.error?.message }}
            </Message>
        </FormField>

        <FormField v-slot="$field" name="email" class="flex flex-col gap-1">
            <label for="email" class="fw-bold">{{ t('user.email') }}</label>
            <InputText v-bind="$field.props" id="email" :placeholder="t('user.email_placeholder')" :disabled="true" />
            <Message v-if="$field.invalid" severity="error" size="small" variant="simple">
                {{ $field.error?.message }}
            </Message>
        </FormField>
        <div class="flex flex-row">
            <FormField v-slot="$field" name="first_name" class="flex flex-col gap-1 mr-3 w-auto">
                <label for="first_name" class="fw-bold">{{ t('user.first_name') }}</label>
                <InputText v-bind="$field.props" id="first_name" :placeholder="t('user.first_name_placeholder')" :disabled="true" />
                <Message v-if="$field.invalid" severity="error" size="small" variant="simple">
                    {{ $field.error?.message }}
                </Message>
            </FormField>
            <FormField v-slot="$field" name="last_name" class="flex flex-col gap-1 w-auto">
                <label for="last_name" class="fw-bold">{{ t('user.last_name') }}</label>
                <InputText v-bind="$field.props" id="last_name" :placeholder="t('user.last_name_placeholder')" :disabled="true" />
                <Message v-if="$field.invalid" severity="error" size="small" variant="simple">
                    {{ $field.error?.message }}
                </Message>
            </FormField>
        </div>
        <Button type="submit" severity="danger" :label="t('form.delete')" :loading="isSubmitting" :disabled="isLoading || isSubmitting" />
    </Form>
</template>

<script setup lang="ts">
import { ref, inject } from 'vue';
import { z } from 'zod';
import { Form, type FormInstance, type FormSubmitEvent } from '@primevue/forms';
import { FormField } from '@primevue/forms';
import { useZodApiResolver } from '@/composable/api/useZodApiResolver';
import { useI18n } from 'vue-i18n';
import api from '@/api/apiService';

const { t } = useI18n();
const isSubmitting = ref(false);
const formRef = ref<FormInstance | null>(null);
const dialogRef = inject('dialogRef') as Ref<{ close: () => void; emit: (event: string, ...args: any[]) => void } | null>;

const initialValues = reactive({
    email: '',
    first_name: '',
    last_name: '',
    groups: []
});

const props = defineProps<{
    row: any;
}>();

const emit = defineEmits<{
    (e: 'submit:success', responseData: any): void;
    (e: 'submit:error', error: unknown): void;
    (e: 'save'): void;
}>();

const schema = z.object({
    email: z.string().email(t('user.email_validation')),
    first_name: z.string().min(2, t('user.first_name_validation')),
    last_name: z.string().min(2, t('user.last_name_validation')),
    groups: z.array(z.string()).min(1, t('user.groups_validation'))
});

const { resolver, setApiErrors, clearApiErrors } = useZodApiResolver(schema);
const formKey = ref(0);
const isLoading = ref(true);

onMounted(async () => {
    isLoading.value = true;
    try {
        const response = await api.get('/construction/manager/user/', {
            params: {
                id: props.row
            }
        });

        const data = response.data[0];

        initialValues.email = data.email || 'asd';
        initialValues.first_name = data.first_name || 'asd';
        initialValues.last_name = data.last_name || 'asd';
        initialValues.groups = data.groups || [];

        formKey.value++;
    } catch (error) {
        console.error('Błąd pobierania danych:', error);
    } finally {
        isLoading.value = false;
    }
});

const groups = [
    { label: 'Administrator', value: 'Administrators' },
    { label: 'Architekt', value: 'Architects' },
    { label: 'Klient', value: 'Clients' },
    { label: 'Kierownik Budowy', value: 'ConstructionsManagers' },
    { label: 'Właściciel Firmy', value: 'Owners' },
    { label: 'Geodeta', value: 'Surveyors' },
    { label: 'Pracownik Fizyczny', value: 'Teams' }
];

const onSubmit = async (event: FormSubmitEvent<Record<string, any>>) => {
    clearApiErrors();
    isSubmitting.value = true;

    try {
        const { data } = await api.delete('/construction/manager/user/' + props.row + '/');
        emit('submit:success', data);
        emit('save');
        formRef.value?.reset();
        dialogRef.value?.close();
    } catch (err: any) {
        setApiErrors(err.response?.data || {});
        await formRef.value?.validate();
        emit('submit:error', err);
    } finally {
        isSubmitting.value = false;
    }
};
</script>

<style scoped></style>
