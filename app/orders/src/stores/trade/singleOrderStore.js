import { defineStore } from "pinia"
import { appConfig } from "@/AppConfig"
import axios from 'axios'

export const useSingleOrderStore = defineStore("singleOrderStore", {
  state: () => ({
    order: {
      serie: '100',
      consecutive: '000000',
      stock_day: 0,
      date: '',
      partner: null,
      type_document: 'ORD_VENTA',
      parent_order: null,
      num_order: '',
      delivery_date: '',
      status: 'PROMESA',
      discount: 0,
      total_price: 0,
      total_margin: 0,
      comision_seler: 0,
      qb_total: 0,
      hb_total: 0,
      fb_total: 0,
      total_stem_flower: 0,
      total_bunches: 0, // Añadir el campo total_bunches
      is_invoiced: false,
      id_invoice: 0,
      num_invoice: null
    },
    orderLines: [],
    isLoading: false,
    hasError: false,
    errorMessage: ''
  }),
  
  actions: {
    addOrderLine() {
      this.orderLines.push({
        quantity: 1,
        box_model: 'QB',
        order_box_items: [{}]
      })
    },
    
    removeOrderLine(index) {
      this.orderLines.splice(index, 1)
    },

    calculateOrderLineTotal(line) {
      let total = 0
      if (Array.isArray(line.order_box_items)) {
        line.order_box_items.forEach(item => {
          const price = parseFloat(item.stem_cost_price) || 0
          const qty = parseFloat(item.qty_stem_flower) || 0
          const margin = parseFloat(item.profit_margin) || 0
          total += (price + margin) * qty
        })
      }
      return total
    },
    
    updateOrderLineTotal(index) {
      if (index >= 0 && index < this.orderLines.length) {
        this.orderLines[index].line_total = this.calculateOrderLineTotal(this.orderLines[index])
      }
    },
    
    async saveOrder(customer, supplier) {
      try {
        if (!customer || !supplier) {
          return {
            success: false,
            message: 'Debe seleccionar un cliente y un proveedor'
          }
        }
        
        const orderData = {
          order: this.order,
          customer: customer,
          supplier: supplier,
          orderLines: this.orderLines
        }
        
        const response = await axios.post(
          appConfig.urlCreateFutureOrder, 
          orderData, 
          { headers: appConfig.headers }
        )
        
        return {
          success: true,
          message: 'Orden creada correctamente',
          data: response.data
        }
      } catch (error) {
        console.error('Error al crear la orden:', error)
        return {
          success: false,
          message: `Error al crear la orden: ${error.message}`
        }
      }
    },
    
    formatDateForAPI(dateStr) {
      // Convertir fecha de DD/MM/YYYY a YYYY-MM-DD
      if (!dateStr || dateStr.trim() === '') {
        return ''
      }
      
      try {
        if (dateStr.includes('/')) {
          const parts = dateStr.split(' ')[0].split('/')
          if (parts.length === 3) {
            const [day, month, year] = parts
            return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
          }
        }
        return dateStr
      } catch {
        return ''
      }
    },
    
    async updateOrder(orderId, customer, supplier) {
      try {
        if (!customer || !supplier) {
          return {
            success: false,
            message: 'Debe seleccionar un cliente y un proveedor'
          }
        }
        
        // Formatear las fechas antes de enviar
        const formattedOrder = {
          ...this.order,
          delivery_date: this.formatDateForAPI(this.order.delivery_date)
        }
        
        const orderData = {
          order_id: orderId,
          order: formattedOrder,
          customer: customer,
          supplier: supplier,
          orderLines: this.orderLines
        }
        
        const response = await axios.post(
          appConfig.urlUpdateCustomerOrder, 
          orderData, 
          { headers: appConfig.headers }
        )
        
        return {
          success: true,
          message: 'Orden actualizada correctamente',
          data: response.data
        }
      } catch (error) {
        console.error('Error al actualizar la orden:', error)
        return {
          success: false,
          message: `Error al actualizar la orden: ${error.message}`
        }
      }
    },
    
    async loadOrder(orderId, baseStore) {
      if (!orderId) {
        this.errorMessage = 'ID de orden no proporcionado'
        this.hasError = true
        this.isLoading = false
        return { success: false }
      }
      
      try {
        this.isLoading = true
        const url = appConfig.urlOrderCustomerDetail.replace('{id_customer_order}', orderId)
        const response = await axios.get(
          url, 
          { headers: appConfig.headers }
        )
        
        // Configurar datos de la orden en el store
        const data = response.data
        
        // Configurar el cliente y proveedor
        if (data.customer) {
          baseStore.selectedCustomer = data.customer
        }
        
        if (data.supplier) {
          baseStore.selectedSupplier = data.supplier
        }
        
        // Configurar la información de la orden
        this.order = {
          serie: data.order.serie || '',
          consecutive: data.order.consecutive || '',
          stock_day: data.order.stock_day || 0,
          date: data.order.date ? data.order.date : baseStore.formatDate(new Date()),
          partner: data.order.partner || null,
          type_document: data.order.type_document || 'ORD_VENTA',
          parent_order: data.order.parent_order || null,
          num_order: data.order.num_order || '',
          delivery_date: data.order.delivery_date || '',
          status: data.order.status || 'PENDIENTE',
          discount: data.order.discount || 0,
          total_price: data.order.total_price || 0,
          total_margin: data.order.total_margin || 0,
          comision_seler: data.order.comision_seler || 0,
          qb_total: data.order.qb_total || 0,
          hb_total: data.order.hb_total || 0, 
          fb_total: data.order.fb_total || 0,
          total_stem_flower: data.order.total_stem_flower || 0,
          total_bunches: data.order.total_bunches || 0,
          is_invoiced: data.order.is_invoiced || false,
          id_invoice: data.order.id_invoice || 0,
          num_invoice: data.order.num_invoice || null
        }
        
        // Configurar las líneas de la orden
        this.orderLines = []
        if (data.orderLines && Array.isArray(data.orderLines)) {
          data.orderLines.forEach(line => {
            const newLine = {
              quantity: line.quantity || 1,
              box_model: line.box_model || 'QB',
              order_box_items: [],
              line_price: line.line_price || 0,
              line_margin: line.line_margin || 0,
              line_total: line.line_total || 0,
              line_commission: line.line_commission || 0,
              tot_stem_flower: line.tot_stem_flower || 0
            }
            
            if (line.order_box_items && Array.isArray(line.order_box_items)) {
              line.order_box_items.forEach(item => {
                newLine.order_box_items.push({
                  product: item.product || null,
                  length: item.length || 0,
                  stems_bunch: item.stems_bunch || 0,
                  total_bunches: item.total_bunches || 0,
                  qty_stem_flower: item.qty_stem_flower || 0,
                  stem_cost_price: item.stem_cost_price || '0.00',
                  profit_margin: item.profit_margin || '0.00',
                  total_stem_flower: item.total_stem_flower || 0,
                  total: item.total || '0.00'
                })
              })
            }
            
            this.orderLines.push(newLine)
          })
        }
        
        this.hasError = false
        this.errorMessage = ''
        return { success: true, data }
        
      } catch (error) {
        console.error('Error al cargar la orden:', error)
        this.errorMessage = `Error al cargar la orden: ${error.message}`
        this.hasError = true
        return { success: false, error }
      } finally {
        this.isLoading = false
      }
    },
    updateOrderTotals(newValues) {
      this.order = {
        ...this.order,
        ...newValues
      }
    },
  }
})