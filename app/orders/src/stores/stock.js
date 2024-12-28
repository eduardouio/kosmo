import { defineStore } from 'pinia';
import { appConfig } from '@/AppConfig';


export const useStockStore = defineStore('stockStore', {
    state: () => ({
        stock: null,
    }),
    actions: {
      async getStock(baseStore){
        console.log('Cargando datos Remotos');
        baseStore.setLoading(true);
        const response = await fetch(appConfig.urlDispo);
        const data = await response.json();
        this.stock = data;
        baseStore.setLoading(false);
      },
      filterData(){
        console.log('Estamos en filterData');
        let data = this.stock;
        let filteredData = data.filter(item => item.stock > 0);
        return filteredData;
      }
    },

  })