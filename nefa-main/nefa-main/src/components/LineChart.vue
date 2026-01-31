<script setup>
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps({
  increase: {
    type: Boolean,
    required: true,
  },
  datasets: {
    type: Array,
    required: true,
  },
})

const chartData = {
  labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
  datasets: [
    {
      label: 'Data One',
      borderColor: props.increase ? '#28C165' : '#F4574D',
      borderWidth: 1,
      backgroundColor: props.increase ? 'rgba(95, 223, 146, 0.3)' : 'rgba(255, 189, 189, 0.3)',
      fill: true,
      data: props.datasets,
      tension: 0.4,
    },
  ],
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
  },
  elements: {
    point: {
      radius: 0,
    },
  },
  scales: {
    y: {
      display: false,
      grid: {
        display: false,
      },
    },
    x: {
      display: false,
      grid: {
        display: false,
      },
    },
  },
}
</script>

<template>
  <Line :data="chartData" :options="chartOptions" />
</template>
