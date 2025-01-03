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
      filterStock(querySearch){
        if (!querySearch){
          if( this.stock){
            this.stock.forEach(item => item.is_visible = true);
          }
          return;
        }
        console.log('filterStock');
        this.stock.forEach(item => {
          item.box_items.forEach(subItem => {
            item.is_visible = subItem.product_variety.toLowerCase().includes(querySearch.toLowerCase());
          });
        });
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