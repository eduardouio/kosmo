import { defineStore } from 'pinia';
import { appConfig } from '@/AppConfig';


export const useStockStore = defineStore('stockStore', {
    state: () => ({
        stock: null,
        orders: [],
        stockDay: null,
        suppliers: [],
    }),
    actions: {
      async getStock(baseStore){
        baseStore.setLoading(true);
        const response = await fetch(appConfig.urlDispo);
        const data = await response.json();
        this.stock = data.stock;
        this.orders = data.orders;
        this.stockDay = data.stockDay;
        baseStore.setLoading(false);
        this.extractSuppliers();
      },
      extractSuppliers(){
        let suppliers = this.stock.map(item => item.partner).filter(
          (value, index, self) => self.findIndex(t => (t.id === value.id)) === index
        );
        this.suppliers = suppliers.map(item =>({...item, is_selected: false}));
      },
      filterData(query){
        let data = this.stock;
        let filteredData = data.filter(item => item.stock > 0);
        return filteredData;
      },
      filterBySupplier(){
        console.log('filterBySupplier');
        let selectedSuppliers = this.suppliers.filter(
          item => item.is_selected)
          .map(item => item.id);

        this.stock.forEach(item => {
          item.is_visible = selectedSuppliers.includes(item.partner.id);
      });
      },
      selectAllSuppliers(select=false){
        this.suppliers = this.suppliers.map(item => ({...item, is_selected: select}));
      },
    },
  })