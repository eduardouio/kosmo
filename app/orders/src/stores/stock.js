import { defineStore } from 'pinia';
import { appConfig } from '@/AppConfig';
import stock from '@/data/stock.json';

export const useStockStore = defineStore('stockStore', {
    state: () => ({
        stock: null,
        is_loading: true,
    }),
    actions: {
      async loadData(){
        console.log('Cargando datos Remotos');
        const response = await fetch(appConfig.urlDispo);
        const data = await response.json();
        this.stock = data;
        this.is_loading = false;
      },
      setData(){
        this.stock = stock.stock;
      },
      filterData(){
        console.log('Estamos en filterData');
        let data = this.stock;
        let filteredData = data.filter(item => item.stock > 0);
        return filteredData;
      }
    },

  })