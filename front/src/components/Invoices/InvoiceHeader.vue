<script setup lang="ts">
import ModalFormItemInvoiceVue from '@/components/Invoices/ModalFormItemInvoice.vue'
import {
  IconPlus, IconEdit, IconPrinter,
  IconTrash,IconCheck, IconCancel
} from '@tabler/icons-vue'

</script>
<template>
   <div class="mx-auto p-4 border rounded-md">
    <!-- Cabecera -->
    <div class="flex justify-between mb-4">
      <h1 class="text-3xl font-bold text-primary">INVOICE</h1>
      <h1 class="text-3xl font-bold text-danger">No. 3837</h1>
    </div>

    <!-- Datos del Cliente -->
    <div class="pb-4  mb-4 border-b">
        <div class="flex justify-end">
            <button class="btn btn-sm bg-blue-900">
              <IconPlus :size="24" stroke-width="1.5" class="text-withe"/>
              New Customer
            </button>
        </div>
      <p><strong>Name:</strong> Juan Pérez</p>
      <p><strong>Address:</strong> Calle Falsa 123, Ciudad, País</p>
      <p><strong>Phone:</strong> +123456789</p>
      <p><strong>Email:</strong> juanperez@example.com</p>
    </div>

    <!-- Detalle de la Factura -->
    <div class="mb-8">
      <div class="flex justify-end p-2">
                <ModalFormItemInvoiceVue/>
      </div>
      <div class="overflow-x-auto">
        <table class="table">
          <!-- Encabezado de la tabla -->
          <thead>
            <tr class="text-center">
              <th class="w-1/12">#</th>
              <th class="w-7/12">Item</th>
              <th class="w-1/12">Qty</th>
              <th class="w-1/12">Cost</th>
              <th class="w-1/12">Total</th>
            </tr>
          </thead>
          <tbody>
            <!-- Los items de la factura irían aquí -->
            <tr>
              <td>1</td>
              <td>Producto 1</td>
              <td class="text-end">2</td>
              <td class="text-end">100.00</td>
              <td>
                  <div class="flex justify-between">
                    <IconEdit stroke-width="1.5" class="text-blue-800 h-5 w-5"/>
                    <IconTrash stroke-width="1.5" class="text-error h-5 w-5"/>
                    <span>200.00</span>
                  </div>
              </td>
            </tr>
            <tr>
              <td>2</td>
              <td>Producto 1</td>
              <td class="text-end">2</td>
              <td class="text-end">100.00</td>
              <td>
                  <div class="flex justify-between">
                    <IconEdit stroke-width="1.5" class="text-blue-800 h-5 w-5"/>
                    <IconTrash stroke-width="1.5" class="text-error h-5 w-5"/>
                    <span>200.00</span>
                  </div>
              </td>
            </tr>
            <tr>
              <th colspan="4" class="text-end">Sum:</th>
              <th class="bg-slate-200 text-end">200.00 USD</th>
            </tr>
            <tr>
              <th colspan="4" class="text-end">Dsc: <span class="text-error">(-)</span>
              </th>
              <th class="bg-orange-100 text-end">
                <div class="flex justify-between">
                  <IconTrash stroke-width="1.5" class="text-error h-5 w-5"/>
                  <span class="text-error">0.00</span>
                </div>
              </th>
            </tr>
            <tr>
              <th colspan="4" class="text-end">Total:</th>
              <th class="bg-green-200 text-end text-success">  200.00 USD</th>
            </tr>
            <!-- Añadir más productos según sea necesario -->
          </tbody>
        </table>
      </div>
    </div>

    <!-- Total de la Factura -->
    <div class="flex justify-between">
      <div class="flex gap-3">
        <button class="btn bg-blue-800 btn-sm">
        <IconPrinter stroke-width="1.5" class="w-5 h-5"/>
        Print
      </button>
      <button class="btn bg-blue-800 btn-sm">
        <IconCheck stroke-width="1.5" class="w-5 h-5"/>
        Save
      </button>
      <button class="btn bg-orange-800 btn-sm">
        <IconCancel stroke-width="1.5" class="w-5 h-5"/>
        Cancel
      </button>
      </div>
      <div class="text-2xl font-bold text-success text-end">
        <span class="p-2">Total:</span>
        <span class="border border-slate-300 p-2 rounded-lg">
          200.00 USD
        </span>
      </div>
    </div>
  </div>
</template>