import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";


export const useBaseStore = defineStore("baseStore", {
    state: () => ({
        colors: {
          'AMARILLO' : 'text-yellow-500',
          'AZUL' : 'text-blue-500',
          'BLANCO' : 'text-light',
          'CAFE' : '.bg-brown-400',
          'CREMA' : 'text-amber-500',
          'MORADO' : 'text-violet-500',
          'NARANJA' : 'text-orange-500',
          'ROJO' : 'text-red-500',
          'ROSADO' : 'text-pink-500',
          'TINTURADO' : 'text-lime-500',
          'VERDE' : 'text-green-500',
          'OTRO' : 'text-gray-500',
        },
        bgColor: {
          'AMARILLO' : 'bg-yellow-500',
          'AZUL' : 'bg-blue-500',
          'BLANCO' : 'bg-light',
          'CAFE' : 'bg-brown-400',
          'CREMA' : 'bg-amber-500',
          'MORADO' : 'bg-violet-500',
          'NARANJA' : 'bg-orange-500',
          'ROJO' : 'bg-red-500',
          'ROSADO' : 'bg-pink-400',
          'TINTURADO' : 'bg-lime-500',
          'VERDE' : 'bg-green-500',
          'OTRO' : 'bg-gray-500',
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