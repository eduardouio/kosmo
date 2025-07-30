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
      currentTime: ''
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
    this.loadPaymentContextData();
  },
  
  methods: {
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
      
      try {
        this.saving = true;
        this.clearModalMessage();
        
        const selectedInvoices = this.filteredInvoices.filter(inv => inv.selected);
        const invoicePayments = {};
        
        selectedInvoices.forEach(invoice => {
          invoicePayments[invoice.id] = parseFloat(invoice.paymentAmount);
        });
        
        const formData = new FormData();
        formData.append('date', this.paymentForm.date);
        formData.append('method', this.paymentForm.method);
        formData.append('amount', this.paymentForm.amount);
        formData.append('bank', this.paymentForm.bank);
        formData.append('nro_account', this.paymentForm.accountNumber);
        formData.append('nro_operation', this.paymentForm.reference);
        formData.append('observations', this.paymentForm.observations);
        formData.append('invoice_payments', JSON.stringify(invoicePayments));
        
        // Agregar el archivo si existe
        if (this.paymentForm.document) {
          formData.append('document', this.paymentForm.document);
        }
        
        const response = await fetch(window.location.href, {
          method: 'POST',
          body: formData,
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          }
        });
        
        if (response.ok) {
          this.showModalSuccess('¡Pago registrado correctamente!');
          
          // Cerrar modal después de un momento
          setTimeout(() => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
            modal.hide();
            
            // Redirigir después de cerrar el modal
            setTimeout(() => {
              window.location.href = '/pagos/';
            }, 500);
          }, 1500);
        } else {
          const errorData = await response.text();
          throw new Error('Error en la respuesta del servidor: ' + errorData);
        }
        
      } catch (error) {
        this.showModalError('Error al guardar el pago: ' + error.message);
      } finally {
        this.saving = false;
      }
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
