<script setup>
import { defineEmits, ref } from 'vue';
import DataTable from 'datatables.net-vue3';
import DataTablesCore from 'datatables.net';
import { IconFolderOpen } from '@tabler/icons-vue';
 
DataTable.use(DataTablesCore);
 // Definir un evento que emitirá el ID al hacer clic
const emit = defineEmits(["row-click"]);

// Datos de ejemplo
const data = ref([
  { id: 1, name: "Juan Pérez", email: "juan@example.com" },
  { id: 2, name: "María López", email: "maria@example.com" }
]);

// Configuración de columnas con un botón que dispara @click
const columns = ref([
  { title: "ID", data: "id" },
  { title: "Nombre", data: "name" },
  { title: "Correo", data: "email" },
  {
    title: "Acciones",
    data: "id", // Este dato se usará en la columna
    render: function (data) {
      return `<button class="btn btn-sm btn-default" data-id="${data}">
        <svg  xmlns="http://www.w3.org/2000/svg"  width="18"  height="18"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="1.5"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-folder-open"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M5 19l2.757 -7.351a1 1 0 0 1 .936 -.649h12.307a1 1 0 0 1 .986 1.164l-.996 5.211a2 2 0 0 1 -1.964 1.625h-14.026a2 2 0 0 1 -2 -2v-11a2 2 0 0 1 2 -2h4l3 3h7a2 2 0 0 1 2 2v2" /></svg>
        Ver Pedido
        </button>`;
    }
  }
]);

// Evento para capturar clics en la tabla
const handleClick = (event) => {
  const button = event.target.closest(".btn-action"); // Verifica si el clic es en un botón
  if (button) {
      const id = button.getAttribute("data-id"); // Obtener ID del registro
    emit("row-click", id); // Emitir evento con el ID
  }
};


// opciones
const options = {
    paging: false,
    createdRow: function (row) {
    row.classList.add("p-1", "bg-light"); // Aplica la clase a cada fila
    },
    columnDefs: [
        {
            targets: "_all",
            className: "p-1 text-center",
        },
    ],
};

</script>

<template>
  <div class="table-container">
    <!-- DataTable con evento de clic -->
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
  padding-bottom: .50rem;
}
</style>
