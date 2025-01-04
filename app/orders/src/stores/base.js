import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";


export const useBaseStore = defineStore("baseStore", {
    state: () => ({
        colors: {
          'AMARILLO' : 'text-yellow-400',
          'AZUL' : 'text-blue-400',
          'BLANCO' : 'text-light',
          'CAFE' : '.bg-brown-400',
          'CREMA' : 'text-amber-400',
          'MORADO' : 'text-violet-400',
          'NARANJA' : 'text-orange-400',
          'ROJO' : 'text-red-400',
          'ROSADO' : 'text-pink-400',
          'TINTURADO' : 'text-indigo-400',
          'VERDE' : 'text-green-400',
          'OTRO' : 'text-gray-400',
        },
        suppliers:[],
        isLoading: true,
        idStock: appConfig.idStock,
    }),
    actions: {
      async loadSuppliers(){
        if (this.suppliers.length > 0) return;
        const response = await fetch(appConfig.urlAllSuppliers);
        const data = await response.json();
        this.suppliers = data;
        this.isLoading = false;
      },
      setLoading(value){
        this.isLoading = value;
      }
    },
});