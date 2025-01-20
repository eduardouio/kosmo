import { defineStore } from 'pinia';
import { appConfig } from '@/AppConfig';

export const useStockStore = defineStore('stockStore', {
    state: () => ({
        stock: [],
        stockText: 'Sin Seleccion',
        orders: [],
        stockDay: null,
        suppliers: [],
        colors:[],
        lengths:[],
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
        this.extractLengths();
      },
      async addBoxItem(boxItem){
        try {
          const response = await fetch(appConfig.urlAddBoxItem, {
            method: 'POST',
            headers: appConfig.headers,
            body: JSON.stringify(boxItem)
        });
        const data = await response.json();
        boxItem.id = data.box_item.id;
        this.stock.forEach(item => {
          if(item.stock_detail_id === boxItem.stock_detail_id){
            console.log('item', item);  
            item.box_items.push(boxItem);
          }
        });
        return data;
        } catch (error) {
          console.error('Error al agregar el item a la caja:', error);
          alert(`Hubo un error al agregar el item a la caja: ${error.message}`);
          return null;
        }
      },
      async updateStockDetail(boxes, boxDelete=false){
        try {
          const response = await fetch(appConfig.urlUpdateStockDetail, {
            method: 'POST',
            headers: appConfig.headers,
            body: JSON.stringify(boxes)
          });
      
          if (!response.ok) {
            throw new Error(`Error en la solicitud: ${response.status} ${response.statusText}`);
          }
          const data = await response.json();
          console.dir(data);
          if (boxDelete){
            this.deleteBoxItem(boxes[0]);
          }
        } catch (error) {
          console.error('Error al actualizar el stock:', error);
          alert(`Hubo un error al actualizar el stock: ${error.message}`);
          return null;
        }
      },
      deleteBoxItem(boxItem){
        console.log('deleteBoxItem', boxItem);
        this.stock.forEach(item => {
          item.box_items = item.box_items.filter(subItem => subItem.id !== boxItem.id);
        });
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
      extractLengths(){
        let lengths = this.stock.map(item => item.box_items).flat().map(item => item.length)
        .filter(
          (value, index, self) => self.findIndex(t => (t === value)) === index
        );
        this.lengths = lengths.map(item => ({name: item, is_selected: true}));
        this.lengths.sort((a,b) => a.name - b.name);
      },
      filterStock(querySearch) {
        if (!querySearch) {
          this.stock.forEach(item => {
            item.is_visible = true;
          });
          this.filterCategories();
          return;
        }
      
        this.stock.forEach(item => {
          item.is_visible = item.box_items.some(subItem =>
            subItem.product_variety.toLowerCase().includes(querySearch.toLowerCase())
          );
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
      filterCategories() {
        const selectedSuppliers = this.suppliers.filter(item => item.is_selected).map(item => item.id);
        const selectedColors = this.colors.filter(item => item.is_selected).map(item => item.name);
        const selectedLengths = this.lengths.filter(item => item.is_selected).map(item => item.name);
      
        if (selectedColors.length === 0 || selectedSuppliers.length === 0 || selectedLengths.length === 0) {
          this.stock.forEach(item => item.is_visible = false);
          return;
        }
        this.stock.forEach(item => {
          if (selectedSuppliers.includes(item.partner.id)) {
            item.is_visible = item.box_items.some(subItem => 
              subItem.product_colors.some(color => selectedColors.includes(color)) &&
              selectedLengths.includes(subItem.length)
            );
          } else {
            item.is_visible = false;
          }
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
        this.filterCategories();
      },
      selectAllColors(select=false){
        this.colors = this.colors.map(item => ({...item, is_selected: select}));
        this.filterCategories();
      },
      selectAllLengths(select=false){
        this.lengths = this.lengths.map(item => ({...item, is_selected: select}));
        this.filterCategories();
      },
      getSelection(){
        return this.stock.filter(
          item => item.is_selected).map(i=>({...i,confirm_delete:false})
        );
      },
      stockToText(){
        this.stockText = 'CANT TALLOS FINCA PRODUCTO LENGTH QTY PRICE COSTBOX\n';
        let selected = this.stock.filter(item => item.is_selected);
        selected.forEach(item => {
          const totalStem = item.box_items.reduce((acc, subItem) => acc + subItem.qty_stem_flower, 0);
          let line_text = `${item.quantity}${item.box_model} ${totalStem}`;
          item.box_items.forEach(subItem => {
            let cost = parseFloat(subItem.stem_cost_price) + parseFloat(subItem.margin);
            cost = cost.toFixed(2);
            line_text += ` ${subItem.product_variety} ${subItem.length}cmX${subItem.qty_stem_flower} $${cost}`;
          });
          this.stockText += line_text + ` ${ item.partner.short_name}\n`
        });
      },
      updateValues(newValue, column){
        let box_items = [];
        this.stock.forEach(stockItem => {
          if(stockItem.is_selected){
            stockItem.box_items.forEach(item => {
              item[column] = newValue;
              box_items.push(item);
            });
          };});
        this.updateStockDetail(box_items);
      },
    },
  });