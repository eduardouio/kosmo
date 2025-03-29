import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";
import axios from "axios";

export const usePurchaseStore = defineStore("purchaseStore", {
  state: () => ({
    purcharses_by_order: [],
    selectedPurchase: {},
    limitsSelectedPurchase: [],
    sales: [],
  }),
  actions: {
    async loadSales(baseStore) {
      if (this.sales.length > 0) {
        baseStore.stagesLoaded++;
        return;
      }
      try {
        const response = await axios.get(
          appConfig.urlOrdersByStock + "?type=sale",
          { headers: appConfig.headers }
        );
        this.sales = response.data;
        baseStore.stagesLoaded++;
      } catch (error) {
        console.error("Error al cargar las ventas:", error);
        alert(`Hubo un error al cargar las ventas: ${error.message}`);
      }
    },
    async getOrdersByCustomerOrder(idCusomtrerOrder, baseStore) {
      console.log("Cargando detalle de orden de compra...");
      this.purcharses_by_order = [];
      try {
        const response = await axios.get(
          appConfig.urlPurchaseOrdersByCustomerOrder.replace(
            "{id_customer_order}",
            idCusomtrerOrder
          ),
          { headers: appConfig.headers }
        );
        this.purcharses_by_order = response.data;
        console.log("Detalle de orde de compra" + response.data);
        baseStore.stagesLoaded++;
      } catch(error) {
        console.error("Error al cargar las ventas:", error);
        alert(
          `Hubo un error al cargar las ordenes de compra de esta venta: ${error.message}`
        );
      }
    },
    selectedPurchaseId(id) {
      console.log("Seleccionando orden de compra con id: " + id);
      this.selectedPurchase = this.sales.find(
        (purchase) => purchase.order.id == id
      );
    },
    async updateSupplierOrder() {
      console.log("Actualizando orden de compra...");
      try {
        const response = await axios.post(
          appConfig.urlUpdateSupplierOrder,
          this.selectedPurchase,
          { headers: appConfig.headers }
        );
        console.log("Orden de compra actualizada: " + response.data);
        return response.data;
      } catch (error) {
        console.error("Error al actualizar la orden de compra:", error);
        alert(
          `Hubo un error al actualizar la orden de compra: ${error.message}`
        );
      }
    },
    async confirmOrder() {
      console.log("Confirmando orden de compra...");
      try {
        const response = await axios.post(          
          appConfig.urlConfirmOrder,
          this.selectedPurchase.order.id,
          { headers: appConfig.headers }
        );
        console.log("Orden de compra confirmada: " + response.data);
        return response.data;
      } catch (error) {
        console.error("Error al confirmar la orden de compra:", error);
        alert(
          `Hubo un error al confirmar la orden de compra: ${error.message}`
        );
      }
    },
    async cancellOrder() {
      console.log("Cancelando orden de compra...");
      try {
        const response = await axios.post(appConfig.urlCancelSupplierOrder,
          {id_order: this.selectedPurchase.order.id},
          { headers: appConfig.headers }
        );
        console.log("Orden de compra cancelada: " + response.data);
        return response.data;
      } catch (error) {
        console.error("Error al cancelar la orden de compra:", error);
        alert(
          `Hubo un error al cancelar la orden de compra: ${error.message}`
        );
      }
    },
    async createInvoice() {
      console.log('Creando factura...');
      try {
        const response = await axios.post(
          appConfig.urlCreateInvoiceOrder,
          { order_id: this.selectedPurchase.order.id },
          { headers: appConfig.headers }
        );
        console.log("Factura creada: " + response.data);
        this.selectedPurchase.order.status = "FACTURADO";
        this.selectedPurchase.is_invoiced = true;
        this.selectedPurchase.id_invoice = response.invoice_id;
        this.selectedPurchase.order.num_invoice = response.data.num_invoice;
        return response.data;
      } catch (error) {
        console.error("Error al crear la factura:", error);
        alert(`Hubo un error al crear la factura: ${error.message}`);
      }
    },
  },
});
