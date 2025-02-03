import { defineStore } from "pinia"
import { appConfig } from "@/AppConfig"
import axios from 'axios';

export const useOrdersStore = defineStore("ordersStore", {
    state: () => ({
        customers: [],
        orders: [],
        selectedCustomer: null,
        selectedOrder: null,
        limitsNewOrder: [],
        newOrder: [],
        stockDay: null,
        showViews: {
            listOrders: true,
            newOrder: false,
            singleOrder: false,
        },
    }),
    actions: {
        async loadCustomers(baseStore) {
            if (this.customers.length > 0) {
                baseStore.stagesLoaded++;
                return
            }
            try {
                const response = await axios.get(appConfig.urlAllCustomers)
                this.customers = response.data
                baseStore.stagesLoaded++;
              } catch (error) {
                console.error('Error al cargar los clientes:', error)
                alert(`Hubo un error al cargar los clientes: ${error.message}`)
            }
        },
        async sendOrder(stockDay) {
            const orderData = {
                customer: this.selectedCustomer,
                order_detail: this.newOrder,
                stock_day: stockDay
            }

            try {
                const response = await axios.post(appConfig.urlCreateOrder, orderData, {
                    headers: appConfig.headers
                })
                this.orders.push(response.data)
                this.newOrder = []
                this.selectedCustomer = null
            } catch (error) {
                console.error('Error al enviar el pedido:', error)
                alert(`Hubo un error al enviar el pedido: ${error.message}`)
            }
        },
        async loadOrders(baseStore) {
            if (this.orders.length > 0) {
                baseStore.stagesLoaded++;
                return
            }
            
            try {
                const response = await axios.get(appConfig.urlOrdersByStock)
                this.orders = response.data
                baseStore.stagesLoaded++;
            } catch (error) {
                console.error('Error al cargar los pedidos:', error)
                alert(`Hubo un error al cargar los pedidos: ${error.message}`)
            }
        },
        setLimits(orderDetail) {
            this.limitsNewOrder = orderDetail
        },
        splitHB(item) {
            const newOrder = this.newOrder.filter(o => o.stock_detail_id !== item.stock_detail_id);
            const stem_flower = item.box_items.map(i => i.qty_stem_flower);
            const id = item.stock_detail_id;

            if ((item.tot_stem_flower % 2) === 0) {
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
                if (itm.stock_detail_id === id) {
                    itm.box_items.forEach((i, index) => {
                        i.qty_stem_flower = stem_flower[index] / 2;
                    });
                }
            });
            this.newOrder = newOrder.map(i => ({ ...i }));
        },
        mergeQB() {
            const selectedQBs = this.newOrder.filter(i => i.is_selected);
            const newOrderItem = { ...selectedQBs[0], box_model: 'HB', is_selected: false };
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
        changeView(viewName){
            this.showViews = {
                listOrders: false,
                newOrder: false,
                singleOrder: false,
                [viewName]: true
            }
        },
        selectOrder(idOrder){
            this.selectedOrder = null;
            this.orders.forEach(order => {
                if (order.order.id === idOrder) {
                    order.is_selected = true;
                    this.selectedOrder = JSON.parse(JSON.stringify(order));
                    this.limitsNewOrder = order.order_details;
                }else{
                    order.is_selected = false;
                }
            });
        },
        async updateOrderItem(newDetaiils){
            console.log(newDetaiils)
            return;
            try {
                const response = await axios.post(appConfig.urlUpdateOrder, this.selectedOrder, {
                    headers: appConfig.headers
                })
                this.selectedOrder = response.data
                this.orders.forEach(order => {
                    if (order.order.id === this.selectedOrder.order.id) {
                        order = this.selectedOrder;
                    }
                });
                this.selectedOrder = null;
            } catch (error) {
                console.error('Error al actualizar el pedido:', error)
                alert(`Hubo un error al actualizar el pedido: ${error.message}`)
            }
        }
    }
})