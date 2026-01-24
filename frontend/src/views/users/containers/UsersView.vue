<script setup lang="tsx">
import { Config } from '@/types/core/CustomDataTable';
import { defineAsyncComponent } from 'vue';
import { useDateFormatter } from '@/composable/useDateFormatter';
import CustomDataTable from '@/components/DataTable/CustomDataTable.vue';
import Tag from 'primevue/tag';
import UserMenu from '@/views/users/components/UserMenu.vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const { formatDate } = useDateFormatter();
const createFormComponent = defineAsyncComponent(() => import('@/views/users/components/CreateUsersForm.vue'));
const tableRef = ref();

const configuration: Config[] = [
    {
        field: 'id',
        header: '',
        sortable: false,
        filterable: false,
        filterType: 'text',
        body: (row: any) => <UserMenu row={row.id} onUpdated={() => tableRef.value?.fetchData?.()} />
    },
    {
        field: 'is_active',
        header: t('user.is_active'),
        sortable: true,
        filterable: true,
        filterType: 'select',
        filterSelectArray: [
            { label: 'Tak', value: true },
            { label: 'Nie', value: false }
        ],
        body: (row: any) => (
            <span
                style={{
                    color: row.is_active ? 'green' : 'red',
                    fontWeight: 'bold',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                }}
            >
                <i class={`pi ${row.is_active ? 'pi-check' : 'pi-times'}`}></i>
            </span>
        )
    },
    { field: 'first_name', header: t('user.first_name'), sortable: true, filterable: true, filterType: 'text' },
    { field: 'last_name', header: t('user.last_name'), sortable: true, filterable: true, filterType: 'text' },
    { field: 'email', header: t('user.email'), sortable: true, filterable: true, filterType: 'text' },
    {
        field: 'groups',
        header: t('user.groups'),
        sortable: true,
        filterable: true,
        filterType: 'select',
        filterSelectArray: [
            { label: 'Administrator', value: 'Administrators' },
            { label: 'Architekt', value: 'Architects' },
            { label: 'Klient', value: 'Clients' },
            { label: 'Kierownik Budowy', value: 'ConstructionsManagers' },
            { label: 'Właściciel Firmy', value: 'Owners' },
            { label: 'Geodeta', value: 'Surveyors' },
            { label: 'Pracownik Fizyczny', value: 'Teams' }
        ],
        body: (row: any) => {
            if (!row.groups || row.groups.length === 0) {
                return <Tag severity="danger" value="Brak grup" />;
            }

            return (
                <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                    {row.groups.map((group: string) => (
                        <Tag severity={group === 'Owners' ? 'warning' : group === 'Administrators' ? 'success' : 'info'} value={group} />
                    ))}
                </div>
            );
        }
    },
    {
        field: 'last_login',
        header: t('user.last_login'),
        sortable: true,
        filterable: true,
        filterType: 'datetime',
        body: (row: any) => <span>{formatDate(row.last_login)}</span>
    },
    { field: 'date_joined', header: t('user.date_joined'), sortable: true, filterable: true, filterType: 'datetime', body: (row: any) => <span>{formatDate(row.date_joined)}</span> }
];
</script>

<template>
    <div class="flex flex-col">
        <CustomDataTable ref="tableRef" url="/construction/manager/user/" :config="configuration" :createFormComponent="createFormComponent" />
    </div>
</template>
