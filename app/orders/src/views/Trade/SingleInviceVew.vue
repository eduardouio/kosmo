<script setup>
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useBaseStore } from '@/stores/base';
import { useOrdersStore } from '@/stores/orders';
import { IconTrash, IconDeviceFloppy, IconAlertTriangle } from '@tabler/icons-vue';

const route = useRoute();
const baseStore = useBaseStore();
const ordersStore = useOrdersStore();

const orderForm = ref({
  partner: null,
  type_document: 'FAC_VENTA',
  num_invoice: '',
  date: new Date().toISOString().split('T')[0],
due_date: null,
  delivery_date: null,
  awb: '',
  dae_export: '',
  hawb: '',
  cargo_agency: '',
  weight: 0,
  status: 'PENDIENTE',
  order_details: [],
});

const newBoxItem = ref({
  product: null,
  length: '',
  qty_stem_flower: 0,
  stem_cost_price: 0.00,
  profit_margin: 0.06,
  commission: 0.00,
  total_bunches: 0,
  stems_bunch: 0
});

const boxTypes = ['QB', 'HB', 'FB'];
const currentBox = ref({
  box_model: 'QB',
  quantity: 1,
  box_items: [],
  tot_stem_flower: 0,
  line_price: 0,
  line_margin: 0,
  line_total: 0,
  line_commission: 0
});

const errors = ref({
  partner: false,
  box_items: false,
  message: ''
});

// Métodos
const addBoxItem = () => {
  if (!validateBoxItem()) return;
  
  currentBox.value.box_items.push({...newBoxItem.value});
  // Reiniciar valores
  newBoxItem.value = {
    product: null,
    length: '',
    qty_stem_flower: 0,
    stem_cost_price: 0.00,
    profit_margin: 0.06,
    commission: 0.00,
    total_bunches: 0,
    stems_bunch: 0
  };
  
  calcTotals();
};

const validateBoxItem = () => {
  if (!newBoxItem.value.product || 
      !newBoxItem.value.length || 
      newBoxItem.value.qty_stem_flower <= 0 || 
      newBoxItem.value.stem_cost_price <= 0) {
    errors.value.message = 'Todos los campos son requeridos y los valores deben ser mayores a 0';
    errors.value.box_items = true;
    return false;
  }
  errors.value.box_items = false;
  errors.value.message = '';
  return true;
};

const addBoxToOrder = () => {
  if (currentBox.value.box_items.length === 0) {
    errors.value.message = 'Debe agregar al menos un item a la caja';
    return;
  }
  orderForm.value.order_details.push({...currentBox.value});
  // Reiniciar la caja actual
  currentBox.value = {
    box_model: 'QB',
    quantity: 1,
    box_items: [],
    tot_stem_flower: 0,
    line_price: 0,
    line_margin: 0,
    line_total: 0,
    line_commission: 0
  };
  calcTotals();
};

const removeBoxItem = (index) => {
  currentBox.value.box_items.splice(index, 1);
  calcTotals();
};

const removeOrderDetail = (index) => {
  orderForm.value.order_details.splice(index, 1);
  calcTotals();
};

const calcTotals = () => {
  let totalPrice = 0;
  let totalMargin = 0;
  let totalStems = 0;
  let qbTotal = 0;
  let hbTotal = 0;
  let fbTotal = 0;

  orderForm.value.order_details.forEach(detail => {
    if (detail.box_model === 'QB') qbTotal += detail.quantity;
    if (detail.box_model === 'HB') hbTotal += detail.quantity;
    if (detail.box_model === 'FB') fbTotal += detail.quantity;

    detail.box_items.forEach(item => {
      const itemTotal = item.qty_stem_flower * item.stem_cost_price * detail.quantity;
      const itemMargin = item.qty_stem_flower * item.profit_margin * detail.quantity;
      totalPrice += itemTotal;
      totalMargin += itemMargin;
      totalStems += item.qty_stem_flower * detail.quantity;
    });
  });

  orderForm.value.total_price = totalPrice;
  orderForm.value.total_margin = totalMargin;
  orderForm.value.tot_stem_flower = totalStems;
  orderForm.value.qb_total = qbTotal;
  orderForm.value.hb_total = hbTotal;
  orderForm.value.fb_total = ((qbTotal / 2) + hbTotal) / 2;
};

const formatNumber = (event) => {
  let value = event.target.value;
  value = value.replace(',', '.');
  if (value === '' || value === '.' || value === ',' || isNaN(value) || value === ' ' || value === '0') {
    event.target.value = '0.00';
    return;
  }
  event.target.value = parseFloat(value).toFixed(2);
  calcTotals();
};

const saveOrder = async () => {
  if (!orderForm.value.partner) {
    errors.value.partner = true;
    errors.value.message = 'Debe seleccionar un cliente';
    return;
  }
  if (orderForm.value.order_details.length === 0) {
    errors.value.message = 'Debe agregar al menos una caja al pedido';
    return;
  }
  // Aquí iría la lógica para guardar el pedido
  console.log(orderForm.value);
};

</script>

<template>
  <div class="container-fluid">
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
                <span class="text-danger fs-4">{{ orderForm.num_invoice }}</span>
              </div>
              <div class="d-flex justify-content-end align-items-center border-top border-success pt-1">
                <span class="small fw-bold me-2">FECHA:</span>
                <span class="fs-4">{{ orderForm.date }}</span>
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
                <select class="form-select" v-model="orderForm.partner" :class="{ 'is-invalid': errors.partner }">
                  <option value="">Seleccione un cliente</option>
                  <option v-for="customer in ordersStore.customers" :key="customer.id" :value="customer">
                    {{ customer.name }}
                  </option>
                </select>
              </div>
              <div v-if="orderForm.partner">
                <p class="small mb-1"><strong>Dirección:</strong> {{ orderForm.partner.address }}</p>
                <p class="small mb-1"><strong>Ciudad - País:</strong> {{ orderForm.partner.city }} - {{ orderForm.partner.country }}</p>
                <div class="d-flex justify-content-between">
                  <p class="small mb-1"><strong>Email:</strong> {{ orderForm.partner.email }}</p>
                  <p class="small mb-1"><strong>Crédito:</strong> {{ orderForm.partner.credit_term }} Días</p>
                </div>
              </div>
            </div>
          </div>
          <div class="col-5">
            <div class="border border-2 border-warning p-3 rounded h-100">
              <h6 class="fw-bold mb-3 text-secondary">Información Adicional</h6>
              <div class="mb-2">
                <label class="form-label small">Agencia de Carga:</label>
                <input type="text" class="form-control form-control-sm" v-model="orderForm.cargo_agency">
              </div>
              <div class="mb-2">
                <label class="form-label small">M.A.W.B.:</label>
                <input type="text" class="form-control form-control-sm" v-model="orderForm.awb">
              </div>
              <div class="mb-2">
                <label class="form-label small">H.A.W.B.:</label>
                <input type="text" class="form-control form-control-sm" v-model="orderForm.hawb">
              </div>
              <div class="mb-2">
                <label class="form-label small">DAE USA:</label>
                <input type="text" class="form-control form-control-sm" v-model="orderForm.dae_export">
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
                      <input type="number" class="form-control form-control-sm" v-model="currentBox.quantity" min="1">
                    </td>
                    <td>
                      <select class="form-select form-select-sm" v-model="currentBox.box_model">
                        <option v-for="type in boxTypes" :key="type" :value="type">{{ type }}</option>
                      </select>
                    </td>
                    <td colspan="7">
                      <div class="d-flex gap-2 align-items-center">
                        <select class="form-control form-control-sm" v-model="newBoxItem.product" style="width: 200px">
                          <option value="">Seleccione un producto</option>
                          <option v-for="product in baseStore.products" :key="product.id" :value="product">
                            {{ product.name }} - {{ product.variety }}
                          </option>
                        </select>
                        <input type="number" class="form-control form-control-sm" v-model="newBoxItem.length" placeholder="Largo" style="width: 80px">
                        <input type="number" class="form-control form-control-sm" v-model="newBoxItem.stems_bunch" placeholder="Tallos/Ramo" style="width: 100px">
                        <input type="number" class="form-control form-control-sm" v-model="newBoxItem.total_bunches" placeholder="Total Ramos" style="width: 100px">
                        <input type="number" class="form-control form-control-sm" v-model="newBoxItem.qty_stem_flower" placeholder="Total Tallos" style="width: 100px">
                        <input type="number" class="form-control form-control-sm" v-model="newBoxItem.stem_cost_price" placeholder="Precio U." style="width: 100px" @change="formatNumber">
                        <div class="form-control form-control-sm text-end" style="width: 100px">
                          {{ (newBoxItem.stem_cost_price * newBoxItem.qty_stem_flower).toFixed(2) }}
                        </div>
                      </div>
                    </td>
                    <td class="text-center">
                      <button class="btn btn-primary btn-sm" @click="addBoxItem">+</button>
                    </td>
                  </tr>

                  <!-- Items agregados -->
                  <template v-for="(box, boxIndex) in orderForm.order_details" :key="boxIndex">
                    <template v-for="(item, itemIndex) in box.box_items" :key="itemIndex">
                      <tr class="text-end small">
                        <td class="text-center" v-if="itemIndex === 0" :rowspan="box.box_items.length">
                          {{ box.quantity }}
                        </td>
                        <td class="text-center" v-if="itemIndex === 0" :rowspan="box.box_items.length">
                          {{ box.box_model }}
                        </td>
                        <td>{{ item.product.name }} - {{ item.product.variety }}</td>
                        <td>{{ item.length }}</td>
                        <td>{{ item.stems_bunch }}</td>
                        <td>{{ item.total_bunches }}</td>
                        <td>{{ item.qty_stem_flower }}</td>
                        <td>{{ item.stem_cost_price }}</td>
                        <td>{{ (item.stem_cost_price * item.qty_stem_flower).toFixed(2) }}</td>
                        <td class="text-center" v-if="itemIndex === 0" :rowspan="box.box_items.length">
                          <button class="btn btn-danger btn-sm" @click="removeOrderDetail(boxIndex)">
                            <IconTrash size="16"/>
                          </button>
                        </td>
                      </tr>
                    </template>
                  </template>
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
                <div class="col-4 text-end">{{ orderForm.hb_total || 0 }}</div>
              </div>
              <div class="row">
                <div class="col-8 text-end"><strong>TOTAL QB:</strong></div>
                <div class="col-4 text-end">{{ orderForm.qb_total || 0 }}</div>
              </div>
              <div class="row">
                <div class="col-8 text-end"><strong>TOTAL FB:</strong></div>
                <div class="col-4 text-end">{{ orderForm.fb_total || 0 }}</div>
              </div>
              <div class="row">
                <div class="col-8 text-end"><strong>TOTAL TALLOS:</strong></div>
                <div class="col-4 text-end">{{ orderForm.tot_stem_flower || 0 }}</div>
              </div>
            </div>
          </div>
          <div class="col-6">
            <div class="bg-light bg-gradient rounded shadow-sm p-3">
              <div class="row">
                <div class="col-7 text-end border-end text-success"><strong>Costo:</strong></div>
                <div class="col-5 text-end text-success">${{ orderForm.total_price?.toFixed(2) || '0.00' }}</div>
              </div>
              <div class="row">
                <div class="col-7 text-end border-end text-success"><strong>Margen:</strong></div>
                <div class="col-5 text-end text-success">${{ orderForm.total_margin?.toFixed(2) || '0.00' }}</div>
              </div>
              <div class="row">
                <div class="col-7 text-end border-end text-success"><strong>Total Factura:</strong></div>
                <div class="col-5 text-end text-success fs-5">${{ (orderForm.total_price + orderForm.total_margin)?.toFixed(2) || '0.00' }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Botón guardar -->
        <div class="row">
          <div class="col-12 text-end">
            <button class="btn btn-default" @click="saveOrder">
              <IconSave class="me-2"/>
              Guardar Factura
            </button>
          </div>
        </div>

        <!-- Mensajes de error -->
        <div v-if="errors.message" class="row mt-3">
          <div class="col-12">
            <div class="alert alert-danger d-flex align-items-center">
              <IconAlertTriangle class="me-2" />
              {{ errors.message }}
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.form-control, .form-select {
  font-size: 0.875rem;
}

.table {
  font-size: 0.875rem;
}
</style>