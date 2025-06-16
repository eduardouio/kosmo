import { defineStore } from "pinia"
import { appConfig } from "@/AppConfig"
import axios from 'axios';
import { 
    BOX_SIZES, 
    canSplit, 
    canMerge, 
    getMergeTarget, 
    getSplitTarget, 
    splitStems 
} from '@/utils/boxUtils';

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
        /**
         * Split a box into two smaller boxes of the next size down
         * @param {Object} item - The box item to split
         */
        splitBox(item) {
            if (!canSplit(item.box_model)) {
                console.error('Cannot split this box size');
                return;
            }

            const newOrder = this.newOrder.filter(o => o !== item);
            const targetSize = getSplitTarget(item.box_model);
            
            // Create two new boxes of the target size
            const box1 = JSON.parse(JSON.stringify({
                ...item,
                box_model: targetSize,
                is_selected: false
            }));
            
            const box2 = JSON.parse(JSON.stringify({
                ...item,
                box_model: targetSize,
                is_selected: false
            }));

            // Calculate stem distribution for the two new boxes
            const stems = splitStems(item.tot_stem_flower);
            box1.tot_stem_flower = stems.first;
            box2.tot_stem_flower = stems.second;

            // Adjust the stem quantities in box_items
            box1.box_items.forEach(boxItem => {
                const boxStems = splitStems(boxItem.qty_stem_flower);
                boxItem.qty_stem_flower = boxStems.first;
            });
            
            box2.box_items.forEach(boxItem => {
                const boxStems = splitStems(boxItem.qty_stem_flower);
                boxItem.qty_stem_flower = boxStems.second;
            });

            // Add the new boxes to the order
            newOrder.push(box1, box2);
            this.newOrder = newOrder;
        },

        // Keep old method for backward compatibility
        splitHB(item) {
            this.splitBox(item);
        },
        /**
         * Merge selected boxes into larger boxes
         * Handles both cases: multiple boxes of same size or single box with quantity >= 2
         */
        mergeBoxes() {
            const selectedItems = this.newOrder.filter(i => i.is_selected);
            
            if (selectedItems.length === 0) {
                console.error('No items selected for merge');
                return;
            }

            // Check if all selected items are of the same box model
            const boxModel = selectedItems[0].box_model;
            if (!selectedItems.every(item => item.box_model === boxModel)) {
                console.error('All selected items must be of the same box model');
                return;
            }

            // Check if we can merge this box type - pass the correct parameters
            const totalQuantity = selectedItems.reduce((sum, item) => sum + (item.quantity || 1), 0);
            if (!canMerge(boxModel, selectedItems.length, totalQuantity)) {
                console.error(`Cannot merge ${boxModel} boxes - not enough items or quantity`);
                return;
            }

            const targetSize = getMergeTarget(boxModel);
            
            // Case 1: Single item with quantity >= 2
            if (selectedItems.length === 1) {
                const item = selectedItems[0];
                const itemQuantity = item.quantity || 1;
                
                if (itemQuantity < 2) {
                    console.error('Need at least 2 items to merge');
                    return;
                }

                const newQuantity = Math.floor(itemQuantity / 2);
                const remainingQuantity = itemQuantity % 2;
                
                // Create new larger box
                const newBox = JSON.parse(JSON.stringify({
                    ...item,
                    box_model: targetSize,
                    is_selected: false,
                    quantity: newQuantity
                }));
                
                // Adjust stem quantities - double them for the larger box
                newBox.tot_stem_flower = (item.tot_stem_flower || 0) * 2;
                newBox.box_items.forEach(boxItem => {
                    boxItem.qty_stem_flower = (boxItem.qty_stem_flower || 0) * 2;
                });
                
                // Update the order
                let newOrder = this.newOrder.filter(i => i !== item);
                newOrder.push(newBox);
                
                // Add remaining items if any
                if (remainingQuantity > 0) {
                    const remainingBox = JSON.parse(JSON.stringify(item));
                    remainingBox.quantity = remainingQuantity;
                    remainingBox.is_selected = false;
                    newOrder.push(remainingBox);
                }
                
                this.newOrder = newOrder;
            } 
            // Case 2: Multiple items of the same type (2 or more QBs)
            else if (selectedItems.length >= 2) {
                // For multiple items, we can merge pairs
                const itemsToMerge = selectedItems.slice(); // Copy array
                const newOrder = this.newOrder.filter(i => !i.is_selected);
                
                // Process pairs of items
                while (itemsToMerge.length >= 2) {
                    const item1 = itemsToMerge.shift();
                    const item2 = itemsToMerge.shift();
                    
                    // Create new larger box combining both items
                    const newBox = JSON.parse(JSON.stringify(item1));
                    newBox.box_model = targetSize;
                    newBox.is_selected = false;
                    newBox.quantity = 1; // One merged box from two smaller ones
                    
                    // Combine stems from both boxes
                    const totalStems1 = item1.tot_stem_flower || 0;
                    const totalStems2 = item2.tot_stem_flower || 0;
                    newBox.tot_stem_flower = totalStems1 + totalStems2;
                    
                    // Combine box items
                    const combinedItems = {};
                    
                    // Add items from first box
                    item1.box_items.forEach(boxItem => {
                        const key = `${boxItem.product_name}-${boxItem.product_variety}-${boxItem.length}`;
                        combinedItems[key] = { ...boxItem };
                    });
                    
                    // Add items from second box
                    item2.box_items.forEach(boxItem => {
                        const key = `${boxItem.product_name}-${boxItem.product_variety}-${boxItem.length}`;
                        if (combinedItems[key]) {
                            combinedItems[key].qty_stem_flower += (boxItem.qty_stem_flower || 0);
                        } else {
                            combinedItems[key] = { ...boxItem };
                        }
                    });
                    
                    newBox.box_items = Object.values(combinedItems);
                    newOrder.push(newBox);
                }
                
                // If there's one item left over, add it back
                if (itemsToMerge.length > 0) {
                    const leftoverItem = itemsToMerge[0];
                    leftoverItem.is_selected = false;
                    newOrder.push(leftoverItem);
                }
                
                this.newOrder = newOrder;
            }
        },
        
        // Keep old method for backward compatibility
        mergeQB() {
            this.mergeBoxes();
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