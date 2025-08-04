const { createApp } = Vue;

createApp({
  data() {
    return {
      loading: true,
      saving: false,
      suppliers: [],
      filteredSuppliers: [],
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
      
      // Autocomplete de proveedores
      supplierSearchTerm: '',
      selectedSupplier: null,
      showSupplierDropdown: false,
      
      // Formulario de pago
      paymentForm: {
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
      editingPaymentId: null
    }
  },
  computed: {
    selectedInvoicesCount() {
      return this.filteredInvoices.filter(inv => inv.selected).length;
    },
    
    selectedInvoicesForPayment() {
      return this.filteredInvoices.filter(inv => inv.selected);
    },
    
    totalPaymentAmount() {
      return this.filteredInvoices
        .filter(inv => inv.selected)
        .reduce((sum, inv) => sum + parseFloat(inv.paymentAmount || 0), 0);
    },
    
    totalBalanceAmount() {
      return this.filteredInvoices
        .filter(inv => inv.selected)
        .reduce((sum, inv) => sum + parseFloat(inv.balance || 0), 0);
    },
    
    paymentDifference() {
      return this.totalBalanceAmount - this.totalPaymentAmount;
    },
    
    canSavePayment() {
      return this.selectedInvoicesCount > 0 && 
             this.paymentForm.date && 
             this.paymentForm.method && 
             this.totalPaymentAmount > 0 &&
             !this.saving &&
             this.validateForm();
    }
  },
  
  mounted() {
    this.initializeDateTime();
    this.loadBankConfig();
    this.loadPaymentContextData();
    
    // Verificar si se debe cargar un pago para edición
    this.checkForEditMode();
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
          this.paymentForm.bank = data.data.bank_name;
          this.paymentForm.accountNumber = data.data.account_number;
        } else {
          console.warn('No se pudo cargar la configuración bancaria:', data.error);
        }
      } catch (error) {
        console.warn('Error al cargar configuración bancaria:', error.message);
      }
    },

    async loadPaymentContextData() {
      try {
        this.loading = true;
        const response = await fetch('/api/payments/context-data/');
        const data = await response.json();
        
        if (data.success) {
          this.suppliers = data.suppliers;
          this.filteredSuppliers = [...this.suppliers];
          this.pendingInvoices = data.pending_invoices.map(invoice => ({
            ...invoice,
            selected: false,
            paymentAmount: invoice.balance
          }));
          this.filteredInvoices = [...this.pendingInvoices];
          this.paymentMethods = data.payment_methods;
          this.popularBanks = data.popular_banks;
          this.statistics = data.statistics;
          this.paymentForm.date = data.current_date;
        } else {
          this.showError('Error al cargar los datos: ' + data.error);
        }
      } catch (error) {
        this.showError('Error de conexión: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    
    // ===== AUTOCOMPLETE DE PROVEEDORES =====
    filterSuppliers() {
      if (this.supplierSearchTerm.trim() === '') {
        this.filteredSuppliers = [...this.suppliers];
      } else {
        const searchTerm = this.supplierSearchTerm.toLowerCase();
        this.filteredSuppliers = this.suppliers.filter(supplier => 
          supplier.name.toLowerCase().includes(searchTerm) ||
          (supplier.business_tax_id && supplier.business_tax_id.includes(searchTerm))
        );
      }
      this.showSupplierDropdown = true;
    },
    
    selectSupplier(supplier) {
      this.selectedSupplier = supplier;
      this.supplierSearchTerm = supplier.name;
      this.showSupplierDropdown = false;
      this.filterInvoicesBySupplier();
    },
    
    clearSupplierFilter() {
      this.selectedSupplier = null;
      this.supplierSearchTerm = '';
      this.showSupplierDropdown = false;
      this.filteredInvoices = [...this.pendingInvoices];
      this.updatePaymentFormAmount();
    },
    
    hideSupplierDropdown() {
      // Delay para permitir que el click en el dropdown se registre
      setTimeout(() => {
        this.showSupplierDropdown = false;
      }, 150);
    },
    
    filterInvoicesBySupplier() {
      if (!this.selectedSupplier) {
        this.filteredInvoices = [...this.pendingInvoices];
      } else {
        this.filteredInvoices = this.pendingInvoices.filter(
          invoice => invoice.partner_id == this.selectedSupplier.id
        );
      }
      this.updatePaymentFormAmount();
    },
    
    // ===== MANEJO DE FACTURAS =====
    updatePaymentAmount(invoice) {
      if (invoice.selected) {
        invoice.paymentAmount = invoice.balance;
      } else {
        invoice.paymentAmount = 0;
      }
      this.updatePaymentFormAmount();
    },
    
    validatePaymentAmount(invoice) {
      const amount = parseFloat(invoice.paymentAmount);
      const balance = parseFloat(invoice.balance);
      
      if (amount > balance) {
        invoice.paymentAmount = balance;
        // Solo mostrar alerta si no estamos en el modal
        if (!document.getElementById('paymentModal').classList.contains('show')) {
          this.showWarning(`El monto no puede ser mayor al saldo ($${this.formatCurrency(balance)})`);
        }
      }
      if (amount < 0) {
        invoice.paymentAmount = 0;
      }
      this.updatePaymentFormAmount();
    },
    
    updatePaymentFormAmount() {
      this.paymentForm.amount = this.totalPaymentAmount;
    },
    
    clearSelection() {
      this.filteredInvoices.forEach(invoice => {
        invoice.selected = false;
        invoice.paymentAmount = 0;
      });
      this.updatePaymentFormAmount();
    },
    
    selectAllInvoices() {
      this.filteredInvoices.forEach(invoice => {
        invoice.selected = true;
        invoice.paymentAmount = invoice.balance;
      });
      this.updatePaymentFormAmount();
    },
    
    // ===== MODAL =====
    openPaymentModal() {
      if (this.selectedInvoicesCount === 0) {
        this.showModalWarning('Debe seleccionar al menos una factura para pagar');
        return;
      }
      
      this.clearFormErrors();
      this.clearModalMessage();
      this.updatePaymentFormAmount();
      
      // Limpiar el archivo previo
      this.paymentForm.document = null;
      this.paymentForm.documentName = '';
      this.paymentForm.documentPreview = null;
      if (this.$refs.documentFile) {
        this.$refs.documentFile.value = '';
      }
      
      // Abrir modal usando Bootstrap
      const modal = new bootstrap.Modal(document.getElementById('paymentModal'));
      modal.show();
    },
    
    // ===== MANEJO DE ARCHIVOS =====
    handleFileChange(event) {
      const file = event.target.files[0];
      if (!file) {
        this.paymentForm.document = null;
        this.paymentForm.documentName = '';
        this.paymentForm.documentPreview = null;
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
      
      this.paymentForm.document = file;
      this.paymentForm.documentName = file.name;
      
      // Crear preview para imágenes
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.paymentForm.documentPreview = e.target.result;
        };
        reader.readAsDataURL(file);
      } else {
        this.paymentForm.documentPreview = 'document';
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
      
      if (!this.paymentForm.date) {
        this.formErrors.date = 'La fecha es requerida';
        isValid = false;
      }
      
      if (!this.paymentForm.method) {
        this.formErrors.method = 'El método de pago es requerido';
        isValid = false;
      }
      
      if (this.totalPaymentAmount <= 0) {
        this.formErrors.amount = 'El monto debe ser mayor a cero';
        isValid = false;
      }
      
      // Validar que la fecha no sea futura
      const paymentDate = new Date(this.paymentForm.date);
      const today = new Date();
      if (paymentDate > today) {
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
    
    // ===== GUARDAR PAGO =====
    async savePayment() {
      if (!this.validateForm()) {
        this.showModalError('Por favor, corrija los errores en el formulario');
        return;
      }
      
      // Decidir si crear o actualizar según el modo
      if (this.isEditMode) {
        await this.updatePayment();
      } else {
        await this.createPayment();
      }
    },
    
    // Crear un nuevo pago
    async createPayment() {
      try {
        this.saving = true;
        this.clearModalMessage();
        
        const selectedInvoices = this.filteredInvoices.filter(inv => inv.selected);
        
        // Preparar los datos para la nueva API REST
        const paymentData = {
          date: this.paymentForm.date,
          method: this.paymentForm.method,
          amount: parseFloat(this.paymentForm.amount),
          bank: this.paymentForm.bank || '',
          nro_account: this.paymentForm.accountNumber || '',
          nro_operation: this.paymentForm.reference || '',
          observations: this.paymentForm.observations || '',
          invoices: selectedInvoices.map(invoice => ({
            invoice_id: invoice.id,
            amount: parseFloat(invoice.paymentAmount)
          }))
        };
        
        // Debug: Log de los datos que se van a enviar
        console.log('Enviando datos al API:', paymentData);
        
        // Obtener token CSRF de manera más robusta
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value 
                         || document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
                         || '';
        
        if (!csrfToken) {
          console.error('No se encontró el token CSRF');
          this.showModalError('Error: No se pudo obtener el token de seguridad');
          return;
        }
        
        console.log('Token CSRF encontrado:', csrfToken.substring(0, 10) + '...');
        
        // Realizar petición a la nueva API
        const response = await fetch('/api/payments/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
          },
          body: JSON.stringify(paymentData)
        });
        
        const result = await response.json();
        
        // Debug: Log de la respuesta del servidor
        console.log('Respuesta del API:', { status: response.status, result });
        
        if (response.ok) {
          this.showModalSuccess('¡Pago registrado correctamente!');
          
          // Actualizar las facturas localmente con los nuevos datos
          this.updateInvoicesAfterPayment(selectedInvoices, result.payment);
          
          // Cerrar modal después de un momento
          setTimeout(() => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
            modal.hide();
            
            // Resetear formulario y selección
            this.resetPaymentForm();
            this.clearSelection();
          }, 1500);
        } else {
          // Manejar errores de validación de la API
          console.error('Error del API:', result);
          if (result.errors) {
            this.formErrors = result.errors;
            this.showModalError('Por favor, corrija los errores indicados en el formulario');
          } else {
            const errorMessage = result.error || result.message || 'Error al procesar el pago';
            this.showModalError(`Error: ${errorMessage}`);
          }
        }
        
      } catch (error) {
        console.error('Error al guardar pago:', error);
        this.showModalError('Error de conexión. Intente nuevamente.');
      } finally {
        this.saving = false;
      }
    },
    
    // Actualizar facturas después del pago exitoso
    updateInvoicesAfterPayment(selectedInvoices, paymentData) {
      selectedInvoices.forEach(invoice => {
        const paidAmount = parseFloat(invoice.paymentAmount);
        
        // Actualizar el monto pagado y calcular nuevo balance
        invoice.paid_amount = (parseFloat(invoice.paid_amount) || 0) + paidAmount;
        invoice.balance = parseFloat(invoice.total_amount) - invoice.paid_amount;
        
        // Resetear el monto de pago y deseleccionar
        invoice.paymentAmount = 0;
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
        pending_invoices: {
          count: pendingInvoices.length,
          total_amount: pendingInvoices.reduce((sum, inv) => sum + parseFloat(inv.balance), 0)
        },
        overdue_payments: {
          total_amount: overdueInvoices.reduce((sum, inv) => sum + parseFloat(inv.balance), 0)
        },
        upcoming_due_invoices: {
          total_amount: upcomingDueInvoices.reduce((sum, inv) => sum + parseFloat(inv.balance), 0)
        }
      };
    },
    
    // ===== GESTIÓN DE ELIMINACIÓN DE PAGOS =====
    
    // Eliminar un pago individual
    async deletePayment(paymentId) {
      if (!confirm('¿Está seguro de que desea eliminar este pago? Esta acción no se puede deshacer.')) {
        return;
      }
      
      try {
        const response = await fetch(`/api/payments/${paymentId}/`, {
          method: 'DELETE',
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          }
        });
        
        const result = await response.json();
        
        if (response.ok) {
          this.showSuccess('Pago eliminado correctamente');
          // Recargar datos para reflejar los cambios
          await this.loadPaymentContextData();
        } else {
          this.showError(result.message || 'Error al eliminar el pago');
        }
        
      } catch (error) {
        console.error('Error al eliminar pago:', error);
        this.showError('Error de conexión al eliminar el pago');
      }
    },
    
    // Eliminar múltiples pagos (bulk delete)
    async deleteMultiplePayments(paymentIds) {
      if (!paymentIds || paymentIds.length === 0) {
        this.showWarning('No hay pagos seleccionados para eliminar');
        return;
      }
      
      if (!confirm(`¿Está seguro de que desea eliminar ${paymentIds.length} pago(s)? Esta acción no se puede deshacer.`)) {
        return;
      }
      
      try {
        const response = await fetch('/api/payments/delete/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          },
          body: JSON.stringify({
            payment_ids: paymentIds
          })
        });
        
        const result = await response.json();
        
        if (response.ok) {
          this.showSuccess(`${result.deleted_count} pago(s) eliminado(s) correctamente`);
          // Recargar datos para reflejar los cambios
          await this.loadPaymentContextData();
        } else {
          this.showError(result.message || 'Error al eliminar los pagos');
        }
        
      } catch (error) {
        console.error('Error al eliminar pagos múltiples:', error);
        this.showError('Error de conexión al eliminar los pagos');
      }
    },
    
    // ===== GESTIÓN DE EDICIÓN DE PAGOS =====
    
    // Cargar un pago existente para edición
    async loadPaymentForEdit(paymentId) {
      try {
        const response = await fetch(`/api/payments/${paymentId}/`, {
          method: 'GET',
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          }
        });
        
        if (response.ok) {
          const payment = await response.json();
          
          // Cargar datos del pago en el formulario
          this.paymentForm = {
            id: payment.id,
            date: payment.date,
            method: payment.method,
            amount: payment.amount,
            reference: payment.reference || '',
            bank: payment.bank || '',
            accountNumber: payment.account_number || '',
            observations: payment.observations || '',
            document: null,
            documentName: '',
            documentPreview: null
          };
          
          // Marcar que estamos en modo edición
          this.isEditMode = true;
          this.editingPaymentId = paymentId;
          
          // Seleccionar las facturas relacionadas con este pago
          if (payment.payment_details) {
            payment.payment_details.forEach(detail => {
              const invoice = this.pendingInvoices.find(inv => inv.id === detail.invoice_id);
              if (invoice) {
                invoice.selected = true;
                invoice.paymentAmount = detail.amount;
              }
            });
          }
          
          this.updatePaymentFormAmount();
          
          // Abrir el modal
          const modal = new bootstrap.Modal(document.getElementById('paymentModal'));
          modal.show();
          
        } else {
          this.showError('No se pudo cargar el pago para edición');
        }
        
      } catch (error) {
        console.error('Error al cargar pago para edición:', error);
        this.showError('Error de conexión al cargar el pago');
      }
    },
    
    // Actualizar un pago existente
    async updatePayment() {
      if (!this.validateForm()) {
        this.showModalError('Por favor, corrija los errores en el formulario');
        return;
      }
      
      try {
        this.saving = true;
        this.clearModalMessage();
        
        const selectedInvoices = this.filteredInvoices.filter(inv => inv.selected);
        
        const paymentData = {
          date: this.paymentForm.date,
          method: this.paymentForm.method,
          amount: parseFloat(this.paymentForm.amount),
          bank: this.paymentForm.bank || '',
          nro_account: this.paymentForm.accountNumber || '',
          nro_operation: this.paymentForm.reference || '',
          observations: this.paymentForm.observations || '',
          invoices: selectedInvoices.map(invoice => ({
            invoice_id: invoice.id,
            amount: parseFloat(invoice.paymentAmount)
          }))
        };
        
        const response = await fetch(`/api/payments/${this.editingPaymentId}/`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          },
          body: JSON.stringify(paymentData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
          this.showModalSuccess('¡Pago actualizado correctamente!');
          
          // Recargar datos para reflejar cambios
          await this.loadPaymentContextData();
          
          setTimeout(() => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
            modal.hide();
            this.exitEditMode();
          }, 1500);
          
        } else {
          if (result.errors) {
            this.formErrors = result.errors;
            this.showModalError('Por favor, corrija los errores indicados');
          } else {
            this.showModalError(result.message || 'Error al actualizar el pago');
          }
        }
        
      } catch (error) {
        console.error('Error al actualizar pago:', error);
        this.showModalError('Error de conexión al actualizar el pago');
      } finally {
        this.saving = false;
      }
    },
    
    // Salir del modo edición
    exitEditMode() {
      this.isEditMode = false;
      this.editingPaymentId = null;
      this.resetPaymentForm();
      this.clearSelection();
    },
    
    // Resetear el formulario de pago
    resetPaymentForm() {
      this.paymentForm = {
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
    
    // ===== UTILIDADES =====
    goBack() {
      window.location.href = '/pagos/';
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
    
    // Verificar si se debe cargar un pago para edición desde URL
    checkForEditMode() {
      const urlParams = new URLSearchParams(window.location.search);
      const editPaymentId = urlParams.get('edit');
      
      if (editPaymentId) {
        // Cargar el pago para edición después de que se carguen los datos de contexto
        setTimeout(() => {
          this.loadPaymentForEdit(editPaymentId);
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
      // Sistema de notificaciones mejorado
      this.showNotification(message, 'error');
    },
    
    showSuccess(message) {
      this.showNotification(message, 'success');
    },
    
    showWarning(message) {
      this.showNotification(message, 'warning');
    },
    
    showNotification(message, type) {
      // Por ahora usamos alert, pero aquí podrías integrar un sistema de notificaciones más elegante
      const icons = {
        error: '❌',
        success: '✅',
        warning: '⚠️'
      };
      
      alert(`${icons[type]} ${message}`);
    }
  }
}).mount('#paymentApp');
