<script setup>
import { ref } from 'vue'
const listado = ref([
    { cant: 1, producto: 'Explorer', proveedor: 'Finca Las Moras', costo: 0.25, margen: 0.06, pvp: 0.31 },
    { cant: 2, producto: 'Explorer', proveedor: 'Finca Las Moras', costo: 0.25, margen: 0.06, pvp: 0.31 },
    { cant: 3, producto: 'Explorer', proveedor: 'Finca Las Moras', costo: 0.25, margen: 0.06, pvp: 0.31 }
])

const selectText = (event) => {
    event.target.select()
}

const handleKeydown = (event, index) => {
    const inputs = document.querySelectorAll('.my-input');
    const currentIndex = Array.prototype.indexOf.call(inputs, event.target);
    if (event.key === 'Enter' && currentIndex < inputs.length - 1) {
        inputs[currentIndex + 1].focus();
    }
    if (event.key === 'Enter' && event.shiftKey   && currentIndex > 0) {
        inputs[currentIndex - 1].focus();
    }
}

const handleKeydown2 = (event, index) => {
    const inputs = document.querySelectorAll('.my-input-2');
    const currentIndex = Array.prototype.indexOf.call(inputs, event.target);
    if (event.key === 'Enter' && currentIndex < inputs.length - 1) {
        inputs[currentIndex + 1].focus();
    }
    if (event.key === 'Enter' && event.shiftKey   && currentIndex > 0) {
        inputs[currentIndex - 1].focus();
    }
}

</script>
<template>
    <div class="container-fluid p-0">
        <div class="row pt-1 pb-3">
            <div class="col d-flex gap-2 justify-content-start align-items-center">
                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        Disponibilidad 
                    </span>
                    <span class="text-secondary ps-1 pe-2">
                        01/01/2024
                    </span>
                </div>
                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        Estado 
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        <i class="text-success">
                            <svg  xmlns="http://www.w3.org/2000/svg"  width="15"  height="15"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="1.5"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-lock-open-2"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M3 13a2 2 0 0 1 2 -2h10a2 2 0 0 1 2 2v6a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2z" /><path d="M9 16a1 1 0 1 0 2 0a1 1 0 0 0 -2 0" /><path d="M13 11v-4a4 4 0 1 1 8 0v4" /></svg>
                        </i>
                        <i class="text-dark">
                            <svg  xmlns="http://www.w3.org/2000/svg"  width="15"  height="15"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="1.5"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-lock"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M5 13a2 2 0 0 1 2 -2h10a2 2 0 0 1 2 2v6a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2v-6z" /><path d="M11 16a1 1 0 1 0 2 0a1 1 0 0 0 -2 0" /><path d="M8 11v-4a4 4 0 1 1 8 0v4" /></svg>
                        </i>
                        <span>
                            Activa
                        </span>
                    </span>
                </div>
            </div>
            <div class="col d-flex gap-2 justify-content-end align-items-center">
                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        Proveedores
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        12
                    </span>
                </div>
                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        QB's
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        5
                    </span>
                </div><div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        HB's
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        5
                    </span>
                </div><div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        Tallos
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        52254
                    </span>
                </div>
            </div>
        </div>
        <div class="row d-flex justify-content-start p-1 rounded-1">
            <div class="col-4">
                <input type="email" class="form-control form-control-sm rounded-1 border-slate-500" placeholder="Buscar">
            </div>
            <div class="col-8 d-flex gap-3 justify-content-end">
                    <a href="" class="border-slate-500 p-0 ps-2 pe-2 d-flex gap-2  align-items-center rounded-1 bg-slate-200">
                        <svg  xmlns="http://www.w3.org/2000/svg"  width="15"  height="15"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="1.5"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-package-import"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M12 21l-8 -4.5v-9l8 -4.5l8 4.5v4.5" /><path d="M12 12l8 -4.5" /><path d="M12 12v9" /><path d="M12 12l-8 -4.5" /><path d="M22 18h-7" /><path d="M18 15l-3 3l3 3" /></svg>
                        Importar
                    </a>
                    <a href="" class="border-slate-500 p-0 ps-2 pe-2 d-flex gap-2  align-items-center rounded-1 bg-slate-200">
                        <svg  xmlns="http://www.w3.org/2000/svg"  width="15"  height="15"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="1.5"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-share"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M6 12m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0" /><path d="M18 6m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0" /><path d="M18 18m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0" /><path d="M8.7 10.7l6.6 -3.4" /><path d="M8.7 13.3l6.6 3.4" /></svg>
                        Compartir
                    </a>
                    <a href="" class="border-slate-500 p-0 ps-2 pe-2 d-flex gap-2  align-items-center rounded-1 bg-slate-200">
                        <svg  xmlns="http://www.w3.org/2000/svg"  width="15"  height="15"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="1.5"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-checkbox"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M9 11l3 3l8 -8" /><path d="M20 12v6a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2v-12a2 2 0 0 1 2 -2h9" /></svg>
                        Todos
                    </a>
                    <a href="" class="border-slate-500 p-0 ps-2 pe-2 d-flex gap-2  align-items-center rounded-1 bg-slate-200">
                        <svg  xmlns="http://www.w3.org/2000/svg"  width="15"  height="15"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="1.5"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-square"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M3 3m0 2a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2z" /></svg>
                        Ninguno
                    </a>
                    <a href="" class="border-slate-500 p-0 ps-2 pe-2 d-flex gap-2  align-items-center rounded-1 bg-slate-200">
                        <svg xmlns="http://www.w3.org/2000/svg"  width="15"  height="15"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="1.5"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-currency-dollar"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M16.7 8a3 3 0 0 0 -2.7 -2h-4a3 3 0 0 0 0 6h4a3 3 0 0 1 0 6h-4a3 3 0 0 1 -2.7 -2" /><path d="M12 3v3m0 12v3" /></svg>
                        Editar
                    </a>
                    <a href="" class="border-slate-500 p-0 ps-2 pe-2 d-flex gap-2  align-items-center rounded-1 bg-slate-200">
                        <svg  xmlns="http://www.w3.org/2000/svg"  width="15"  height="15"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="1.5"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-shopping-cart-dollar"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M4 19a2 2 0 1 0 4 0a2 2 0 0 0 -4 0" /><path d="M13 17h-7v-14h-2" /><path d="M6 5l14 1l-.575 4.022m-4.925 2.978h-8.5" /><path d="M21 15h-2.5a1.5 1.5 0 0 0 0 3h1a1.5 1.5 0 0 1 0 3h-2.5" /><path d="M19 21v1m0 -8v1" /></svg>
                        Armar Pedido
                    </a>
            </div>
        </div>        
        <div class="row">
            <div class="col">
            <div class="table-responsive">
            <table class="table table-bordered table-hover">
                <thead>
                    <tr class="text-center">
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">Cant</th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">Productos</th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">Proveedor</th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">Tallos</th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">Costo</th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">Margen</th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">PVP</th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">
                                <svg  xmlns="http://www.w3.org/2000/svg"  width="18"  height="18"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="1.5"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-settings"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M10.325 4.317c.426 -1.756 2.924 -1.756 3.35 0a1.724 1.724 0 0 0 2.573 1.066c1.543 -.94 3.31 .826 2.37 2.37a1.724 1.724 0 0 0 1.065 2.572c1.756 .426 1.756 2.924 0 3.35a1.724 1.724 0 0 0 -1.066 2.573c.94 1.543 -.826 3.31 -2.37 2.37a1.724 1.724 0 0 0 -2.572 1.065c-.426 1.756 -2.924 1.756 -3.35 0a1.724 1.724 0 0 0 -2.573 -1.066c-1.543 .94 -3.31 -.826 -2.37 -2.37a1.724 1.724 0 0 0 -1.065 -2.572c-1.756 -.426 -1.756 -2.924 0 -3.35a1.724 1.724 0 0 0 1.066 -2.573c-.94 -1.543 .826 -3.31 2.37 -2.37c1 .608 2.296 .07 2.572 -1.065z" /><path d="M9 12a3 3 0 1 0 6 0a3 3 0 0 0 -6 0" /></svg>
                        </th>
                    </tr>
                </thead>
                <tbody>
                        <tr v-for="item in listado" :key="item">
                            <td class="p-0 text-start ps-3">{{ item.cant }} QB</td>
                            <td class="p-0 d-flex flex-column justify-content-start text-start">
                            <span> Explorer </span>
                            </td>
                            <td class="p-0 text-start">Finca Las Moras</td>
                            <td class="p-0 text-end">
                                {{  item * 3 }}
                            </td>
                            <td class="p-0 text-end">
                                <input type="number" step="0.01" class="my-input-2 border" v-model="item.pvp" @focus="selectText"  @keydown="handleKeydown2($event, index)">
                            </td>
                            <td class="p-0 text-end bg-green-100">
                                <input type="number" step="0.01" class="my-input border" v-model="item.pvp" @focus="selectText"  @keydown="handleKeydown($event, index)">
                            </td>
                            <td class="p-0 text-end bg-green-100">0.31</td>
                            <td class="p-0 text-center">
                                <input type="checkbox" name="" id="">
                            </td>
                        </tr>
                    </tbody>
            </table>
        </div>
        </div>
        </div>
        </div>
</template>
<style scoped>
    input[type="checkbox"] {
        width: 15px;
        height: 15px;
    }
    .my-input {
        width: 30%;
        height: 20px;
        border: 1px solid #ccc;
        border-radius: 2px;
        text-align: right;
    }
</style>