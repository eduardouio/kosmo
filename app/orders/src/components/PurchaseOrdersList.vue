<script setup>
import { defineEmits, ref, computed, onMounted } from 'vue';
import DataTable from 'datatables.net-vue3';
import DataTablesCore from 'datatables.net';
import { usePurchaseStore } from '@/stores/purcharses';

// Variables
const purchasesStore = usePurchaseStore();
DataTable.use(DataTablesCore);

// Datos computados para extraer solo las órdenes
const data = computed(() => {
  return purchasesStore.purcharses_by_order.map(orderData => ({
    id: orderData.order.id,
    date: orderData.order.date,
    status: orderData.order.status,
    type_document: orderData.order.type_document,
    total_price: orderData.order.total_price,
    partner_name: orderData.order.partner.name,
    qb_total: orderData.order.qb_total,
    hb_total: orderData.order.hb_total,
  }));
});

// Configuración de columnas
const columns = ref([
  { title: "ID", data: "id" },
  { title: "Fecha", data: "date" },
  { title: "Estado", data: "status" },
  { title: "Tipo Documento", data: "type_document" },
  { title: "Proveedor", data: "partner_name" },
  { title: "QBs", data:"qb_total" },
  { title: "HBs", data:"hb_total" },
  { title: "Total", data: "total_price" },
  {
    title: "Acciones",
    data: "id",
    render: function (data) {
      return `<button class="btn btn-sm btn-default view-order" data-id="${data}">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-folder-open">
          <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
          <path d="M5 19l2.757 -7.351a1 1 0 0 1 .936 -.649h12.307a1 1 0 0 1 .986 1.164l-.996 5.211a2 2 0 0 1 -1.964 1.625h-14.026a2 2 0 0 1 -2 -2v-11a2 2 0 0 1 2 -2h4l3 3h7a2 2 0 0 1 2 2v2"/>
        </svg>
        Ver Pedido
        </button>`;
    }
  }
]);

// Evento para capturar clics en la tabla
const handleClick = (event) => {
  const button = event.target.closest(".view-order");
  if (button) {
    const id = button.getAttribute("data-id");
    handleViewOrder(id);
  }
};

// Función para manejar el evento de ver pedido
const handleViewOrder = (id) => {
  console.log(`Pedido seleccionado: ${id}`);
};

// Opciones de DataTable
const options = {
  paging: false,
  createdRow: function (row, data, dataIndex) {
    row.classList.add("p-1", "bg-light");
    row.cells[0].classList.add("text-center");
    row.cells[1].classList.add("text-start");
    row.cells[2].classList.add("text-center");
    row.cells[3].classList.add("text-start");
    row.cells[4].classList.add("text-start");
    row.cells[5].classList.add("text-end");
    row.cells[6].classList.add("text-end");
    row.cells[7].classList.add("text-end");
    row.cells[8].classList.add("text-center");
  },
};
</script>

<template>
  <div class="table-container">
    <DataTable
      :columns="columns"
      :data="data"
      :options="options"
      class="table table-bordered table-striped table-hover"
      @click="handleClick"
    />
  </div>
</template>

<style>
.dt-search {
  float: right;
  padding-top: 1rem;
  padding-bottom: 0.5rem;
}
</style>
