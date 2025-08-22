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
        async loadCustomers(baseStore, cycleId = baseStore.currentCycleId) {
            if (this.customers.length > 0) {
                baseStore.incrementStage(cycleId,'customers');
                return
            }
            try {
                const response = await axios.get(
                    appConfig.urlAllCustomers, {headers: appConfig.headers}
                )
                this.customers = response.data
                baseStore.incrementStage(cycleId,'customers');
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
    async loadOrders(baseStore, cycleId = baseStore.currentCycleId) {
            console.log('Cargando pedidos de clientes...');
            if (this.orders.length > 0) {
        baseStore.incrementStage(cycleId,'orders');
                return
            }
            
            try {
                console.log('Cargando pedidos de clientes...' +  appConfig.urlOrdersByStock + '?type=sale');
                const response = await axios.get(appConfig.urlOrdersByStock + '?type=sale')
                this.orders = response.data
        baseStore.incrementStage(cycleId,'orders');
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

            // Calculate total quantity from all selected items
            const totalQuantity = selectedItems.reduce((sum, item) => sum + (item.quantity || 1), 0);
            
            // Check if we can merge this box type - pass the correct parameters
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
            // Case 2: Multiple items (2 QB + 2 QB = 2 HB)
            else {
                // Calculate how many merged boxes we can create
                const mergedQuantity = Math.floor(totalQuantity / 2);
                const remainingQuantity = totalQuantity % 2;
                
                if (mergedQuantity === 0) {
                    console.error('Not enough total quantity to merge');
                    return;
                }
                
                // Create new larger box based on the first item
                const newBox = JSON.parse(JSON.stringify(selectedItems[0]));
                newBox.box_model = targetSize;
                newBox.is_selected = false;
                newBox.quantity = mergedQuantity;
                
                // Combine box items from all selected items
                const combinedItems = {};
                let totalStemsFromAllItems = 0;
                
                selectedItems.forEach(item => {
                    item.box_items.forEach(boxItem => {
                        const key = `${boxItem.product_name}-${boxItem.product_variety}-${boxItem.length}`;
                        const stemsForThisItem = (boxItem.qty_stem_flower || 0) * (item.quantity || 1);
                        
                        if (!combinedItems[key]) {
                            combinedItems[key] = JSON.parse(JSON.stringify(boxItem));
                            combinedItems[key].qty_stem_flower = stemsForThisItem;
                        } else {
                            combinedItems[key].qty_stem_flower += stemsForThisItem;
                        }
                        
                        totalStemsFromAllItems += stemsForThisItem;
                    });
                });
                
                // Distribute stems for the merged boxes
                Object.values(combinedItems).forEach(boxItem => {
                    // Distribute the stems proportionally to merged quantity
                    boxItem.qty_stem_flower = Math.floor(boxItem.qty_stem_flower * 2 / mergedQuantity);
                });
                
                newBox.box_items = Object.values(combinedItems);
                newBox.tot_stem_flower = totalStemsFromAllItems * 2 / mergedQuantity;
                
                // Update the order - remove all selected items
                let newOrder = this.newOrder.filter(i => !i.is_selected);
                newOrder.push(newBox);
                
                // Add remaining quantity if any
                if (remainingQuantity > 0) {
                    const remainingBox = JSON.parse(JSON.stringify(selectedItems[0]));
                    remainingBox.quantity = remainingQuantity;
                    remainingBox.is_selected = false;
                    newOrder.push(remainingBox);
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