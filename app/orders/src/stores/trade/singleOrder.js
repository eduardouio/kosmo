import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";
import axios from "axios";


export const useSingleOrderStore = defineStore("singleOrderStore", {
  state: () => ({
    order: {},
    orderLines: [],
    orderLine: {},
    orderLineId: null,
    orderLineIndex: null,
    orderLineSelected: {},
    orderLinesSelected: [],
    orderLinesDeleted: [],
  }),
  actions: {
    async loadOrder(id, baseStore) {
      console.log("Cargando orden de compra...");
      this.order = {};
      this.orderLines = [];
      try {
        const response = await axios.get(
          appConfig.urlOrdersByStock.replace("{id}", id),
          { headers: appConfig.headers }
        );
        this.order = response.data;
        this.orderLines = response.data.lines;
        console.log("Orden de compra cargada", response.data);
        baseStore.stagesLoaded++;
      } catch (error) {
        console.error("Error al cargar la orden de compra:", error);
        alert(`Hubo un error al cargar la orden de compra: ${error.message}`);
      }
    },
},
});