<script setup>
import { ref } from 'vue'
import { reactive } from 'vue';
import { onMounted } from 'vue'
import stock from '../data/stock.json'

const indicator = ref({})

const my_stock = reactive(stock.stock)
const colors = ref({
    'AMARILLO': 'bg-yellow-400 bg-gradient',
    'CREMA': 'bg-amber-400 bg-gradient',
    'ROJO': 'bg-red-400 bg-gradient',
    'BLANCO': 'bg-light',
    'TINTURADO': 'bg-gray-400 bg-gradient',
    'NARANJA': 'bg-orange-400 bg-gradient',
    'VIOLETA': 'bg-indigo-400 bg-gradient',
    'MORADO': 'bg-indigo-400 bg-gradient',
})

const selectText = (event) => {
    event.target.select()
}

const stockIdicator = (quantity) => {
    let my_indicator = {
        'total_QB': 0,
        'total_HB': 0,
        'total_stems': 0,
        'total_suppliers': [],
    }
    if (!my_stock || my_stock.length === 0) {
        console.warn('my_stock is empty or undefined.');
        indicator.value = my_indicator;
    }

    my_stock.forEach(item => {
        my_indicator.total_QB += item.box_model === 'HB' ? item.quantity : 0; 
        my_indicator.total_HB += item.box_model === 'QB' ? item.quantity : 0;
        my_indicator.total_stems += item.tot_stem_flower;
        if (!my_indicator.total_suppliers.includes(item.partner.name)) {
                my_indicator.total_suppliers.push(item.partner.name);
        }
    });
    console.log(my_indicator);
    indicator.value = my_indicator; // no fuciona
}

const handleKeydown = (event, index, cssClass) => {
    const inputs = document.querySelectorAll(cssClass);
    const currentIndex = Array.prototype.indexOf.call(inputs, event.target);
    if (event.key === 'Enter' && currentIndex < inputs.length - 1) {
        inputs[currentIndex + 1].focus();
    }
    if (event.key === 'Enter' && event.shiftKey   && currentIndex > 0) {
        inputs[currentIndex - 1].focus();
    }
}


onMounted(function(){
    stockIdicator();
})

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
                        <span v-if="indicator.total_suppliers">
                            {{ indicator.total_suppliers.length }}
                        </span>
                    </span>
                </div>
                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        Pedidos
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        8
                    </span>
                </div>
                <div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        QB's
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        {{ indicator.total_QB }}
                    </span>
                </div><div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        HB's
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        {{ indicator.total_HB }}
                    </span>
                </div><div class="d-flex align-items-center gap-2 border-blue-600 rounded-1">
                    <span class="text-white bg-blue-600 ps-1 pe-2">
                        Tallos
                    </span>
                    <span class="text-blue-600 ps-1 pe-2">
                        {{ indicator.total_stems }}
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
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">Tallos</th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">Proveedor</th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">Colores</th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50 d-flex justify-content-between gap-3">
                            <section class="pl-5">
                            </section>
                            <section class="d-flex gap-3 justify-content-between w-50">
                                <span>Productos</span>
                                <span>Tallos</span>
                                <span>Costo</span>
                                <span>Margen</span>
                                <span>Total</span>
                            </section>
                        </th>
                        <th class="p-0 bg-blue-600 bg-gradient fw-medium text-cyan-50">
                                <svg  xmlns="http://www.w3.org/2000/svg"  width="18"  height="18"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="1.5"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-settings"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M10.325 4.317c.426 -1.756 2.924 -1.756 3.35 0a1.724 1.724 0 0 0 2.573 1.066c1.543 -.94 3.31 .826 2.37 2.37a1.724 1.724 0 0 0 1.065 2.572c1.756 .426 1.756 2.924 0 3.35a1.724 1.724 0 0 0 -1.066 2.573c.94 1.543 -.826 3.31 -2.37 2.37a1.724 1.724 0 0 0 -2.572 1.065c-.426 1.756 -2.924 1.756 -3.35 0a1.724 1.724 0 0 0 -2.573 -1.066c-1.543 .94 -3.31 -.826 -2.37 -2.37a1.724 1.724 0 0 0 -1.065 -2.572c-1.756 -.426 -1.756 -2.924 0 -3.35a1.724 1.724 0 0 0 1.066 -2.573c-.94 -1.543 .826 -3.31 2.37 -2.37c1 .608 2.296 .07 2.572 -1.065z" /><path d="M9 12a3 3 0 1 0 6 0a3 3 0 0 0 -6 0" /></svg>
                        </th>
                    </tr>
                </thead>
                <tbody>
                        <tr v-for="item in my_stock" :key="item">
                            <td class="p-1 text-start ps-3">
                                {{ item.quantity }} {{ item.box_model }}
                            </td>
                            <td class="p-1 text-end">
                                {{ item.tot_stem_flower }}
                            </td>
                            <td class="p-1 text-start">
                                {{ item.partner.name }}
                                <i v-if="item.partner.is_profit_margin_included" class="text-info" title="Incluye margen de beneficio">
                                    <svg  xmlns="http://www.w3.org/2000/svg"  width="15"  height="15"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="1.5"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-pin-end"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M21 11v-5a1 1 0 0 0 -1 -1h-16a1 1 0 0 0 -1 1v12a1 1 0 0 0 1 1h9" /><path d="M19 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" /><path d="M10 13v-4h4" /><path d="M14 13l-4 -4" /></svg>
                                </i>
                            </td>
                            <td class="p-1">
                                <section v-for="box in item.box_items" :key="box" class="d-flex gap-1">
                                <div  class="d-flex gap-1">
                                        <small v-for="color in box.product_colors" :key="color" class="badge text-slate-500 border-sky-500" :class="colors[color]">
                                            {{ color }}
                                        </small>
                                    </div>
                                    </section>
                            </td>
                            <td class="p-1">
                                <section v-for="box in item.box_items" :key="box" class="text-end d-flex justify-content-end gap-2">
                                    <span>
                                        <small class="badge border-gray-300 text-gray-400">{{ box.product_id }}</small> {{ box.product_name }}
                                    </span>
                                    <span> {{ box.product_variety }} </span>
                                    <span class="text-slate-300">|</span>
                                    <input type="number" class="my-input-3 w-15 text-end" @keydown="event => handleKeydown(event, index, '.my-input-3')" @focus="selectText" v-model="qty_stem_flower">
                                    <span class="text-slate-300">|</span>
                                    <input type="number" class="my-input w-15 text-end" @keydown="event => handleKeydown(event, index, 'my-input')" @focus="selectText" v-model="box.stem_cost_price">
                                    <input type="number" class="my-input-2 w-15 text-end" @keydown="event => handleKeydown2(event, index, 'my-input-2')" @focus="selectText" v-model="box.margin">
                                    <span class="text-gray-600 fw-semibold border-gray-300 w-15 text-end">
                                        {{  (box.margin +  box.stem_cost_price).toFixed(2) }}
                                    </span>
                                </section>
                            </td>
                            <td class="p-1 text-center">
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
        border: 1px solid #ccc;
        border-radius: 2px;
        text-align: right;
    }
    .my-input-2 {
        border: 1px solid #ccc;
        border-radius: 2px;
        text-align: right;
    }
    .my-input-3 {
        border: 1px solid #ccc;
        border-radius: 2px;
        text-align: right;
    }
</style>