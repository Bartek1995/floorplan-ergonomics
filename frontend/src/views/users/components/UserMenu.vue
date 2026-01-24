<script lang="ts" setup>
import { ref } from 'vue';
import { useDialog } from 'primevue/usedialog';
import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const toast = useToast();
const dialog = useDialog();

const UpdateUserForm = defineAsyncComponent(() => import('@/views/users/components/UpdateUserForm.vue'));
const DeleteUserForm = defineAsyncComponent(() => import('@/views/users/components/DeleteUserForm.vue'));

const props = defineProps<{
    row: string | number;
}>();

const emit = defineEmits<{
    (e: 'updated'): void;
}>();

const showUpdateDialog = () => {
    dialog.open(UpdateUserForm, {
        props: {
            header: t('user.edit_user'),
            modal: true
        },
        emits: {
            ...props,
            onSave: (e) => {
                toast.add({ severity: 'success', summary: 'Sukces', detail: t('user.edit_user_succes'), life: 3000 });
                emit('updated');
            }
        },
        templates: {}
    });
};

const showDeleteDialog = () => {
    dialog.open(DeleteUserForm, {
        props: {
            header: t('user.delete_user'),
            modal: true
        },
        emits: {
            ...props,
            onSave: (e) => {
                toast.add({ severity: 'success', summary: 'Sukces', detail: t('user.delete_user_succes'), life: 3000 });
            }
        },
        templates: {}
    });
};

const menu = ref();
const items = ref([
    {
        label: t('user.edit_user'),
        icon: 'pi pi-file-edit',
        command: () => {
            showUpdateDialog();
        }
    },
    {
        label: t('user.delete_user'),
        icon: 'pi pi-trash',
        command: () => {
            showDeleteDialog();
        }
    }
]);

const toggle = (event) => {
    menu.value.toggle(event);
};
</script>

<template>
    <Button type="button" severity="secondary" icon="pi pi-bars" class="p-button-rounded p-button-text" @click="toggle" aria-haspopup="true" aria-controls="overlay_tmenu" />
    <TieredMenu ref="menu" id="overlay_tmenu" :model="items" popup />
</template>
