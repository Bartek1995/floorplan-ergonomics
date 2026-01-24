<template>
    <ThemeSwitcher />
    <div class="card flex justify-center">
        <Form :initialValues @submit="onFormSubmit" class="flex flex-col gap-4 w-full sm:w-80">
            <FormField v-slot="$field" name="username" initialValue="" class="flex flex-col gap-1">
                <InputText type="text" placeholder="Username" />
            </FormField>
            <FormField v-slot="$field" name="firstname" initialValue="" class="flex flex-col gap-1">
                <InputText type="text" placeholder="First Name" />
            </FormField>
            <FormField v-slot="$field" name="lastname" initialValue="" class="flex flex-col gap-1">
                <InputText type="text" placeholder="Last Name" />
            </FormField>
            <FormField v-slot="$field" name="password" initialValue="" class="flex flex-col gap-1">
                <Password type="text" placeholder="Password" :feedback="false" toggleMask fluid />
            </FormField>
            <FormField v-slot="$field" name="details" class="flex flex-col gap-1">
                <Textarea placeholder="Details" />
            </FormField>
            <Button type="submit" severity="secondary" label="Submit" />
        </Form>
    </div>
</template>

<script setup>
import { reactive } from 'vue';
import { Form, FormField } from '@primevue/forms';
import { useToast } from 'primevue/usetoast';

const toast = useToast();

const initialValues = reactive({
    details: ''
});

const onFormSubmit = ({ valid }) => {
  if (valid) {
    toast.add({ severity: 'success', summary: 'Form is submitted.', life: 3000 });
  }
};
</script>
