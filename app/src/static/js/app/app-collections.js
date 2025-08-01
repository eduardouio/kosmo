const { createApp } = Vue;

createApp({
  data() {
    return {
      loading: true,
      saving: false,
      customers: [],
      filteredCustomers: [],
      pendingInvoices: [],
      filteredInvoices: [],
      paymentMethods: [],
      popularBanks: [],
      statistics: {},
      
      // Autocomplete de clientes
      customerSearchTerm: '',
      selectedCustomer: null,
      showCustomerDropdown: false,
      
      // Formulario de cobro
      collectionForm: {
        date: '',
        method: '',
        reference: '',
        amount: 0,
        bank: '',
        accountNumber: '',
        observations: '',
        document: null,
        documentName: '',
        documentPreview: null
      },
      
      // Sistema de mensajes del modal
      modalMessage: {
        show: false,
        type: 'info', // success, warning, danger, info
        text: '',
        icon: 'fa-info-circle'
      },
      
      // Validaciones
      formErrors: {
        date: '',
        method: '',
        amount: '',
        document: ''
      },
      
      // Facturas seleccionadas para el cobro
      selectedInvoices: [],
      
      // Configuración de factura
      invoiceSearchTerm: '',
      showInvoiceDropdown: false,
      currentInvoiceAmount: 0,
      
      // Tabla de pagos/cobros
      collections: [],
      currentPage: 1,
      pageSize: 10,
      totalPages: 0,
      totalCount: 0,
    }
  },

  computed: {
    // Busqueda de clientes
    searchedCustomers() {
      if (!this.customerSearchTerm) return this.customers.slice(0, 10);
      return this.customers.filter(customer => 
        customer.name.toLowerCase().includes(this.customerSearchTerm.toLowerCase()) ||
        customer.company_name.toLowerCase().includes(this.customerSearchTerm.toLowerCase())
      ).slice(0, 10);
    },

    // Facturas filtradas
    searchedInvoices() {
      if (!this.invoiceSearchTerm) return this.pendingInvoices.slice(0, 15);
      return this.pendingInvoices.filter(invoice => 
        invoice.invoice_number.toLowerCase().includes(this.invoiceSearchTerm.toLowerCase()) ||
        invoice.partner_name.toLowerCase().includes(this.invoiceSearchTerm.toLowerCase())
      ).slice(0, 15);
    },

    // Total de facturas seleccionadas
    totalSelectedInvoices() {
      return this.selectedInvoices.reduce((sum, invoice) => sum + parseFloat(invoice.amount), 0);
    },

    // Validar si el formulario es válido
    isFormValid() {
      return this.collectionForm.date && 
             this.collectionForm.method && 
             this.selectedInvoices.length > 0 &&
             this.totalSelectedInvoices > 0;
    }
  },

  async mounted() {
    await this.loadContextData();
    this.setDefaultDate();
    this.loading = false;
  },

  methods: {
    async loadContextData() {
      try {
        const response = await fetch('/api/collections/context-data/', {
          method: 'GET',
          headers: {
            'X-CSRFToken': this.getCsrfToken(),
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          this.customers = data.customers || [];
          this.pendingInvoices = data.pending_invoices || [];
          this.paymentMethods = data.payment_methods || [];
          this.popularBanks = data.popular_banks || [];
          this.statistics = data.statistics || {};
        }
      } catch (error) {
        console.error('Error cargando datos de contexto:', error);
        this.showModal('Error al cargar datos', 'danger');
      }
    },

    setDefaultDate() {
      const today = new Date();
      this.collectionForm.date = today.toISOString().split('T')[0];
    },

    // Métodos de autocompletado para clientes
    onCustomerSearch() {
      this.showCustomerDropdown = this.customerSearchTerm.length > 0;
    },

    selectCustomer(customer) {
      this.selectedCustomer = customer;
      this.customerSearchTerm = `${customer.name} - ${customer.company_name}`;
      this.showCustomerDropdown = false;
      this.filterInvoicesByCustomer(customer.id);
    },

    filterInvoicesByCustomer(customerId) {
      this.filteredInvoices = this.pendingInvoices.filter(
        invoice => invoice.partner_id === customerId
      );
    },

    clearCustomerSelection() {
      this.selectedCustomer = null;
      this.customerSearchTerm = '';
      this.filteredInvoices = [];
      this.selectedInvoices = [];
    },

    // Métodos para manejar facturas
    onInvoiceSearch() {
      this.showInvoiceDropdown = this.invoiceSearchTerm.length > 0;
    },

    selectInvoice(invoice) {
      // Verificar si la factura ya está seleccionada
      const exists = this.selectedInvoices.find(inv => inv.invoice_id === invoice.id);
      if (exists) {
        this.showModal('Esta factura ya está seleccionada', 'warning');
        return;
      }

      this.selectedInvoices.push({
        invoice_id: invoice.id,
        invoice_number: invoice.invoice_number,
        partner_name: invoice.partner_name,
        total_amount: parseFloat(invoice.total_amount),
        amount: this.currentInvoiceAmount || parseFloat(invoice.pending_amount)
      });

      this.invoiceSearchTerm = '';
      this.currentInvoiceAmount = 0;
      this.showInvoiceDropdown = false;
      this.updateTotalAmount();
    },

    removeInvoice(index) {
      this.selectedInvoices.splice(index, 1);
      this.updateTotalAmount();
    },

    updateInvoiceAmount(index, newAmount) {
      const invoice = this.selectedInvoices[index];
      const amount = parseFloat(newAmount) || 0;
      
      if (amount > invoice.total_amount) {
        this.showModal(`El monto no puede ser mayor al total de la factura (${invoice.total_amount})`, 'warning');
        return;
      }
      
      invoice.amount = amount;
      this.updateTotalAmount();
    },

    updateTotalAmount() {
      this.collectionForm.amount = this.totalSelectedInvoices;
    },

    // Validaciones
    validateForm() {
      this.formErrors = {
        date: '',
        method: '',
        amount: '',
        document: ''
      };

      let isValid = true;

      if (!this.collectionForm.date) {
        this.formErrors.date = 'La fecha es requerida';
        isValid = false;
      }

      if (!this.collectionForm.method) {
        this.formErrors.method = 'El método de cobro es requerido';
        isValid = false;
      }

      if (this.selectedInvoices.length === 0) {
        this.formErrors.amount = 'Debe seleccionar al menos una factura';
        isValid = false;
      }

      if (this.totalSelectedInvoices <= 0) {
        this.formErrors.amount = 'El monto total debe ser mayor a cero';
        isValid = false;
      }

      return isValid;
    },

    // Crear cobro
    async createCollection() {
      if (!this.validateForm()) {
        this.showModal('Por favor corrige los errores en el formulario', 'danger');
        return;
      }

      this.saving = true;

      try {
        const collectionData = {
          date: this.collectionForm.date,
          amount: this.totalSelectedInvoices,
          method: this.collectionForm.method,
          bank: this.collectionForm.bank,
          nro_account: this.collectionForm.accountNumber,
          nro_operation: this.collectionForm.reference,
          invoices: this.selectedInvoices.map(inv => ({
            invoice_id: inv.invoice_id,
            amount: inv.amount
          }))
        };

        const response = await fetch('/api/collections/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': this.getCsrfToken(),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(collectionData)
        });

        const data = await response.json();

        if (response.ok && data.success) {
          this.showModal(data.message || 'Cobro creado exitosamente', 'success');
          this.resetCollectionForm();
          await this.loadContextData(); // Recargar datos
        } else {
          this.showModal(data.error || 'Error al crear el cobro', 'danger');
        }
      } catch (error) {
        console.error('Error creando cobro:', error);
        this.showModal('Error de conexión al crear el cobro', 'danger');
      } finally {
        this.saving = false;
      }
    },

    resetCollectionForm() {
      this.collectionForm = {
        date: '',
        method: '',
        reference: '',
        amount: 0,
        bank: '',
        accountNumber: '',
        observations: '',
        document: null,
        documentName: '',
        documentPreview: null
      };
      this.selectedInvoices = [];
      this.selectedCustomer = null;
      this.customerSearchTerm = '';
      this.invoiceSearchTerm = '';
      this.setDefaultDate();
    },

    // Cargar lista de cobros
    async loadCollections(page = 1) {
      try {
        const response = await fetch(`/api/collections/?page=${page}&page_size=${this.pageSize}`, {
          method: 'GET',
          headers: {
            'X-CSRFToken': this.getCsrfToken(),
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            this.collections = data.collections || [];
            this.currentPage = data.pagination.page;
            this.totalPages = data.pagination.total_pages;
            this.totalCount = data.pagination.total_count;
          }
        }
      } catch (error) {
        console.error('Error cargando cobros:', error);
      }
    },

    // Eliminar cobro
    async deleteCollection(collectionId) {
      if (!confirm('¿Está seguro de eliminar este cobro?')) {
        return;
      }

      try {
        const response = await fetch(`/api/collections/${collectionId}/delete/`, {
          method: 'DELETE',
          headers: {
            'X-CSRFToken': this.getCsrfToken(),
            'Content-Type': 'application/json'
          }
        });

        const data = await response.json();

        if (response.ok && data.success) {
          this.showModal(data.message || 'Cobro eliminado exitosamente', 'success');
          await this.loadCollections(this.currentPage);
        } else {
          this.showModal(data.error || 'Error al eliminar el cobro', 'danger');
        }
      } catch (error) {
        console.error('Error eliminando cobro:', error);
        this.showModal('Error de conexión al eliminar el cobro', 'danger');
      }
    },

    // Navegación de páginas
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.loadCollections(page);
      }
    },

    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.goToPage(this.currentPage + 1);
      }
    },

    prevPage() {
      if (this.currentPage > 1) {
        this.goToPage(this.currentPage - 1);
      }
    },

    // Utilidades
    getCsrfToken() {
      return document.querySelector('[name=csrfmiddlewaretoken]').value;
    },

    showModal(message, type = 'info') {
      this.modalMessage = {
        show: true,
        type: type,
        text: message,
        icon: this.getIconByType(type)
      };

      // Auto-cerrar después de 5 segundos para mensajes de éxito
      if (type === 'success') {
        setTimeout(() => {
          this.modalMessage.show = false;
        }, 5000);
      }
    },

    getIconByType(type) {
      const icons = {
        success: 'fa-check-circle',
        warning: 'fa-exclamation-triangle',
        danger: 'fa-times-circle',
        info: 'fa-info-circle'
      };
      return icons[type] || 'fa-info-circle';
    },

    closeModal() {
      this.modalMessage.show = false;
    },

    formatCurrency(amount) {
      return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
      }).format(amount);
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('es-ES');
    }
  }
}).mount('#app-collections');
