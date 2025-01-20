import { defineStore } from "pinia"
import { appConfig } from "@/AppConfig"


export const useOrdersStore = defineStore("ordersStore", {
    state: () => ({
        customers:[],
        orders: [],
        selectedCustomer: null,
        limitsNewOrder: [],
        newOrder:[],
    }),
    actions:{
        async loadCustomers(){
            if (this.customers.length > 0) return
            try{
              const response = await fetch(appConfig.urlAllCustomers)
              const data = await response.json()
              this.customers = data
            }
            catch (error) {
              console.error('Error al cargar los clientes:', error)
              alert(`Hubo un error al cargar los clientes: ${error.message}`)
            }   
          },
          setLimits(orderDetail){
            this.limitsNewOrder = orderDetail
          },
          splitHB(item){
            const newOrder = this.newOrder.filter(o => o.stock_detail_id !== item.stock_detail_id);
            const stem_flower = item.box_items.map(i => i.qty_stem_flower);
            const id = item.stock_detail_id;

            if ((item.tot_stem_flower % 2) === 0){
              newOrder.push({
                ...item,
                tot_stem_flower: item.tot_stem_flower / 2,
                box_model: 'QB',
              });
              newOrder.push({
                ...item,
                tot_stem_flower: item.tot_stem_flower / 2,
                box_model: 'QB',
              });
            }
            newOrder.forEach((itm) => {
              if (itm.stock_detail_id === id){
                itm.box_items.forEach((i, index) => {
                  i.qty_stem_flower = stem_flower[index]/2;
                });
              }
            });
            this.newOrder = newOrder.map(i=>({...i}));
          },
          mergeQB(){
            const newOrder = this.newOrder;
            const qbItems = newOrder.filter(i => i.box_model === 'QB');
            const id = qbItems[0].stock_detail_id;
            const qbItemsQty = qbItems.map(i => i.tot_stem_flower).reduce((a,b) => a+b, 0);
            const newOrderFiltered = newOrder.filter(i => i.stock_detail_id !== id);
            newOrderFiltered.push({
              ...qbItems[0],
              tot_stem_flower: qbItemsQty,
              box_model: 'HB',
            });
            this.newOrder = newOrderFiltered.map(i=>({...i}));
          },
    }
})