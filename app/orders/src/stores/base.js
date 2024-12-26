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
        supliers:[],
        is_loading: true,
    }),
    actions: {
      async loadSupp(){
        console.log('Cargando datos Remotos');
        const response = await fetch(`${appConfig.apiBaseUrl}/api/colors/`);
        const data = await response.json();
        this.colors = data;
        this.is_loading = false;
      },
      loadSupliers(){
        console.log('Cargando datos Remotos');
        fetch(`${appConfig.apiBaseUrl}/api/supliers/`)
        .then(response => response.json())
        .then(data => {
          this.supliers = data;
        });
      },
      filterData(){
        console.log('Estamos en filterData');
        let data = this.colors;
        let filteredData = data.filter(item => item.stock > 0);
        return filteredData;
      }
    },
});