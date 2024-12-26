import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";


export const useBaseStore = defineStore("baseStore", {
    state: () => ({
        colors: {
                'AMARILLO': 'bg-yellow-400 bg-gradient',
                'CREMA': 'bg-amber-400 bg-gradient',
                'ROJO': 'bg-red-400 bg-gradient',
                'BLANCO': 'bg-light',
                'TINTURADO': 'bg-gray-400 bg-gradient',
                'NARANJA': 'bg-orange-400 bg-gradient',
        },
        suppliers:[],
        isLoading: true,
    }),
    actions: {
      async loadSuppliers(){
        if (this.suppliers.length > 0) return;
        const response = await fetch(appConfig.urlAllSuppliers);
        const data = await response.json();
        this.suppliers = data;
        this.isLoading = false;
      },
    },
});