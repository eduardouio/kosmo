const { createApp } = Vue;

createApp({
  delimiters: ['${', '}'], // Configuración para usar los selectores personalizados
  data() {
    return {
      // Estados de carga
      loading: true,
      saving: false,
      isEditMode: false, // Para saber si estamos editando o creando un cobro
      
      // Datos de clientes
      customers: [],
      filteredCustomers: [],
      customerSearchTerm: '',
      selectedCustomer: null,
      showCustomerDropdown: false,
      
      // Datos de facturas
      pendingInvoices: [],
      filteredInvoices: [],
      
      // Métodos de pago y bancos
      collectionMethods: [],
      popularBanks: [],
      bankConfig: {
        bank_name: '',
        account_number: '',
        account_type: '',
        account_holder: ''
      },
      
      // Estadísticas con valores por defecto
      statistics: {
        pending_invoices: {
          count: 0,
          total_amount: 0
        },
        overdue_collections: {
          count: 0,
          total_amount: 0
        },
        upcoming_due_invoices: {
          count: 0,
          total_amount: 0
        }
      },
      
      // Formulario de cobro
      collectionForm: {
        date: new Date().toISOString().split('T')[0],
        method: '',
        nro_operation: '',
        amount: 0,
        bank: '',
        nro_account: '',
        document: null,
        documentName: '',
        documentPreview: null,
  observations: '',
  notes: ''
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
      
      currentDate: '',
      currentTime: '',
      collectionModal: null // Instancia del modal Bootstrap
    }
  },
  computed: {
    selectedInvoicesCount() {
      return this.filteredInvoices.filter(inv => inv.selected).length;
    },
    
    selectedInvoicesForCollection() {
      return this.filteredInvoices.filter(inv => inv.selected);
    },
    
    totalCollectionAmount() {
      return this.filteredInvoices
        .filter(inv => inv.selected)
        .reduce((sum, inv) => sum + parseFloat(inv.collectionAmount || 0), 0);
    },
    
    totalBalanceAmount() {
      return this.filteredInvoices
        .filter(inv => inv.selected)
        .reduce((sum, inv) => sum + parseFloat(inv.balance || 0), 0);
    },
    
    collectionDifference() {
      return this.totalBalanceAmount - this.totalCollectionAmount;
    },
    
    canSaveCollection() {
      return this.selectedInvoicesCount > 0 && 
              this.collectionForm.date && 
              this.collectionForm.method && 
              this.totalCollectionAmount > 0 &&
              !this.saving &&
              this.validateForm();
    }
  },
  
  mounted() {
    this.initializeDateTime();
    this.loadBankConfig();
    this.loadCollectionContextData();
    
    // Inicializar el modal después de que el DOM esté completamente cargado
    this.$nextTick(() => {
      this.collectionModal = new bootstrap.Modal(document.getElementById('collectionModal'));
    });
  },
  
  methods: {
    async loadBankConfig() {
      try {
        const response = await fetch('/api/bank-config/');
        const data = await response.json();
        
        if (data.success) {
          // Guardar configuración bancaria
          this.bankConfig = data.data;
          
          // Configurar los valores bancarios por defecto en el formulario
          this.collectionForm.bank = data.data.bank_name;
          this.collectionForm.nro_account = data.data.account_number;
        } else {
          console.warn('No se pudo cargar la configuración bancaria:', data.error);
        }
      } catch (error) {
        console.warn('Error al cargar configuración bancaria:', error.message);
      }
    },

    async loadCollectionContextData() {
      try {
        const response = await fetch('/api/collections/context-data/', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          
          console.log('Datos cargados:', {
            customers: data.customers?.length || 0,
            invoices: data.invoices?.length || 0,
            sampleCustomer: data.customers?.[0] || 'No customers',
            sampleInvoice: data.invoices?.[0] || 'No invoices'
          });
          
          this.customers = data.customers || [];
          this.filteredCustomers = [...this.customers];
          this.pendingInvoices = data.invoices || [];
          this.filteredInvoices = [...this.pendingInvoices];
          this.collectionMethods = data.payment_methods || [];
          this.popularBanks = data.popular_banks || [];
          this.statistics = data.statistics || {};
          
          // Inicializar montos de cobro
          this.filteredInvoices.forEach(invoice => {
            if (!invoice.collectionAmount) {
              invoice.collectionAmount = parseFloat(invoice.balance || 0);
            }
            invoice.selected = false;
          });
          
        } else {
          this.showError('Error al cargar datos de cobros');
        }
      } catch (error) {
        console.error('Error loading collection context:', error);
        this.showError('Error de conexión al cargar datos');
      } finally {
        this.loading = false;
      }
    },
    
    // ===== AUTOCOMPLETE DE CLIENTES =====
    filterCustomers() {
      if (!this.customerSearchTerm.trim()) {
        this.filteredCustomers = [...this.customers];
        this.showCustomerDropdown = true;
        return;
      }
      
      const searchTerm = this.customerSearchTerm.toLowerCase();
      this.filteredCustomers = this.customers.filter(customer => 
        customer.name.toLowerCase().includes(searchTerm) ||
        customer.business_tax_id.toLowerCase().includes(searchTerm)
      );
      this.showCustomerDropdown = true;
    },
    
    selectCustomer(customer) {
      console.log('Cliente seleccionado:', customer);
      this.selectedCustomer = customer;
      this.customerSearchTerm = customer.name;
      this.showCustomerDropdown = false;
      this.filterInvoicesByCustomer();
    },
    
    clearCustomerFilter() {
      this.selectedCustomer = null;
      this.customerSearchTerm = '';
      this.filteredCustomers = [...this.customers];
      this.filteredInvoices = [...this.pendingInvoices];
      this.showCustomerDropdown = false;
    },
    
    hideCustomerDropdown() {
      setTimeout(() => {
        this.showCustomerDropdown = false;
      }, 200);
    },
    
    filterInvoicesByCustomer() {
      if (this.selectedCustomer) {
        console.log('Filtrando por cliente:', {
          selectedCustomer: this.selectedCustomer,
          totalInvoices: this.pendingInvoices.length,
          sampleInvoice: this.pendingInvoices[0] || 'No hay facturas'
        });
        
        this.filteredInvoices = this.pendingInvoices.filter(invoice => {
          // Convertir ambos valores a string para comparación segura
          const invoiceCustomerId = String(invoice.customer_id);
          const selectedCustomerId = String(this.selectedCustomer.id);
          const matches = invoiceCustomerId === selectedCustomerId;
          
          if (matches) {
            console.log('Factura coincide:', invoice);
          }
          
          return matches;
        });
        
        console.log('Facturas filtradas:', this.filteredInvoices.length);
      } else {
        this.filteredInvoices = [...this.pendingInvoices];
      }
      
      // Reset selections
      this.filteredInvoices.forEach(invoice => {
        invoice.selected = false;
        invoice.collectionAmount = parseFloat(invoice.balance || 0);
      });
    },
    
    // ===== MANEJO DE FACTURAS =====
    updateCollectionAmount(invoice) {
      if (invoice.selected) {
        if (!invoice.collectionAmount || invoice.collectionAmount <= 0) {
          invoice.collectionAmount = parseFloat(invoice.balance || 0);
        }
      }
      this.updateCollectionFormAmount();
    },
    
    validateCollectionAmount(invoice) {
      const maxAmount = parseFloat(invoice.balance || 0);
      const amount = parseFloat(invoice.collectionAmount || 0);
      
      if (amount > maxAmount) {
        invoice.collectionAmount = maxAmount;
      } else if (amount < 0) {
        invoice.collectionAmount = 0;
      }
      
      this.updateCollectionFormAmount();
    },
    
    updateCollectionFormAmount() {
      this.collectionForm.amount = this.totalCollectionAmount;
    },
    
    clearSelection() {
      this.filteredInvoices.forEach(invoice => {
        invoice.selected = false;
        invoice.collectionAmount = parseFloat(invoice.balance || 0);
      });
      this.updateCollectionFormAmount();
    },
    
    selectAllInvoices() {
      this.filteredInvoices.forEach(invoice => {
        if (parseFloat(invoice.balance) > 0) {
          invoice.selected = true;
          invoice.collectionAmount = parseFloat(invoice.balance || 0);
        }
      });
      this.updateCollectionFormAmount();
    },
    
    // ===== MODAL =====
    openCollectionModal() {
      if (this.selectedInvoicesCount === 0) {
        this.showWarning('Debe seleccionar al menos una factura para cobrar');
        return;
      }
      
      this.updateCollectionFormAmount();
      this.clearModalMessage();
      this.clearFormErrors();
      
      // Usar la instancia del modal ya creada
      if (this.collectionModal) {
        this.collectionModal.show();
      } else {
        console.error('El modal no se ha inicializado correctamente');
      }
    },
    
    // ===== MANEJO DE ARCHIVOS =====
    handleFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        // Validar tamaño (5MB máximo)
        if (file.size > 5 * 1024 * 1024) {
          this.showModalError('El archivo no puede ser mayor a 5MB');
          this.$refs.documentFile.value = '';
          return;
        }
        
        // Validar tipo de archivo
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf', 
                              'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (!allowedTypes.includes(file.type)) {
          this.showModalError('Tipo de archivo no permitido. Use JPG, PNG, PDF o DOC');
          this.$refs.documentFile.value = '';
          return;
        }
        
        this.collectionForm.document = file;
        this.collectionForm.documentName = file.name;
        
        // Crear preview para imágenes
        if (file.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onload = (e) => {
            this.collectionForm.documentPreview = e.target.result;
          };
          reader.readAsDataURL(file);
        } else {
          this.collectionForm.documentPreview = null;
        }
        
        this.showModalSuccess(`Archivo "${file.name}" seleccionado correctamente`);
      }
    },
    
    // ===== SISTEMA DE MENSAJES DEL MODAL =====
    showModalMessage(text, type = 'info') {
      const icons = {
        success: 'fa-check-circle',
        warning: 'fa-exclamation-triangle',
        danger: 'fa-exclamation-circle',
        info: 'fa-info-circle'
      };
      
      this.modalMessage = {
        show: true,
        type: type,
        text: text,
        icon: icons[type] || icons.info
      };
      
      // Auto-ocultar después de 5 segundos para mensajes de éxito
      if (type === 'success') {
        setTimeout(() => {
          this.clearModalMessage();
        }, 5000);
      }
    },
    
    showModalSuccess(text) {
      this.showModalMessage(text, 'success');
    },
    
    showModalWarning(text) {
      this.showModalMessage(text, 'warning');
    },
    
    showModalError(text) {
      this.showModalMessage(text, 'danger');
    },
    
    clearModalMessage() {
      this.modalMessage.show = false;
    },
    
    // ===== VALIDACIONES =====
    validateForm() {
      this.clearFormErrors();
      let isValid = true;
      
      if (!this.collectionForm.date) {
        this.formErrors.date = 'La fecha es requerida';
        isValid = false;
      }
      
      if (!this.collectionForm.method) {
        this.formErrors.method = 'El método de cobro es requerido';
        isValid = false;
      }
      
      if (this.totalCollectionAmount <= 0) {
        this.formErrors.amount = 'El monto debe ser mayor a cero';
        isValid = false;
      }
      
      return isValid;
    },
    
    clearFormErrors() {
      this.formErrors = {
        date: '',
        method: '',
        amount: '',
        document: ''
      };
    },
    
    // ===== GUARDAR COBRO =====
    async saveCollection() {
      if (!this.validateForm()) {
        this.showModalError('Por favor corrija los errores del formulario');
        return;
      }
      
      this.saving = true;
      this.clearModalMessage();
      
      try {
        await this.createCollection();
      } catch (error) {
        console.error('Error saving collection:', error);
        this.showModalError('Error al guardar el cobro: ' + error.message);
      } finally {
        this.saving = false;
      }
    },
    
    // Crear un nuevo cobro
    async createCollection() {
      // Preparar datos base
      const collectionData = {
        date: this.collectionForm.date,
        method: this.collectionForm.method,
        amount: parseFloat(this.totalCollectionAmount || 0),
        bank: this.collectionForm.bank || '',
        nro_account: this.collectionForm.nro_account || '',
        nro_operation: this.collectionForm.nro_operation || '',
        observations: this.collectionForm.observations || '',
        notes: this.collectionForm.notes || '',
        invoices: this.selectedInvoicesForCollection.map(inv => ({
          invoice_id: inv.id,
          amount: parseFloat(inv.collectionAmount || 0)
        }))
      };

      // CSRF token robusto
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value 
                      || document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
                      || '';
      if (!csrfToken) {
        this.showModalError('No se pudo obtener el token CSRF');
        return;
      }

      // Construir request: usar FormData si hay documento
      const hasDocument = !!this.collectionForm.document;
      const requestOptions = {
        method: 'POST',
        headers: hasDocument ? { 'X-CSRFToken': csrfToken } : {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: undefined
      };

      if (hasDocument) {
        const formData = new FormData();
        // Agregar campos; invoices como string JSON
        Object.entries(collectionData).forEach(([key, value]) => {
          if (key === 'invoices') {
            formData.append('invoices', JSON.stringify(value));
          } else {
            formData.append(key, value);
          }
        });
        formData.append('document', this.collectionForm.document);
        requestOptions.body = formData;
      } else {
        requestOptions.body = JSON.stringify(collectionData);
      }

      const response = await fetch('/api/collections/', requestOptions);

      const result = await response.json().catch(() => ({}));
      if (response.ok) {
        this.showModalSuccess('Cobro registrado correctamente');

        // Actualizar facturas después del cobro exitoso
        this.updateInvoicesAfterCollection(this.selectedInvoicesForCollection, result?.collection || result);

        // Intentar descargar automáticamente el PDF del cobro
        const collectionId = result?.collection?.id || result?.id || result?.payment?.id; // fallback por si la API usa otra clave
        if (collectionId) {
          setTimeout(() => this.downloadCollectionPDF(collectionId), 500);
        }

        // Cerrar modal y resetear
        setTimeout(() => {
          const modal = bootstrap.Modal.getInstance(document.getElementById('collectionModal'));
          modal?.hide();
          this.resetCollectionForm();
        }, 1500);
      } else {
        const msg = result?.error || result?.message || 'Error desconocido al procesar el cobro';
        throw new Error(msg);
      }
    },
    
    // Actualizar facturas después del cobro exitoso
    updateInvoicesAfterCollection(selectedInvoices, collectionData) {
      selectedInvoices.forEach(invoice => {
        const collectedAmount = parseFloat(invoice.collectionAmount || 0);
        
        // Actualizar los montos de la factura
        invoice.paid_amount = parseFloat(invoice.paid_amount || 0) + collectedAmount;
        invoice.balance = parseFloat(invoice.balance || 0) - collectedAmount;
        
        // Desmarcar y resetear
        invoice.selected = false;
        invoice.collectionAmount = invoice.balance;
      });
      
      // Filtrar facturas con saldo cero
      this.removeZeroBalanceInvoices();
      
      // Actualizar estadísticas
      this.updateStatistics();
      
      // Actualizar la lista filtrada
      this.refreshFilteredInvoices();
    },
    
    // Eliminar facturas con saldo cero o negativo
    removeZeroBalanceInvoices() {
      this.pendingInvoices = this.pendingInvoices.filter(invoice => 
        parseFloat(invoice.balance || 0) > 0
      );
    },
    
    // Refrescar la lista filtrada después de cambios
    refreshFilteredInvoices() {
      if (this.selectedCustomer) {
        this.filterInvoicesByCustomer();
      } else {
        this.filteredInvoices = [...this.pendingInvoices];
      }
    },
    
    // Método para actualizar una factura específica (útil para actualizaciones en tiempo real)
    updateInvoiceById(invoiceId, updates) {
      // Actualizar en la lista principal
      const mainIndex = this.pendingInvoices.findIndex(inv => inv.id === invoiceId);
      if (mainIndex !== -1) {
        Object.assign(this.pendingInvoices[mainIndex], updates);
      }
      
      // Actualizar en la lista filtrada
      const filteredIndex = this.filteredInvoices.findIndex(inv => inv.id === invoiceId);
      if (filteredIndex !== -1) {
        Object.assign(this.filteredInvoices[filteredIndex], updates);
      }
    },
    
    // Recalcular estadísticas después de cambios
    updateStatistics() {
      const totalInvoices = this.pendingInvoices.length;
      const totalPending = this.pendingInvoices.reduce((sum, inv) => 
        sum + parseFloat(inv.balance || 0), 0
      );
      
      // Calcular facturas vencidas
      const overdueInvoices = this.pendingInvoices.filter(inv => inv.days_overdue > 0);
      const overdueAmount = overdueInvoices.reduce((sum, inv) => 
        sum + parseFloat(inv.balance || 0), 0
      );
      
      // Calcular facturas por vencer
      const upcomingDueInvoices = this.pendingInvoices.filter(inv => 
        inv.days_overdue >= -30 && inv.days_overdue <= 0
      );
      const upcomingDueAmount = upcomingDueInvoices.reduce((sum, inv) => 
        sum + parseFloat(inv.balance || 0), 0
      );
      
      this.statistics = {
        pending_invoices: {
          count: totalInvoices,
          total_amount: totalPending
        },
        overdue_collections: {
          count: overdueInvoices.length,
          total_amount: overdueAmount
        },
        upcoming_due_invoices: {
          count: upcomingDueInvoices.length,
          total_amount: upcomingDueAmount
        }
      };
    },
    
    // ===== GESTIÓN DE ELIMINACIÓN DE COBROS =====
    
    // Eliminar un cobro individual
    async deleteCollection(collectionId) {
      if (!confirm('¿Está seguro de que desea anular este cobro?')) {
        return;
      }
      
      try {
        const response = await fetch(`/api/collections-void/${collectionId}/`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          }
        });
        
        if (response.ok) {
          this.showSuccess('Cobro anulado correctamente');
          // Recargar datos
          await this.loadCollectionContextData();
        } else {
          const errorData = await response.json();
          this.showError(errorData.error || 'Error al anular el cobro');
        }
      } catch (error) {
        console.error('Error deleting collection:', error);
        this.showError('Error de conexión al anular el cobro');
      }
    },
    
    // Eliminar múltiples cobros (bulk delete)
    async deleteMultipleCollections(collectionIds) {
      if (!collectionIds || collectionIds.length === 0) {
        this.showWarning('No hay cobros seleccionados para anular');
        return;
      }
      
      if (!confirm(`¿Está seguro de que desea anular ${collectionIds.length} cobros?`)) {
        return;
      }
      
      try {
        const response = await fetch('/api/collections-void/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          },
          body: JSON.stringify({
            collection_ids: collectionIds
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          this.showSuccess(data.message || 'Cobros anulados correctamente');
          // Recargar datos
          await this.loadCollectionContextData();
        } else {
          const errorData = await response.json();
          this.showError(errorData.error || 'Error al anular los cobros');
        }
      } catch (error) {
        console.error('Error deleting multiple collections:', error);
        this.showError('Error de conexión al anular los cobros');
      }
    },
    
    // ===== UTILIDADES =====
    goBack() {
      window.history.back();
    },
    
    initializeDateTime() {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      
      this.currentDate = `${year}-${month}-${day}`;
      this.currentTime = `${hours}:${minutes}`;
      
      // Establecer fecha actual por defecto
      this.collectionForm.date = this.currentDate;
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES');
    },
    
    formatCurrency(amount) {
      if (isNaN(amount) || amount === null || amount === undefined) return '0.00';
      return parseFloat(amount).toLocaleString('es-ES', { 
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2 
      });
    },
    
    showError(message) {
      this.showNotification(message, 'error');
    },
    
    showSuccess(message) {
      this.showNotification(message, 'success');
    },
    
    showWarning(message) {
      this.showNotification(message, 'warning');
    },
    
    showNotification(message, type) {
      // Implementar sistema de notificaciones toast o similar
      console.log(`${type.toUpperCase()}: ${message}`);
      
      // Por ahora, usar alert básico
      if (type === 'error') {
        alert('Error: ' + message);
      } else if (type === 'success') {
        alert('Éxito: ' + message);
      } else if (type === 'warning') {
        alert('Advertencia: ' + message);
      }
    },
    
    // Resetear el formulario de cobro
    resetCollectionForm() {
      this.collectionForm = {
        date: this.currentDate,
        method: '',
        nro_operation: '',
        amount: 0,
        bank: this.bankConfig.bank_name || '',
        nro_account: this.bankConfig.account_number || '',
        document: null,
        documentName: '',
        documentPreview: null,
  observations: '',
  notes: ''
      };
      
      // Limpiar el input de archivo
      if (this.$refs.documentFile) {
        this.$refs.documentFile.value = '';
      }
      
      this.clearFormErrors();
      this.clearModalMessage();
    },

    // ===== DESCARGA DE PDF =====
    /**
     * Descarga automáticamente el PDF del comprobante de cobro
     * @param {number} collectionId - ID del cobro para descargar el PDF
     */
    downloadCollectionPDF(collectionId) {
      try {
        if (!collectionId) {
          this.showWarning('No se pudo determinar el ID del cobro para descargar el PDF.');
          return;
        }

        const pdfUrl = `/trade/collection/${collectionId}/pdf/`;

        const link = document.createElement('a');
        link.href = pdfUrl;
        link.download = `comprobante_cobro_${collectionId}.pdf`;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        setTimeout(() => {
          if (document.body.contains(link)) document.body.removeChild(link);
        }, 1000);
      } catch (error) {
        console.error('Error al descargar el PDF del cobro:', error);
        try {
          const pdfUrl = `/trade/collection/${collectionId}/pdf/`;
          window.open(pdfUrl, '_blank', 'noopener,noreferrer');
        } catch (fallbackError) {
          console.error('Error en método de respaldo de descarga:', fallbackError);
        }
      }
    },

    /**
     * Prueba manual de descarga de PDF
     */
    testDownloadPDF(collectionId) {
      const id = collectionId || parseInt(prompt('ID de cobro para descargar PDF:'));
      if (id) this.downloadCollectionPDF(id);
    }
  }
}).mount('#collectionsApp');