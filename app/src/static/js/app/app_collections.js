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
      bankConfig: {
        bank_name: '',
        account_number: '',
        account_type: '',
        account_holder: ''
      },
      
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
      
      currentDate: '',
      currentTime: '',
      
      // Modo edición
      isEditMode: false,
      editingCollectionId: null,
      
      // Lista de cobros
      collections: [],
      currentPage: 1,
      pageSize: 10,
      totalPages: 0,
      totalCount: 0
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
    
    // Verificar si se debe cargar un cobro para edición
    this.checkForEditMode();
  },
  
  methods: {
    async loadBankConfig() {
      try {
        const response = await fetch('/api/bank-config/');
        const data = await response.json();
        
        if (data.success) {
          this.bankConfig = data.data;
          this.collectionForm.bank = data.data.bank_name;
          this.collectionForm.accountNumber = data.data.account_number;
        } else {
          console.warn('No se pudo cargar la configuración bancaria:', data.error);
        }
      } catch (error) {
        console.warn('Error al cargar configuración bancaria:', error.message);
      }
    },

    async loadCollectionContextData() {
      try {
        this.loading = true;
        const response = await fetch('/api/collections/context-data/');
        const data = await response.json();
        
        if (data.success) {
          this.customers = data.customers;
          this.filteredCustomers = [...this.customers];
          this.pendingInvoices = data.invoices.map(invoice => ({
            ...invoice,
            selected: false,
            collectionAmount: invoice.balance
          }));
          this.filteredInvoices = [...this.pendingInvoices];
          this.paymentMethods = data.payment_methods;
          this.popularBanks = data.popular_banks || [];
          this.statistics = data.statistics;
          this.collectionForm.date = data.current_date;
        } else {
          this.showError('Error al cargar los datos: ' + data.error);
        }
      } catch (error) {
        this.showError('Error de conexión: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    
    // ===== AUTOCOMPLETE DE CLIENTES =====
    filterCustomers() {
      if (this.customerSearchTerm.trim() === '') {
        this.filteredCustomers = [...this.customers];
      } else {
        const searchTerm = this.customerSearchTerm.toLowerCase();
        this.filteredCustomers = this.customers.filter(customer => 
          customer.name.toLowerCase().includes(searchTerm) ||
          (customer.document_number && customer.document_number.includes(searchTerm))
        );
      }
      this.showCustomerDropdown = true;
    },
    
    selectCustomer(customer) {
      this.selectedCustomer = customer;
      this.customerSearchTerm = customer.name;
      this.showCustomerDropdown = false;
      this.filterInvoicesByCustomer();
    },
    
    clearCustomerFilter() {
      this.selectedCustomer = null;
      this.customerSearchTerm = '';
      this.showCustomerDropdown = false;
      this.filteredInvoices = [...this.pendingInvoices];
      this.updateCollectionFormAmount();
    },
    
    hideCustomerDropdown() {
      setTimeout(() => {
        this.showCustomerDropdown = false;
      }, 150);
    },
    
    filterInvoicesByCustomer() {
      if (!this.selectedCustomer) {
        this.filteredInvoices = [...this.pendingInvoices];
      } else {
        this.filteredInvoices = this.pendingInvoices.filter(
          invoice => invoice.customer_id == this.selectedCustomer.id
        );
      }
      this.updateCollectionFormAmount();
    },
    
    // ===== MANEJO DE FACTURAS =====
    updateCollectionAmount(invoice) {
      if (invoice.selected) {
        invoice.collectionAmount = invoice.balance;
      } else {
        invoice.collectionAmount = 0;
      }
      this.updateCollectionFormAmount();
    },
    
    validateCollectionAmount(invoice) {
      const amount = parseFloat(invoice.collectionAmount);
      const balance = parseFloat(invoice.balance);
      
      if (amount > balance) {
        invoice.collectionAmount = balance;
        if (!document.getElementById('collectionModal').classList.contains('show')) {
          this.showWarning(`El monto no puede ser mayor al saldo ($${this.formatCurrency(balance)})`);
        }
      }
      if (amount < 0) {
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
        invoice.collectionAmount = 0;
      });
      this.updateCollectionFormAmount();
    },
    
    selectAllInvoices() {
      this.filteredInvoices.forEach(invoice => {
        invoice.selected = true;
        invoice.collectionAmount = invoice.balance;
      });
      this.updateCollectionFormAmount();
    },
    
    // ===== MODAL =====
    openCollectionModal() {
      if (this.selectedInvoicesCount === 0) {
        this.showModalWarning('Debe seleccionar al menos una factura para cobrar');
        return;
      }
      
      this.clearFormErrors();
      this.clearModalMessage();
      this.updateCollectionFormAmount();
      
      // Limpiar el archivo previo
      this.collectionForm.document = null;
      this.collectionForm.documentName = '';
      this.collectionForm.documentPreview = null;
      if (this.$refs.documentFile) {
        this.$refs.documentFile.value = '';
      }
      
      // Abrir modal usando Bootstrap
      const modal = new bootstrap.Modal(document.getElementById('collectionModal'));
      modal.show();
    },
    
    // ===== MANEJO DE ARCHIVOS =====
    handleFileChange(event) {
      const file = event.target.files[0];
      if (!file) {
        this.collectionForm.document = null;
        this.collectionForm.documentName = '';
        this.collectionForm.documentPreview = null;
        return;
      }
      
      // Validar tamaño del archivo (máximo 5MB)
      const maxSize = 5 * 1024 * 1024; // 5MB en bytes
      if (file.size > maxSize) {
        this.showModalError('El archivo es demasiado grande. Máximo 5MB permitido.');
        event.target.value = '';
        return;
      }
      
      // Validar tipo de archivo
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 
                           'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!allowedTypes.includes(file.type)) {
        this.showModalError('Tipo de archivo no permitido. Use JPG, PNG, PDF o DOC.');
        event.target.value = '';
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
        this.collectionForm.documentPreview = 'document';
      }
      
      this.clearModalMessage();
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
      
      // Validar que la fecha no sea futura
      const collectionDate = new Date(this.collectionForm.date);
      const today = new Date();
      if (collectionDate > today) {
        this.formErrors.date = 'La fecha no puede ser futura';
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
        this.showModalError('Por favor, corrija los errores en el formulario');
        return;
      }
      
      // Decidir si crear o actualizar según el modo
      if (this.isEditMode) {
        await this.updateCollection();
      } else {
        await this.createCollection();
      }
    },
    
    // Crear un nuevo cobro
    async createCollection() {
      try {
        this.saving = true;
        this.clearModalMessage();
        
        const selectedInvoices = this.filteredInvoices.filter(inv => inv.selected);
        
        // Preparar los datos para la API REST
        const collectionData = {
          date: this.collectionForm.date,
          method: this.collectionForm.method,
          amount: parseFloat(this.collectionForm.amount),
          bank: this.collectionForm.bank || '',
          nro_account: this.collectionForm.accountNumber || '',
          nro_operation: this.collectionForm.reference || '',
          observations: this.collectionForm.observations || '',
          invoices: selectedInvoices.map(invoice => ({
            invoice_id: invoice.id,
            amount: parseFloat(invoice.collectionAmount)
          }))
        };
        
        console.log('Enviando datos al API:', collectionData);
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value 
                         || document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
                         || '';
        
        if (!csrfToken) {
          console.error('No se encontró el token CSRF');
          this.showModalError('Error: No se pudo obtener el token de seguridad');
          return;
        }
        
        // Realizar petición a la API
        const response = await fetch('/api/collections/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
          },
          body: JSON.stringify(collectionData)
        });
        
        const result = await response.json();
        
        console.log('Respuesta del API:', { status: response.status, result });
        
        if (response.ok && result.success) {
          this.showModalSuccess('¡Cobro registrado correctamente!');
          
          // Actualizar las facturas localmente
          this.updateInvoicesAfterCollection(selectedInvoices, result.collection);
          
          // Cerrar modal después de un momento
          setTimeout(() => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('collectionModal'));
            modal.hide();
            
            // Resetear formulario y selección
            this.resetCollectionForm();
            this.clearSelection();
          }, 1500);
        } else {
          console.error('Error del API:', result);
          if (result.errors) {
            this.formErrors = result.errors;
          } else {
            this.showModalError(result.error || 'Error al procesar el cobro');
          }
        }
        
      } catch (error) {
        console.error('Error al guardar cobro:', error);
        this.showModalError('Error de conexión. Intente nuevamente.');
      } finally {
        this.saving = false;
      }
    },
    
    // Actualizar facturas después del cobro exitoso
    updateInvoicesAfterCollection(selectedInvoices, collectionData) {
      selectedInvoices.forEach(invoice => {
        const collectedAmount = parseFloat(invoice.collectionAmount);
        
        // Actualizar el monto cobrado y calcular nuevo balance
        invoice.paid_amount = (parseFloat(invoice.paid_amount) || 0) + collectedAmount;
        invoice.balance = parseFloat(invoice.total_amount) - invoice.paid_amount;
        
        // Resetear el monto de cobro y deseleccionar
        invoice.collectionAmount = 0;
        invoice.selected = false;
      });
      
      // Recalcular estadísticas
      this.updateStatistics();
    },
    
    // Recalcular estadísticas después de cambios
    updateStatistics() {
      const pendingInvoices = this.pendingInvoices.filter(inv => inv.balance > 0);
      const overdueInvoices = pendingInvoices.filter(inv => inv.days_overdue > 0);
      const upcomingDueInvoices = pendingInvoices.filter(inv => inv.days_overdue <= 0 && inv.days_overdue >= -30);
      
      this.statistics = {
        total_invoices: pendingInvoices.length,
        total_pending: pendingInvoices.reduce((sum, inv) => sum + parseFloat(inv.balance), 0),
        overdue_amount: overdueInvoices.reduce((sum, inv) => sum + parseFloat(inv.balance), 0),
        due_soon_amount: upcomingDueInvoices.reduce((sum, inv) => sum + parseFloat(inv.balance), 0)
      };
    },
    
    // ===== GESTIÓN DE ELIMINACIÓN DE COBROS =====
    
    // Eliminar un cobro individual
    async deleteCollection(collectionId) {
      if (!confirm('¿Está seguro de que desea eliminar este cobro? Esta acción no se puede deshacer.')) {
        return;
      }
      
      try {
        const response = await fetch(`/api/collections/${collectionId}/delete/`, {
          method: 'DELETE',
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          }
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
          this.showSuccess('Cobro eliminado correctamente');
          // Recargar datos para reflejar los cambios
          await this.loadCollectionContextData();
          await this.loadCollections(this.currentPage);
        } else {
          this.showError(result.error || 'Error al eliminar el cobro');
        }
        
      } catch (error) {
        console.error('Error al eliminar cobro:', error);
        this.showError('Error de conexión al eliminar el cobro');
      }
    },
    
    // Eliminar múltiples cobros (bulk delete)
    async deleteMultipleCollections(collectionIds) {
      if (!collectionIds || collectionIds.length === 0) {
        this.showWarning('No hay cobros seleccionados para eliminar');
        return;
      }
      
      if (!confirm(`¿Está seguro de que desea eliminar ${collectionIds.length} cobro(s)? Esta acción no se puede deshacer.`)) {
        return;
      }
      
      try {
        const response = await fetch('/api/collections/delete/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          },
          body: JSON.stringify({
            collection_ids: collectionIds
          })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
          this.showSuccess(`${result.deleted_collections.length} cobro(s) eliminado(s) correctamente`);
          // Recargar datos para reflejar los cambios
          await this.loadCollectionContextData();
          await this.loadCollections(this.currentPage);
        } else {
          this.showError(result.error || 'Error al eliminar los cobros');
        }
        
      } catch (error) {
        console.error('Error al eliminar cobros múltiples:', error);
        this.showError('Error de conexión al eliminar los cobros');
      }
    },
    
    // ===== GESTIÓN DE EDICIÓN DE COBROS =====
    
    // Cargar un cobro existente para edición
    async loadCollectionForEdit(collectionId) {
      try {
        const response = await fetch(`/api/collections/${collectionId}/`, {
          method: 'GET',
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          const collection = data.collection;
          
          // Cargar datos del cobro en el formulario
          this.collectionForm = {
            id: collection.id,
            date: collection.date,
            method: collection.method,
            amount: collection.amount,
            reference: collection.nro_operation || '',
            bank: collection.bank || '',
            accountNumber: collection.nro_account || '',
            observations: collection.observations || '',
            document: null,
            documentName: '',
            documentPreview: null
          };
          
          // Marcar que estamos en modo edición
          this.isEditMode = true;
          this.editingCollectionId = collectionId;
          
          // Seleccionar las facturas relacionadas con este cobro
          if (collection.invoices) {
            collection.invoices.forEach(invoiceDetail => {
              const invoice = this.filteredInvoices.find(inv => inv.id === invoiceDetail.invoice_id);
              if (invoice) {
                invoice.selected = true;
                invoice.collectionAmount = parseFloat(invoiceDetail.amount);
              }
            });
          }
          
          this.updateCollectionFormAmount();
          
          // Abrir el modal
          const modal = new bootstrap.Modal(document.getElementById('collectionModal'));
          modal.show();
          
        } else {
          this.showError('No se pudo cargar el cobro para edición');
        }
        
      } catch (error) {
        console.error('Error al cargar cobro para edición:', error);
        this.showError('Error de conexión al cargar el cobro');
      }
    },
    
    // Actualizar un cobro existente
    async updateCollection() {
      if (!this.validateForm()) {
        this.showModalError('Por favor, corrija los errores en el formulario');
        return;
      }
      
      try {
        this.saving = true;
        this.clearModalMessage();
        
        const selectedInvoices = this.filteredInvoices.filter(inv => inv.selected);
        
        const collectionData = {
          date: this.collectionForm.date,
          method: this.collectionForm.method,
          amount: parseFloat(this.collectionForm.amount),
          bank: this.collectionForm.bank || '',
          nro_account: this.collectionForm.accountNumber || '',
          nro_operation: this.collectionForm.reference || '',
          observations: this.collectionForm.observations || '',
          invoices: selectedInvoices.map(invoice => ({
            invoice_id: invoice.id,
            amount: parseFloat(invoice.collectionAmount)
          }))
        };
        
        const response = await fetch(`/api/collections/${this.editingCollectionId}/`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          },
          body: JSON.stringify(collectionData)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
          this.showModalSuccess('¡Cobro actualizado correctamente!');
          
          // Recargar datos para reflejar cambios
          await this.loadCollectionContextData();
          
          setTimeout(() => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('collectionModal'));
            modal.hide();
            this.exitEditMode();
          }, 1500);
          
        } else {
          if (result.errors) {
            this.formErrors = result.errors;
          } else {
            this.showModalError(result.error || 'Error al actualizar el cobro');
          }
        }
        
      } catch (error) {
        console.error('Error al actualizar cobro:', error);
        this.showModalError('Error de conexión al actualizar el cobro');
      } finally {
        this.saving = false;
      }
    },
    
    // Salir del modo edición
    exitEditMode() {
      this.isEditMode = false;
      this.editingCollectionId = null;
      this.resetCollectionForm();
      this.clearSelection();
    },
    
    // Resetear el formulario de cobro
    resetCollectionForm() {
      this.collectionForm = {
        date: this.currentDate,
        method: '',
        reference: '',
        amount: 0,
        bank: this.bankConfig.bank_name || '',
        accountNumber: this.bankConfig.account_number || '',
        observations: '',
        document: null,
        documentName: '',
        documentPreview: null
      };
      this.clearFormErrors();
    },
    
    // ===== LISTA DE COBROS =====
    
    // Cargar lista de cobros con paginación
    async loadCollections(page = 1) {
      try {
        const response = await fetch(`/api/collections/?page=${page}&page_size=${this.pageSize}`, {
          method: 'GET',
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
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
    
    // ===== UTILIDADES =====
    goBack() {
      window.location.href = '/cobros/';
    },
    
    initializeDateTime() {
      const now = new Date();
      this.currentDate = now.toISOString().split('T')[0]; // YYYY-MM-DD format
      this.currentTime = now.toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    },
    
    formatDate(dateString) {
      if (!dateString) return '-';
      return new Date(dateString).toLocaleDateString('es-ES');
    },
    
    // Verificar si se debe cargar un cobro para edición desde URL
    checkForEditMode() {
      const urlParams = new URLSearchParams(window.location.search);
      const editCollectionId = urlParams.get('edit');
      
      if (editCollectionId) {
        // Cargar el cobro para edición después de que se carguen los datos de contexto
        setTimeout(() => {
          this.loadCollectionForEdit(editCollectionId);
        }, 1000); // Dar tiempo para que se carguen las facturas
      }
    },
    
    formatCurrency(amount) {
      return parseFloat(amount || 0).toLocaleString('es-ES', {
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
      const icons = {
        error: '❌',
        success: '✅',
        warning: '⚠️'
      };
      
      alert(`${icons[type]} ${message}`);
    }
  }
}).mount('#collectionsApp');