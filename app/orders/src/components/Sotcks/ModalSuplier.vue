<script setup>
import { IconX } from '@tabler/icons-vue';
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
                    <div class="row border shadow fs-6">
                        <div class="col-5 border-bottom border-end text-end bg-gray-300">Nombre:</div>
                        <div class="col-7 border-bottom">{{ suplier.name }}</div>
                        <div class="col-5 border-bottom border-end text-end bg-gray-300">Tax ID:</div>
                        <div class="col-7 border-bottom">{{ suplier.business_tax_id }}</div>
                        <div class="col-5 border-bottom border-end text-end bg-gray-300">Dirección:</div>
                        <div class="col-7 border-bottom">{{ suplier.address }}</div>
                        <div class="col-5 border-bottom border-end text-end bg-gray-300">Ciudad:</div>
                        <div class="col-7 border-bottom">{{ suplier.city }}</div>
                        <div class="col-5 border-bottom border-end text-end bg-gray-300">Margen base:
                        </div>
                        <div class="col-7 border-bottom">{{ suplier.default_profit_margin }}</div>
                        <div class="col-5 border-bottom border-end text-end bg-gray-300">Incluir margen:
                        </div>
                        <div class="col-7 border-bottom">
                            {{ suplier.is_profit_margin_included ? 'Sí' : 'No' }}
                        </div>
                        <div class="col-5 border-bottom border-end text-end bg-gray-300">Sitio web:</div>
                        <div class="col-7 border-bottom">
                            <a v-if="suplier.website" :href="suplier.website" target="_blank">{{ suplier.website }}</a>
                        </div>
                        <div class="col-5 border-bottom border-end text-end bg-gray-300">Crédito:</div>
                        <div class="col-7 border-bottom">{{ suplier.credit_term }}</div>

                        <div class="col-5 border-bottom border-end text-end bg-gray-300">Skype:</div>
                        <div class="col-7 border-bottom">{{ suplier.skype }}</div>

                        <div class="col-5 border-bottom border-end text-end bg-gray-300">Email:</div>
                        <div class="col-7 border-bottom">{{ suplier.email }}</div>

                        <div class="col-5 border-bottom border-end text-end bg-gray-300">Teléfono:</div>
                        <div class="col-7 border-bottom">{{ suplier.phone }}</div>

                        <div class="col-5 border-bottom border-end text-end bg-gray-300">Activo:</div>
                        <div class="col-7 border-bottom">
                            {{ suplier.is_active ? 'Activo' : 'Inactivo' }}
                        </div>
                    </div>
                </div>
                <div class="modal-footer bg-secondary bg-gradient p-1">
                    <button class="btn bnt-sm btn-default" data-bs-dismiss="modal">
                        <IconX  size="20" stroke="1.5" />
                        Cerrar
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
