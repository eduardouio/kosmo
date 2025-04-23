import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";
import axios from "axios";

export const useSingleOrderStore = defineStore("singleOrderStore", {
  state: () => ({
    order:{
      serie: "200",
      serie_name: "ORD-VENTA",
      consecutive: "000000",
      stock_day: 0,
      date: null,
      partner: 1,
      type_document: "ORD_COMPRA",
      parent_order: null,
      num_order: "PO-001",
      delivery_date: "2024-04-18",
      status: "PENDIENTE",
      discount: 0,
      total_price: 0,
      total_margin: 0,
      comision_seler: 0,
      qb_total: 0,
      hb_total: 0,
      fb_total: 0,
      total_stem_flower: 0,
      is_invoiced: false,
      id_invoice: null,
      num_invoice: null
    },
    // Inicializa con una línea en blanco
    orderLines: [ 
      // Se clona para evitar referencia reactiva
      JSON.parse(JSON.stringify({
        id_stock_detail: 0,
        line_price: 0,
        line_margin: 0,
        line_total: 0,
        line_commission: 0,
        tot_stem_flower: 0,
        box_model: "QB",
        quantity: 1,
        order_box_items: [
          {
            product: null,
            length: '',
            stems_bunch: 0,
            total_bunches: 0,
            qty_stem_flower: 0,
            stem_cost_price: 0,
            profit_margin: 0,
            total_stem_flower: 0,
          }
        ]
      }))
    ],
    new_orderLine:  {
      id_stock_detail: 0,
      line_price: 0,
      line_margin: 0,
      line_total: 0,
      line_commission: 0,
      tot_stem_flower: 0,
      box_model: "QB",
      quantity: 1,
      order_box_items: [
        {
          product: null,
          length: '',
          stems_bunch: 0,
          total_bunches: 0,
          qty_stem_flower: 0,
          stem_cost_price: 0,
          profit_margin: 0,
          total_stem_flower: 0,
        }
      ]
    }
  }),
  actions: {
    async loadOrder(id, baseStore) {
      console.log("Cargando orden de compra...");
      this.order = {};
      this.orderLines = [];
      try {
        const response = await axios.get(
          appConfig.urlOrdersByStock.replace("{id}", id),
          { headers: appConfig.headers }
        );
        this.order = response.data;
        this.orderLines = response.data.lines;
        console.log("Orden de compra cargada", response.data);
        baseStore.stagesLoaded++;
      } catch (error) {
        console.error("Error al cargar la orden de compra:", error);
        alert(`Hubo un error al cargar la orden de compra: ${error.message}`);
      }
    },
    calculateOrderLineTotal(orderLine) {
      // Suma el total de cada box_item: (stem_cost_price + profit_margin) * qty_stem_flower
      // Luego multiplica por la cantidad de cajas (quantity)
      let boxItemsTotal = 0;
      if (orderLine.order_box_items && Array.isArray(orderLine.order_box_items)) {
        boxItemsTotal = orderLine.order_box_items.reduce((sum, item) => {
          const price = parseFloat(item.stem_cost_price) || 0;
          const margin = parseFloat(item.profit_margin) || 0;
          const qtyStems = parseFloat(item.qty_stem_flower) || 0;
          return sum + (price + margin) * qtyStems;
        }, 0);
      }
      const quantity = parseFloat(orderLine.quantity) || 0;
      orderLine.line_total = boxItemsTotal * quantity;
      return orderLine.line_total;
    },
    addOrderLine() {
      console.log("Agregando línea de pedido...");
      // Clonar la línea para evitar referencias reactivas
      const line = JSON.parse(JSON.stringify(this.new_orderLine));
      this.calculateOrderLineTotal(line);
      this.orderLines.push(line);
    },
    updateOrderLineTotal(index) {
      if (this.orderLines[index]) {
        this.calculateOrderLineTotal(this.orderLines[index]);
      }
    },
    removeOrderLine(index) {
      this.orderLines.splice(index, 1);
      // Si no queda ninguna línea, agrega una nueva en blanco
      if (this.orderLines.length === 0) {
        const line = JSON.parse(JSON.stringify(this.new_orderLine));
        this.orderLines.push(line);
      }
    },
    async saveOrder(customer, supplier) {
      // Agrupa los datos necesarios
      const payload = {
        order: this.order,
        orderLines: this.orderLines,
        customer: customer,
        supplier: supplier
      }
      try {
        const response = await axios.post('http://localhost/orders/create', payload)
        return { success: true, message: 'Pedido guardado correctamente' }
      } catch (error) {
        return { 
          success: false, 
          message: 'Error al guardar el pedido: ' + (error.response?.data?.message || error.message) 
        }
      }
    },
  },
});