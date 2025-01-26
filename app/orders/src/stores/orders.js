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
          async sendOrder() {
            try {
                const response = await fetch(appConfig.urlCreateOrder, {
                    method: 'POST',
                    headers: appConfig.headers,
                    body: JSON.stringify({
                      customer: this.selectedCustomer, 
                      order : this.newOrder
                    })
                })
                if (!response.ok) {
                    throw new Error('Error al enviar el pedido')
                }
                const data = await response.json()
                alert('Pedido creado exitosamente')
                this.newOrder = []
                this.selectedCustomer = null
            } catch (error) {
                console.error('Error al enviar el pedido:', error)
                alert(`Hubo un error al enviar el pedido: ${error.message}`)
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
            const selectedQBs = this.newOrder.filter(i => i.is_selected);
            const newOrderItem = {...selectedQBs[0], box_model: 'HB', is_selected: false};
            this.newOrder = this.newOrder.filter(i => !i.is_selected);
            newOrderItem.tot_stem_flower = selectedQBs.reduce(
              (acc, i) => acc + i.tot_stem_flower, 0
            );
            newOrderItem.box_items = selectedQBs.reduce((acc, i) => {
              acc.push(...i.box_items);
              return acc;
            }, []);
            
            const groupedBoxItems = Object.values(
              newOrderItem.box_items.reduce((acc, item) => {
                  const key = `${item.product_name}-${item.product_variety}-${item.length}`;
                  if (!acc[key]) {
                      acc[key] = { ...item };
                  } else {
                      acc[key].qty_stem_flower += item.qty_stem_flower;
                  }
                  return acc;
              }, {})
            );

            newOrderItem.box_items = groupedBoxItems;

            this.newOrder.push(newOrderItem);
          },
    }
})