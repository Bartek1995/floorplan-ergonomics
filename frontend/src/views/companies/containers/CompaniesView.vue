<script setup lang="tsx">
import { Config } from '@/types/core/CustomDataTable';
import CustomDataTable from '@/components/DataTable/CustomDataTable.vue';
import { defineAsyncComponent } from 'vue';

const CompaniesForm = defineAsyncComponent(() => import('@/views/companies/components/CompaniesForm.vue'));

const configuration: Config[] = [
  { field: 'id', header: 'ID', sortable: true, filterable: true, filterType: 'number' },
  {
    field: 'is_active',
    header: 'Aktywny',
    sortable: true,
    filterable: true,
    filterType: 'select',
    filterSelectArray: [
      { label: 'Tak', value: true },
      { label: 'Nie', value: false },
    ],
    body: (row: any) => {
      return () => (
        <span
          style={{
            color: row.is_active ? 'green' : 'red',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}
        >
          <i class={`pi ${row.is_active ? 'pi-check' : 'pi-times'}`}></i>
        </span>
      );
    }
  },
  { field: 'created_at', header: 'Data', sortable: true, filterable: true, filterType: 'date' },
  { field: 'name', header: 'Nazwa', sortable: true, filterable: true, filterType: 'text' },
  { field: 'email', header: 'Email', sortable: true, filterable: true, filterType: 'text' },
  { field: 'phone_number_1', header: 'Telefon 1', sortable: true, filterable: true, filterType: 'text' },
  { field: 'vat_id', header: 'NIP', sortable: true, filterable: true, filterType: 'text' },
  { field: 'address.state', header: 'Województwo', sortable: true, filterable: true, filterType: 'text' },
  { field: 'address.city', header: 'Miasto', sortable: true, filterable: true, filterType: 'text' },
  { field: 'address.postal_code', header: 'Kod Pocztowy', sortable: true, filterable: true, filterType: 'text' },
];
</script>

<template>
    <div class="flex flex-col">
        <CustomDataTable
            url="http://127.0.0.1:8000/api/construction/manager/company/"
            :config="configuration"
            :formComponent="CompaniesForm"
        />
    </div>
</template>
