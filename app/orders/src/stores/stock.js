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
        this.suppliers = suppliers.map(item =>({...item, is_selected: true}));
      },
      filterStock(querySearch){
        if (!querySearch){
          if( this.stock){
            this.stock.forEach(item => item.is_visible = true);
          }
          return;
        }
        this.stock.forEach(item => {
          item.box_items.forEach(subItem => {
            item.is_visible = subItem.product_variety.toLowerCase().includes(querySearch.toLowerCase());
          });
        });
      },
      selectAll(option){
        this.stock.forEach(item => {
          if( item.is_visible === true){
            item.is_selected = option;
          }
        });
      },
      filterBySupplier(){
        let selectedSuppliers = this.suppliers.filter(
          item => item.is_selected)
          .map(item => item.id);

        this.stock.forEach(item => {
          item.is_visible = selectedSuppliers.includes(item.partner.id);
      });
      },
      async deleteSelected(){
        let toDelete = this.stock.filter(item => item.is_selected);
        this.stock = this.stock.filter(item => !item.is_selected);
        const response = await fetch(appConfig.urlDeleteStockDetail, {
          method: 'POST',
          headers: appConfig.headers,
          body: JSON.stringify(toDelete)
        });
        const data = await response.json();
        console.dir(data);
      },
      selectAllSuppliers(select=false){
        this.suppliers = this.suppliers.map(item => ({...item, is_selected: select}));
      },
    },
  })