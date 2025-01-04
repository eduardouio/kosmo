import { defineStore } from 'pinia';
import { appConfig } from '@/AppConfig';
import { watch } from 'vue';


export const useStockStore = defineStore('stockStore', {
    state: () => ({
        stock: null,
        stockText: 'Sin Seleccion',
        orders: [],
        stockDay: null,
        suppliers: [],
        colors:[],
    }),
    actions: {
      async getStock(baseStore){
        baseStore.setLoading(true);
        const response = await fetch(appConfig.urlDispo);
        const data = await response.json();
        if (data.error){
          alert(data.error);
          return;
        }
        this.stock = data.stock;
        this.orders = data.orders;
        this.stockDay = data.stockDay;
        baseStore.setLoading(false);
        this.extractSuppliers();
        this.extractColors();
      },
      async updateStockDetail(item){
        const response = await fetch(appConfig.urlUpdateStockDetail, {
          method: 'POST',
          headers: appConfig.headers,
          body: JSON.stringify(item)
        });
        const data = await response.json();
        console.dir(data);
      },
      extractColors(){
        let colors = this.stock.map(item => item.box_items).flat().map(item => item.product_colors)
        .flat().filter(
          (value, index, self) => self.findIndex(t => (t === value)) === index
        );
        this.colors = colors.map(item => ({name: item, is_selected: true}));
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
            this.filterBySupplier();
            this.filterByColor();
          }
          return;
        }
        this.stock.forEach(item => {
          if(item.is_visible){
          item.box_items.forEach(subItem => {
            item.is_visible = subItem.product_variety.toLowerCase().includes(querySearch.toLowerCase());
          });
        }
        });
      },
      selectAll(option){
        this.stock.forEach(item => {
          if( item.is_visible === true){
            item.is_selected = option;
          }
        });
        this.stockToText();
      },
      filterBySupplier(){
        let selectedSuppliers = this.suppliers.filter(
          item => item.is_selected)
          .map(item => item.id);
        this.stock.forEach(item => {
          item.is_visible = selectedSuppliers.includes(item.partner.id);
      });
      },
      filterByColor(){
        let selectedColors = this.colors.filter(
          item => item.is_selected)
          .map(item => item.name);
          this.stock.forEach(item => {
            item.is_visible = item.box_items.some(subItem => {
              return subItem.product_colors.some(color => selectedColors.includes(color));
            });
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
        this.filterBySupplier();
      },
      selectAllColors(select=false){
        this.colors = this.colors.map(item => ({...item, is_selected: select}));
        this.filterByColor();
      },
      stockToText(){
        this.stockText = 'QTY\tBOX\tTOTAL\tSUPPLIER\tPRODUCT\tLENGTH\tQTY\tPRICE\tCOSTBOX\n';
        let selected = this.stock.filter(item => item.is_selected);
        selected.forEach(item => {
          const totalStem = item.box_items.reduce((acc, subItem) => acc + subItem.qty_stem_flower, 0);
          let line_text = `${item.quantity}\t${item.box_model}\t${totalStem}\t${ item.partner.name}`;
          item.box_items.forEach(subItem => {
            let cost = parseFloat(subItem.stem_cost_price) + parseFloat(subItem.margin);
            cost = cost.toFixed(2);
            line_text += `\t[${subItem.product_variety}\t${subItem.length}CM\t${subItem.qty_stem_flower}\t${cost}]`;
          });
          const totalValue = item.box_items.reduce((acc, subItem) => acc + ((subItem.stem_cost_price + subItem.margin) * subItem.qty_stem_flower), 0);
          this.stockText += line_text + `\t $ ${totalValue.toFixed(2)} \n`;
        });
      },
      updateValues(newValue, column){
        this.stock.forEach(stockItem => {
          if(stockItem.is_selected){
            stockItem.box_items.forEach(item => {
              item[column] = newValue;
            });
          };});
      },
    },
  });