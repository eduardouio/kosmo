import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";
import axios from "axios";

export const useSalesStore = defineStore("salesStore", {
  state: () => ({
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
          appConfig.urlOrdersByStock + "?type=sale"
        );
        this.sales = response.data;
        baseStore.stagesLoaded++;
      } catch (error) {
        console.error("Error al cargar las ventas:", error);
        alert(`Hubo un error al cargar las ventas: ${error.message}`);
      }
    },
  },
});
