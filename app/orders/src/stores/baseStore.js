import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";
import axios from 'axios';

export const useBaseStore = defineStore("baseStore", {
    state: () => ({
        colors: {
          'AMARILLO' : 'text-yellow-500',
          'AZUL' : 'text-blue-500',
          'BLANCO' : 'text-gray-500',
          'CAFE' : '.bg-brown-400',
          'CREMA' : 'text-amber-500',
          'MORADO' : 'text-violet-500',
          'NARANJA' : 'text-orange-500',
          'ROJO' : 'text-red-500',
          'ROSADO' : 'text-pink-500',
          'TINTURADO' : 'text-lime-500',
          'VERDE' : 'text-green-500',
          'BICOLOR': 'text-indigo-500',
          'OTRO' : 'text-gray-500',
        },
        bgColor: {
          'AMARILLO' : 'bg-yellow-500 text-white',
          'AZUL' : 'bg-blue-500 text-white',
          'BLANCO' : 'bg-light border-gray-400',
          'CAFE' : 'bg-brown-400 text-white',
          'CREMA' : 'bg-amber-500 text-white',
          'MORADO' : 'bg-violet-500 text-white',
          'NARANJA' : 'bg-orange-500 text-white',
          'ROJO' : 'bg-red-500 text-white',
          'ROSADO' : 'bg-pink-400 text-white',
          'TINTURADO' : 'bg-lime-500 text-white',
          'BICOLOR': 'bg-indigo-500 text-white',
          'VERDE' : 'bg-green-500 text-white',
          'OTRO' : 'bg-gray-500 text-white',
        },
        // Nueva sección de alertas
        alertMessage: '',
        alertType: 'info', // 'info', 'warning', 'error'
        defaultInfoMessage: 'Revise los detalles del pedido y proceda a guardar para generar las órdenes de compra a los proveedores.',
        
        suppliers:[],
        products:[],
        customers:[],
        isLoading: false,
        stagesLoaded: 0,
        idStock: appConfig.idStock,
        selectedProduct: null,
        selectedCustomer: null,
        selectedSupplier: null,
    }),
    actions: {
      // Nueva funcionalidad de alertas
      setAlert(message, type = 'info') {
        this.alertMessage = message;
        this.alertType = type;
      },
      
      updateGlobalAlertStatus(ordersStore) {
        // Priority 1: Pending delete confirmation
        const itemPendingDelete = ordersStore.newOrder.find(item => item.confirm_delete);
        if (itemPendingDelete) {
          this.setAlert('El item marcado será eliminado del pedido, click nuevamente para confirmar.', 'warning');
          return;
        }

        // Priority 2: Zero data errors in items
        for (const order of ordersStore.newOrder) {
          if (order.box_items.some(p => parseInt(p.total_bunches) === 0 || parseInt(p.stems_bunch) === 0 || parseFloat(p.stem_cost_price) <= 0)) {
            this.setAlert('No se permiten items con bunches 0, tallos por bunch 0, o costo <= 0.', 'error');
            return;
          }
        }

        // Priority 3: Customer not selected (only if there are items in the order)
        if (ordersStore.newOrder.length > 0 && !ordersStore.selectedCustomer) {
          this.setAlert('Debe seleccionar un cliente.', 'error');
          return;
        }
        
        // Priority 4: If current alert is an error not covered above (e.g. quantity error), keep it.
        const isKnownGlobalError = 
          (this.alertMessage.startsWith('No se permiten items con bunches 0')) ||
          (this.alertMessage.startsWith('Debe seleccionar un cliente'));

        if (this.alertType === 'error' && !isKnownGlobalError) {
          // This is likely a quantity error set by delimitedNumber, keep it until resolved there.
          return;
        }

        // If no active warnings or errors, show default info message.
        this.setAlert(this.defaultInfoMessage, 'info');
      },
      
      async loadSuppliers(all=false){
        if (this.suppliers.length > 0) {
          this.stagesLoaded++;
          return;
        }
        try {
          let url = appConfig.urlAllSuppliers.replace("{isStockDay}", this.idStock);
          
          if (all){
            url = appConfig.urlAllSuppliers.replace("{isStockDay}", 0);
          }

          const response = await axios.get(url, { headers: appConfig.headers });
          this.suppliers = response.data;
          this.suppliers.sort((a, b) => a.name.localeCompare(b.name));
          this.stagesLoaded++;
        }
        catch (error) {
          console.error('Error al cargar los proveedores:', error);
          alert(`Hubo un error al cargar los proveedores: ${error.message}`);
        }
      },
      async loadProducts(){
        if (this.products.length > 0) { 
          this.stagesLoaded++;
          return;
        }
        try{
          const response = await axios.get(
            appConfig.urlAllProducts, { headers: appConfig.headers }
          );
          this.products = response.data.products;
          this.stagesLoaded++;
        }
        catch (error) {
          console.error('Error al cargar los productos:', error);
          alert(`Hubo un error al cargar los productos: ${error.message}`);
        }
      },
      async loadCustomers(){
        console.log("Cargando clientes...");
        if (this.customers.length > 0) {
          this.stagesLoaded++;
          return;
        }
        try{
          const response = await axios.get(
              appConfig.urlAllCustomers, { headers: appConfig.headers }
          );
          this.customers = response.data;
          this.customers.sort((a, b) => a.name.localeCompare(b.name));
          this.stagesLoaded++;
        }
        catch (error) {
          console.error('Error al cargar los clientes:', error);
          alert(`Hubo un error al cargar los clientes: ${error.message}`);
        }
      },
      formatDate(date){
        if (!date) return '--:--';
        const options = {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          hour12: false
        };
        return new Date(date).toLocaleDateString('es-ES', options).replace(',', '');
      },
      formatCurrency(value) {
        if (!value) return '0.00';
        return new Intl.NumberFormat('es-EC', {
          style: 'currency',
          currency: 'COP',
          minimumFractionDigits: 2
        }).format(value).replace('COP', '').replace(',','.').trim()
      },
      formatNumber(event){
        let value = event.target.value;
        value = value.replace(',', '.');
        if (value === '' || value === '.' || value === ',' || isNaN(value) || value === ' ' || value === '0') {
          event.target.value = '0.00';
          return;
        }
        event.target.value = parseFloat(value).toFixed(2);
      },
      formatInteger(event, box = null){
          let value = event.target.value;
          value = value.replace(',', '.');
          if (value === '' || value === '.' || value === ',' || isNaN(value) || value === ' ' || value === '0') {
              event.target.value = '0';
              return;
          }
          event.target.value = parseInt(value);
      },
      formatInputNumber(number){
        console.log('Formatting input number')
        if (number === null || number === undefined || number === '' || number === '0') {
          return parseFloat(0).toFixed(2)
        }
        number =  String(number).replace(',','.')
        return parseFloat(number).toFixed(2);
      },
    },
});