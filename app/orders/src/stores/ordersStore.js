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
                const response = await axios.get(
                    appConfig.urlAllCustomers, {headers: appConfig.headers}
                )
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
                console.log('Pedido enviado:', response.data)
                if (Array.isArray(this.orders)) {
                    if (this.orders.length > 0) {
                        this.orders.unshift(response.data)
                    }else{
                        this.orders.push(response.data)
                    }   
                }
                this.newOrder = []
                this.selectedCustomer = null
                return response.data.order.id
            } catch (error) {
                console.error('Error al enviar el pedido:', error)
                alert(`Hubo un error al enviar el pedido: ${error.message}`)
            }
        },
        async loadOrders(baseStore) {
            console.log('Cargando pedidos de clientes...');
            if (this.orders.length > 0) {
                baseStore.stagesLoaded++;
                return
            }
            
            try {
                console.log('Cargando pedidos de clientes...' +  appConfig.urlOrdersByStock + '?type=sale');
                const response = await axios.get(appConfig.urlOrdersByStock + '?type=purchase')
                this.orders = response.data
                baseStore.stagesLoaded++;
            } catch (error) {
                console.error('Error al cargar los pedidos:', error)
                alert(`Hubo un error al cargar los pedidos: ${error.message}`)
                return false;
            }
        },
        setLimits(orderDetail) {
            this.limitsNewOrder = orderDetail
        },
        splitHB(item) {
            const newOrder = this.newOrder.filter(o => o !== item); // Filtrar por referencia del objeto en lugar de stock_detail_id
            const stem_flower = item.box_items.map(i => i.qty_stem_flower);
            const id = item.stock_detail_id;

            // Crear dos nuevos objetos QB completamente independientes
            const qb1 = JSON.parse(JSON.stringify({
                ...item,
                box_model: 'QB',
                is_selected: false
            }));
            
            const qb2 = JSON.parse(JSON.stringify({
                ...item,
                box_model: 'QB',
                is_selected: false
            }));

            // Ajustar las cantidades según si es par o impar
            if ((item.tot_stem_flower % 2) === 0) {
                qb1.tot_stem_flower = item.tot_stem_flower / 2;
                qb2.tot_stem_flower = item.tot_stem_flower / 2;
            } else {
                qb1.tot_stem_flower = Math.floor(item.tot_stem_flower / 2);
                qb2.tot_stem_flower = Math.ceil(item.tot_stem_flower / 2);
            }

            // Ajustar las cantidades de tallos en los box_items
            qb1.box_items.forEach((i, index) => {
                i.qty_stem_flower = Math.floor(stem_flower[index] / 2);
            });
            
            qb2.box_items.forEach((i, index) => {
                i.qty_stem_flower = Math.ceil(stem_flower[index] / 2);
            });

            // Agregar los nuevos QBs al array de pedidos
            newOrder.push(qb1);
            newOrder.push(qb2);

            this.newOrder = newOrder;
        },
        mergeQB() {
            const selectedQBs = this.newOrder.filter(i => i.box_model === 'QB' && i.is_selected);
            
            // Caso 1: Solo un QB está seleccionado pero su cantidad es par (2 o más)
            if (selectedQBs.length === 1 && selectedQBs[0].quantity >= 2 && selectedQBs[0].quantity % 2 === 0) {
                const qb = selectedQBs[0];
                const newHBCount = qb.quantity / 2; // Convertimos pares de QB en HBs
                
                // Crear el nuevo HB con las mismas características pero cantidad ajustada
                const newHB = JSON.parse(JSON.stringify({
                    ...qb,
                    box_model: 'HB',
                    is_selected: false,
                    quantity: newHBCount
                }));
                
                // Duplicar la cantidad de tallos en cada ítem de la caja
                newHB.box_items.forEach(item => {
                    item.qty_stem_flower = item.qty_stem_flower * 2;
                });
                
                // Reemplazar el QB original con el nuevo HB
                const index = this.newOrder.findIndex(i => i === qb);
                if (index !== -1) {
                    this.newOrder.splice(index, 1, newHB);
                }
            } 
            // Caso 2: Dos QB están seleccionados
            else if (selectedQBs.length === 2) {
                const [qb1, qb2] = selectedQBs;
                
                // Determinamos cuántas cajas podemos unificar (el mínimo entre ambos)
                const minQuantity = Math.min(qb1.quantity, qb2.quantity);
                const newHBCount = minQuantity;
                
                // Crear el nuevo HB con características combinadas
                const newHB = {
                    ...qb1, // Tomamos propiedades base del primer QB
                    box_model: 'HB',
                    is_selected: false,
                    quantity: newHBCount
                };
                
                // Combinamos los box_items de ambos QBs
                const combinedBoxItems = [...qb1.box_items, ...qb2.box_items];
                
                // Agrupamos por producto, variedad y longitud
                const groupedBoxItems = Object.values(
                    combinedBoxItems.reduce((acc, item) => {
                        const key = `${item.product_name}-${item.product_variety}-${item.length}`;
                        if (!acc[key]) {
                            acc[key] = { ...item };
                        } else {
                            acc[key].qty_stem_flower += item.qty_stem_flower;
                        }
                        return acc;
                    }, {})
                );
                
                newHB.box_items = groupedBoxItems;
                
                // Actualizar las cantidades de los QBs existentes o eliminarlos
                this.newOrder = this.newOrder.filter(i => !i.is_selected);
                
                // Si qb1 tiene más cajas que el mínimo, mantenemos las restantes
                if (qb1.quantity > minQuantity) {
                    const remainingQB1 = JSON.parse(JSON.stringify(qb1));
                    remainingQB1.quantity = qb1.quantity - minQuantity;
                    remainingQB1.is_selected = false;
                    this.newOrder.push(remainingQB1);
                }
                
                // Si qb2 tiene más cajas que el mínimo, mantenemos las restantes
                if (qb2.quantity > minQuantity) {
                    const remainingQB2 = JSON.parse(JSON.stringify(qb2));
                    remainingQB2.quantity = qb2.quantity - minQuantity;
                    remainingQB2.is_selected = false;
                    this.newOrder.push(remainingQB2);
                }
                
                // Agregar el nuevo HB
                this.newOrder.push(newHB);
            }
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
            console.log('Seleccionando pedido:', idOrder)
            this.selectedOrder = null;
            this.orders.forEach(order => {
                if (order.order.id === parseInt(idOrder)) {
                    order.is_selected = true;
                    this.selectedOrder = JSON.parse(JSON.stringify(order));
                    this.limitsNewOrder = order.order_details;
                }else{
                    order.is_selected = false;
                }
            });
            console.log('Pedido seleccionado:', this.selectedOrder);
        },
        async updateOrder(){
            console.log('Actualizando pedido:', this.selectedOrder)
            try {
                const response = await axios.post(appConfig.urlUpdateOrder,this.selectedOrder, {
                    headers: appConfig.headers
                })
                console.log('Pedido actualizado:', response.data)
                return true
            } catch (error) {
                console.error('Error al actualizar el pedido:', error)
                alert(`Hubo un error al actualizar el pedido: ${error.message}`)
            }
        },
        async cancellOrder(){
            console.log('Cancelando pedido:', this.selectedOrder)
            try {
                debugger;
                const response = await axios.post(appConfig.urlCancelOrder, {'id_order' : this.selectedOrder.order.id}, {
                    headers: appConfig.headers
                })
                console.log('Pedido cancelado:', response.data)
                return true
            } catch (error) {
                console.error('Error al cancelar el pedido:', error)
                alert(`Hubo un error al cancelar el pedido: ${error.message}`)
                return false
            }
        },
        async createInvoice(){
            console.log('Creando factura:', this.selectedOrder)
            try {
                const response = await axios.post(
                    appConfig.urlCreateInvoiceOrder, 
                    {'order_id' : this.selectedOrder.order.id},
                    {headers: appConfig.headers})
                console.log('Factura creada:', response.data)
                this.selectedOrder.order.status = 'FACTURADO'
                this.selectedOrder.is_invoiced = true
                this.selectedOrder.id_invoice = response.data.id_invoice
                this.selectedOrder.order.num_invoice = response.data.num_invoice
                return response.data
            } catch (error) {
                console.error('Error al crear la factura:', error)
                alert(`Hubo un error al crear la factura: ${error.message}`)
                return false
            }
        }, formatNumber(num) {
            if (num === null || num === undefined) return '0.00';
            const base_num = parseFloat(num);
            if (isNaN(base_num)) return '0.00';
            const parts = base_num.toString().split(".");
            const integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            const decimalPart = parts.length > 1 ? "." + parts[1].slice(0, 2) : ".00";
            return integerPart + decimalPart
        },
    }
})