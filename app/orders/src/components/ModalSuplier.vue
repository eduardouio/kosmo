<script setup>
const props = defineProps(['suplier']);
</script>

<template>
    <div class="modal fade modal-lg" id="suplierModal" tabindex="-1" aria-labelledby="suplierModal" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content" v-if="suplier">
                <div class="modal-header bg-kosmo-primary p-1 text-white">
                    <span class="modal-title fs-6 ps-3" id="suplierModal">
                        # {{ suplier.id }} - {{ suplier.name }}
                    </span>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="row border shadow">
                        <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Nombre:</div>
                        <div class="col-7 border-bottom">{{ suplier.name }}</div>

                        <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Tax ID:</div>
                        <div class="col-7 border-bottom">{{ suplier.business_tax_id }}</div>

                        <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Dirección:</div>
                        <div class="col-7 border-bottom">{{ suplier.address }}</div>

                        <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Ciudad:</div>
                        <div class="col-7 border-bottom">{{ suplier.city }}</div>

                        <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Margen base:
                        </div>
                        <div class="col-7 border-bottom">{{ suplier.default_profit_margin }}</div>

                        <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Incluir margen:
                        </div>
                        <div class="col-7 border-bottom">
                            {{ suplier.is_profit_margin_included ? 'Sí' : 'No' }}
                        </div>

                        <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Sitio web:</div>
                        <div class="col-7 border-bottom">
                            <a v-if="suplier.website" :href="suplier.website" target="_blank">{{ suplier.website }}</a>
                        </div>

                        <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Crédito:</div>
                        <div class="col-7 border-bottom">{{ suplier.credit_term }}</div>

                        <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Skype:</div>
                        <div class="col-7 border-bottom">{{ suplier.skype }}</div>

                        <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Email:</div>
                        <div class="col-7 border-bottom">{{ suplier.email }}</div>

                        <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Teléfono:</div>
                        <div class="col-7 border-bottom">{{ suplier.phone }}</div>

                        <div class="col-5 border-bottom border-end text-gray-100 text-end bg-gray-500">Activo:</div>
                        <div class="col-7 border-bottom">
                            {{ suplier.is_active ? 'Activo' : 'Inactivo' }}
                        </div>
                    </div>
                </div>
                <div class="modal-footer bg-secondary bg-gradient p-1">

                </div>
            </div>
        </div>
    </div>
</template>
