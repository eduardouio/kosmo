<script setup>
import {onMounted, ref, computed} from 'vue'

import {useBaseStore} from '@/stores/baseStore.js'
import { useSingleOrderStore } from '@/stores/trade/singleOrderStore.js'

import AutocompleteCustomer from '@/components/Sotcks/AutocompleteCustomer.vue'
import Loader from '@/components/Sotcks/Loader.vue'

const baseStore = useBaseStore()
const stagesToLoad = ref(3)

// computed
const isLoading = computed(() => {
  return baseStore.stagesLoaded != stagesToLoad.value
})

// mouted
onMounted(() => {
  baseStore.loadSuppliers()
  baseStore.loadProducts()
  baseStore.loadCustomers(true)
})

</script>
<template>
  <div class="container-fluid">
    <Loader v-if="isLoading" />
    <div class="bg-light py-4">
      <div class="container bg-white shadow-lg border border-2 border-warning rounded-3 p-4 mx-auto" style="max-width: 1200px;">
        <!-- Encabezado -->
        <div class="row mb-4 align-items-center">
          <div class="col-7">
            <img src="https://kosmoflowers.com/wp-content/uploads/2022/07/Mesa-de-trabajo-6.svg" class="img-fluid" style="height: 60px"/>
          </div>
          <div class="col-5">
            <div class="border border-2 border-warning p-2 rounded">
              <div class="d-flex justify-content-end align-items-center mb-1">
                <span class="small fw-bold me-2">PEDIDO:</span>
                <span class="text-danger fs-4">KOSMO-001</span>
              </div>
              <div class="d-flex justify-content-end align-items-center border-top border-success pt-1">
                <span class="small fw-bold me-2">FECHA:</span>
                <span class="fs-4">15/04/2025</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Información de la empresa -->
        <div class="row mb-3">
          <div class="col-12">
            <div class="border border-2 border-warning p-2 rounded">
              <div class="row">
                <div class="col-6">
                  <div class="small mt-2"><strong>Roses Grown by:</strong> KOSMO FLOWERS</div>
                  <div class="small"><strong>Address:</strong> Tupigachi - Tabacundo</div>
                  <div class="small"><strong>Country:</strong> ECUADOR</div>
                </div>
                <div class="col-6 text-end">
                  <p class="small mt-2"><strong>Email:</strong> invoices@kosmoflowers.com</p>
                  <p class="small"><strong>Phone:</strong> (+593) 0999475741</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Información del cliente y adicional -->
        <div class="row mb-4">
          <div class="col-7">
            <div class="border border-2 border-warning p-3 rounded h-100">
              <h6 class="fw-bold mb-3">Información del Cliente</h6>
              <div class="mb-3">
                <select class="form-select">
                  <option value="">Seleccione un cliente</option>
                  <option value="1">Cliente 1</option>
                  <option value="2">Cliente 2</option>
                  <option value="3">Cliente 3</option>
                </select>
              </div>
              <div>
                <p class="small mb-1"><strong>Dirección:</strong> Calle Principal #123</p>
                <p class="small mb-1"><strong>Ciudad - País:</strong> Miami - USA</p>
                <div class="d-flex justify-content-between">
                  <p class="small mb-1"><strong>Email:</strong> cliente@example.com</p>
                  <p class="small mb-1"><strong>Crédito:</strong> 30 Días</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tabla de productos -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="table-responsive">
              <table class="table table-bordered table-sm">
                <thead class="bg-warning bg-opacity-25">
                  <tr class="text-center small">
                    <th>CAJAS</th>
                    <th>TIPO</th>
                    <th>VARIEDAD</th>
                    <th>LARGO</th>
                    <th>TALLOS/RAMO</th>
                    <th>TOTAL RAMOS</th>
                    <th>TOTAL TALLOS</th>
                    <th>PRECIO U. $</th>
                    <th>TOTAL $</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <!-- Formulario para agregar items -->
                  <tr>
                    <td>
                      <input type="number" class="form-control form-control-sm" min="1">
                    </td>
                    <td>
                      <select class="form-select form-select-sm">
                        <option>HB</option>
                        <option>FB</option>
                        <option>QB</option>
                      </select>
                    </td>
                    <td colspan="7">
                      <div class="d-flex gap-2 align-items-center">
                        <select class="form-control form-control-sm" style="width: 200px">
                          <option value="">Seleccione un producto</option>
                          <option value="1">Rosa - Freedom</option>
                          <option value="2">Rosa - Explorer</option>
                        </select>
                        <input type="number" class="form-control form-control-sm" placeholder="Largo" style="width: 80px">
                        <input type="number" class="form-control form-control-sm" placeholder="Tallos/Ramo" style="width: 100px">
                        <input type="number" class="form-control form-control-sm" placeholder="Total Ramos" style="width: 100px">
                        <input type="number" class="form-control form-control-sm" placeholder="Total Tallos" style="width: 100px">
                        <input type="number" class="form-control form-control-sm" placeholder="Precio U." style="width: 100px">
                        <div class="form-control form-control-sm text-end" style="width: 100px">
                          0.00
                        </div>
                      </div>
                    </td>
                    <td class="text-center">
                      <button class="btn btn-primary btn-sm">+</button>
                    </td>
                  </tr>

                  <!-- Items agregados - ejemplo estático -->
                  <tr class="text-end small">
                    <td class="text-center" rowspan="2">
                      2
                    </td>
                    <td class="text-center" rowspan="2">
                      HB
                    </td>
                    <td>Rosa - Freedom</td>
                    <td>50</td>
                    <td>25</td>
                    <td>8</td>
                    <td>200</td>
                    <td>0.45</td>
                    <td>90.00</td>
                    <td class="text-center" rowspan="2">
                      <button class="btn btn-danger btn-sm">
                        <i class="bi bi-trash"></i>
                      </button>
                    </td>
                  </tr>
                  <tr class="text-end small">
                    <td>Rosa - Explorer</td>
                    <td>60</td>
                    <td>25</td>
                    <td>8</td>
                    <td>200</td>
                    <td>0.50</td>
                    <td>100.00</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Totales -->
        <div class="row mb-4">
          <div class="col-6">
            <div class="border border-secondary p-3 rounded">
              <div class="row">
                <div class="col-8 text-end"><strong>TOTAL HB:</strong></div>
                <div class="col-4 text-end">2</div>
              </div>
              <div class="row">
                <div class="col-8 text-end"><strong>TOTAL QB:</strong></div>
                <div class="col-4 text-end">0</div>
              </div>
              <div class="row">
                <div class="col-8 text-end"><strong>TOTAL FB:</strong></div>
                <div class="col-4 text-end">0</div>
              </div>
              <div class="row">
                <div class="col-8 text-end"><strong>TOTAL TALLOS:</strong></div>
                <div class="col-4 text-end">400</div>
              </div>
            </div>
          </div>
          <div class="col-6">
            <div class="bg-light bg-gradient rounded shadow-sm p-3">
              <div class="row">
                <div class="col-7 text-end border-end text-success"><strong>Costo:</strong></div>
                <div class="col-5 text-end text-success">$190.00</div>
              </div>
              <div class="row">
                <div class="col-7 text-end border-end text-success"><strong>Margen:</strong></div>
                <div class="col-5 text-end text-success">$38.00</div>
              </div>
              <div class="row">
                <div class="col-7 text-end border-end text-success"><strong>Total Factura:</strong></div>
                <div class="col-5 text-end text-success fs-5">$228.00</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Botón guardar -->
        <div class="row">
          <div class="col-12 text-end">
            <button class="btn btn-default">
              <i class="bi bi-save me-2"></i>
              Guardar Factura
            </button>
          </div>
        </div>

        <!-- Mensajes de error -->
        <div class="row mt-3">
          <div class="col-12">
            <div class="alert alert-danger d-flex align-items-center">
              <i class="bi bi-exclamation-triangle me-2"></i>
              Error de ejemplo: Seleccione un cliente antes de guardar
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>