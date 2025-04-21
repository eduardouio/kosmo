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
    orderLines: [],
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
    addOrderLine() {
      console.log("Agregando línea de pedido...");
      this.orderLines.push(this.new_orderLine);
    },
    removeOrderLine(index) {
      this.orderLines.splice(index, 1);
    },

},
});