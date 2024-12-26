<script setup>
</script>

<template>
    <div class="bg-light border-end vh-100 d-flex flex-column justify-content-start p-2">
        <router-link to="/import" class="text-decoration-none mb-2">
            <div class="border border-blue-600 rounded-1 p-1 text-end text-slate-600 fw-semibold hover-opacity">
                Importar Disponibilidad
            </div>
        </router-link>
        <router-link to="/" class="text-decoration-none mb-2">
            <div class="border border-blue-600 rounded-1 p-1 text-end text-slate-600 fw-semibold hover-opacity">
                Disponibilidad Actual
            </div>
        </router-link>

        <router-link to="/" class="text-decoration-none mb-2">
            <div class="border border-orange-600 rounded-1 p-1 text-end text-slate-600 fw-semibold hover-opacity">
                Pedidos de Clientes
            </div>
        </router-link>

        <router-link to="/" class="text-decoration-none">
            <div class="border border-slate-600 rounded-1 p-1 text-end text-slate-600 fw-semibold hover-opacity">
                Compras a Proveedor
            </div>
        </router-link>
    </div>
</template>

<style scoped>
.hover-opacity:hover {
  opacity: 0.8;
  background-color: rgba(0, 0, 0, 0.1);
}
</style>
