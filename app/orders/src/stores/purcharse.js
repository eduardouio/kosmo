import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";
import axios from "axios";

export const useSalesStore = defineStore("salesStore", {
  state: () => ({
    purcharses_by_order: [],
    sales: [],
    showViews: {
        listOrders: true,
        newOrder: false,
        singleOrder: false,
    },
  }),
  actions: {
    async loadSales(baseStore) {
      if (this.sales.length > 0) {
        baseStore.stagesLoaded++;
        return;
      }
      try {
        const response = await axios.get(
          appConfig.urlOrdersByStock + "?type=sale" ,
          {headers: appConfig.headers}
        );
        this.sales = response.data;
        baseStore.stagesLoaded++;
      } catch (error) {
        console.error("Error al cargar las ventas:", error);
        alert(`Hubo un error al cargar las ventas: ${error.message}`);
      }
    },
    async getOrdersByCustomerOrder(idCusomtrerOrder){
      console.log("Cargando informacion de compra de pedido " + idCusomtrerOrder);
      try {
        const reponse = await axios.get( appConfig.urlPurchaseOrdersByCustomerOrder.replace(
            "{id_customer_order}", idCusomtrerOrder
          ),
          {headers: appConfig.headers}
        )
        this.purcharses_by_order = reponse.data;
        console.log('Detalle de orde de compra' +  response.data);
      }catch{
        console.error("Error al cargar las ventas:", error);
        alert(`Hubo un error al cargar las ordenes de compra de esta venta: ${error.message}`);
      }
    },
  },
});
