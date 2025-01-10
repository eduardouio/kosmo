import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";


export const useOrdersStore = defineStore("ordersStore", {
    state: () => ({
        customers:[],
        orders: [],
    }),
    actions:{
        async loadCustomers(){
            if (this.customers.length > 0) return;
            try{
              const response = await fetch(appConfig.urlAllCustomers);
              const data = await response.json();
              this.customers = data;
            }
            catch (error) {
              console.error('Error al cargar los clientes:', error);
              alert(`Hubo un error al cargar los clientes: ${error.message}`);
            }   
          },
    }
});