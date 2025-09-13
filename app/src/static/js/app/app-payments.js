const { createApp } = Vue;

createApp({
  delimiters: ['${', '}'],
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
        document: null,
        documentName: '',
  documentPreview: null,
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
  document: '',
  bank: '',
  reference: ''
      },
      
      currentDate: '',
      currentTime: '',
      isEditMode: false
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
    
    // Fallback: Definir métodos de pago por defecto si no se cargan desde el API
    this.setDefaultPaymentMethods();
  },
  
  methods: {
    // ===== CONFIGURACIÓN INICIAL =====
    setDefaultPaymentMethods() {
      // Métodos de pago por defecto - mismo formato que el API
      if (!this.paymentMethods || this.paymentMethods.length === 0) {
        this.paymentMethods = [
          {'value': 'TRANSF', 'label': 'Transferencia Bancaria'},
          {'value': 'EFECTIVO', 'label': 'Efectivo'},
          {'value': 'CHEQUE', 'label': 'Cheque'},
          {'value': 'TC', 'label': 'Tarjeta de Crédito'},
          {'value': 'TD', 'label': 'Tarjeta de Débito'},
          {'value': 'NC', 'label': 'Nota de Crédito'},
          {'value': 'OTRO', 'label': 'Otro'}
        ];
        console.log('Usando métodos de pago por defecto');
      }
    },

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
          
          // Filtrar facturas pendientes (solo con saldo > 0) y mapear propiedades adicionales
          this.pendingInvoices = data.pending_invoices
            .filter(invoice => parseFloat(invoice.balance) > 0.01) // Filtrar saldo > 0
            .map(invoice => ({
              ...invoice,
              selected: false,
              paymentAmount: invoice.balance
            }));
            
          this.refreshFilteredInvoices();
          this.paymentMethods = data.payment_methods || [];
          this.popularBanks = data.popular_banks;
          this.statistics = data.statistics;
          this.paymentForm.date = data.current_date;
          
          // Debug: Verificar que los métodos de pago se cargaron correctamente
          console.log('Métodos de pago cargados:', this.paymentMethods);
          
          if (this.paymentMethods.length === 0) {
            console.warn('No se cargaron métodos de pago desde el API');
            this.setDefaultPaymentMethods();
          }
        } else {
          this.showError('Error al cargar los datos: ' + data.error);
          // Si hay error, usar métodos por defecto
          this.setDefaultPaymentMethods();
        }
      } catch (error) {
        this.showError('Error de conexión: ' + error.message);
        // Si hay error de conexión, usar métodos por defecto
        this.setDefaultPaymentMethods();
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
      this.refreshFilteredInvoices();
      this.updatePaymentFormAmount();
    },
    
    hideSupplierDropdown() {
      // Delay para permitir que el click en el dropdown se registre
      setTimeout(() => {
        this.showSupplierDropdown = false;
      }, 150);
    },
    
    filterInvoicesBySupplier() {
      this.refreshFilteredInvoices();
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
      
      // Verificar que los métodos de pago estén cargados
      if (!this.paymentMethods || this.paymentMethods.length === 0) {
        console.warn('Métodos de pago no disponibles, aplicando fallback...');
        this.setDefaultPaymentMethods();
      }
      
      this.clearFormErrors();
      this.clearModalMessage();
      this.updatePaymentFormAmount();
      
      // Limpiar el archivo previo
      this.paymentForm.document = null;
      this.paymentForm.documentName = '';
      this.paymentForm.documentPreview = null;
  this.paymentForm.notes = '';
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
      
      // Reglas adicionales según el método
      const methodRequiresOperation = ['TRANSF', 'TC', 'TD'].includes(this.paymentForm.method);
      if (methodRequiresOperation) {
        if (!this.paymentForm.bank || !this.paymentForm.bank.trim()) {
          this.formErrors.bank = 'El banco es requerido para este método de pago';
          isValid = false;
        }
        if (!this.paymentForm.reference || !this.paymentForm.reference.trim()) {
          this.formErrors.reference = 'El número de operación es requerido para este método de pago';
          isValid = false;
        }
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
  document: '',
  bank: '',
  reference: ''
      };
    },
    
    // ===== GUARDAR PAGO =====
    async savePayment() {
      if (!this.validateForm()) {
        this.showModalError('Por favor, corrija los errores en el formulario');
        return;
      }
      
      // Crear nuevo pago
      await this.createPayment();
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
          notes: this.paymentForm.notes || '',
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
        
        // Preparar la petición
        let requestOptions = {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken
          }
        };
        
        // Si hay archivo adjunto, usar FormData
        if (this.paymentForm.document) {
          const formData = new FormData();
          
          // Agregar todos los campos del pago
          Object.keys(paymentData).forEach(key => {
            if (key === 'invoices') {
              formData.append(key, JSON.stringify(paymentData[key]));
            } else {
              formData.append(key, paymentData[key]);
            }
          });
          
          // Agregar el archivo
          formData.append('document', this.paymentForm.document);
          
          requestOptions.body = formData;
          // No establecer Content-Type para FormData, el navegador lo hará automáticamente
        } else {
          // Sin archivo, usar JSON tradicional
          requestOptions.headers['Content-Type'] = 'application/json';
          requestOptions.body = JSON.stringify(paymentData);
        }
        
        // Realizar petición a la nueva API
        const response = await fetch('/api/payments/', requestOptions);
        
        const result = await response.json();
        
        // Debug: Log de la respuesta del servidor
        console.log('Respuesta del API:', { status: response.status, result });
        
        if (response.ok) {
          // Contar cuántas facturas se pagaron completamente
          const selectedInvoices = this.filteredInvoices.filter(inv => inv.selected);
          const fullyPaidCount = selectedInvoices.filter(invoice => {
            const paidAmount = parseFloat(invoice.paymentAmount);
            const balance = parseFloat(invoice.balance);
            return paidAmount >= balance;
          }).length;
          
          // Mensaje personalizado según el resultado
          let successMessage = '¡Pago registrado correctamente!';
          if (fullyPaidCount > 0) {
            successMessage += ` ${fullyPaidCount} factura${fullyPaidCount > 1 ? 's' : ''} pagada${fullyPaidCount > 1 ? 's' : ''} completamente y ${fullyPaidCount > 1 ? 'removidas' : 'removida'} de la lista.`;
          }
          
          this.showModalSuccess(successMessage);
          
          // Actualizar las facturas localmente con los nuevos datos
          this.updateInvoicesAfterPayment(selectedInvoices, result.payment);
          
          // Debug: Verificar datos del pago antes de descargar PDF
          console.log('Datos del pago creado:', result.payment);
          console.log('ID del pago para PDF:', result.payment?.id);
          
          // Descargar automáticamente el PDF del pago
          if (result.payment && result.payment.id) {
            console.log('Iniciando descarga automática del PDF...');
            // Delay pequeño para asegurar que el pago se haya guardado completamente
            setTimeout(() => {
              this.downloadPaymentPDF(result.payment.id);
            }, 500);
          } else {
            console.warn('No se pudo obtener el ID del pago para descargar el PDF:', result);
            this.showWarning('El pago se creó correctamente, pero no se pudo obtener el ID para descargar el PDF automáticamente.');
          }
          
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

    // Reinicia el formulario de pago a sus valores por defecto
    resetPaymentForm() {
      this.paymentForm = {
        date: this.currentDate,
        method: '',
        reference: '',
        amount: 0,
        bank: this.bankConfig?.bank_name || '',
        accountNumber: this.bankConfig?.account_number || '',
        document: null,
        documentName: '',
        documentPreview: null,
        notes: ''
      };
      this.clearFormErrors();
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
      
      // Eliminar facturas con saldo cero de ambas listas
      this.removeZeroBalanceInvoices();
      
      // Recalcular estadísticas
      this.updateStatistics();
      
      // Refiltrar la lista visible
      this.refreshFilteredInvoices();
    },
    
    // Eliminar facturas con saldo cero o negativo
    removeZeroBalanceInvoices() {
      // Eliminar de la lista principal de facturas pendientes
      this.pendingInvoices = this.pendingInvoices.filter(invoice => {
        const balance = parseFloat(invoice.balance) || 0;
        return balance > 0.01; // Usar 0.01 para evitar problemas de precisión decimal
      });
    },
    
    // Refrescar la lista filtrada después de cambios
    refreshFilteredInvoices() {
      if (!this.selectedSupplier) {
        // Si no hay proveedor seleccionado, mostrar todas las facturas pendientes
        this.filteredInvoices = [...this.pendingInvoices];
      } else {
        // Si hay proveedor seleccionado, filtrar por proveedor
        this.filteredInvoices = this.pendingInvoices.filter(
          invoice => invoice.partner_id == this.selectedSupplier.id
        );
      }
    },
    
    // Método para actualizar una factura específica (útil para actualizaciones en tiempo real)
    updateInvoiceById(invoiceId, updates) {
      // Actualizar en la lista principal
      const invoiceIndex = this.pendingInvoices.findIndex(inv => inv.id === invoiceId);
      if (invoiceIndex !== -1) {
        this.pendingInvoices[invoiceIndex] = { ...this.pendingInvoices[invoiceIndex], ...updates };
        
        // Si el balance es cero o negativo, eliminar la factura
        if (parseFloat(this.pendingInvoices[invoiceIndex].balance) <= 0.01) {
          this.pendingInvoices.splice(invoiceIndex, 1);
        }
      }
      
      // Refrescar la lista filtrada
      this.refreshFilteredInvoices();
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
    
    // ===== UTILIDADES =====
    testPaymentMethods() {
      console.log('=== TESTING MÉTODOS DE PAGO ===');
      console.log('Cantidad de métodos:', this.paymentMethods.length);
      console.log('Métodos disponibles:', this.paymentMethods);
      console.log('Método seleccionado:', this.paymentForm.method);
      
      if (this.paymentMethods.length === 0) {
        console.warn('⚠️ No hay métodos de pago cargados');
        this.setDefaultPaymentMethods();
        console.log('✅ Métodos de pago por defecto aplicados');
      } else {
        console.log('✅ Métodos de pago cargados correctamente');
      }
    },

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
      const date = new Date(dateString);
      const day = date.getDate().toString().padStart(2, '0');
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const year = date.getFullYear();
      return `${day}/${month}/${year}`;
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
    },
    
    // ===== DESCARGA DE PDF =====
    
    /**
     * Descarga automáticamente el PDF del comprobante de pago
     * @param {number} paymentId - ID del pago para descargar el PDF
     */
    downloadPaymentPDF(paymentId) {
      try {
        console.log(`Iniciando descarga del PDF para el pago ID: ${paymentId}`);
        
        // Verificar que el paymentId es válido
        if (!paymentId) {
          console.error('ID de pago no válido:', paymentId);
          this.showWarning('No se pudo obtener el ID del pago para descargar el PDF.');
          return;
        }
        
        // Crear URL del PDF usando la ruta de Playwright
        const pdfUrl = `/reports/payment/${paymentId}/`;
        console.log(`URL del PDF: ${pdfUrl}`);
        
        // Método principal: Descarga directa via enlace
        const link = document.createElement('a');
        link.href = pdfUrl;
        link.download = `comprobante_pago_${paymentId}.pdf`;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        
        // Estilo invisible
        link.style.display = 'none';
        
        // Agregar al DOM
        document.body.appendChild(link);
        
        // Simular clic para iniciar descarga
        link.click();
        console.log(`Descarga del PDF iniciada para el pago ${paymentId}`);
        
        // Remover el enlace del DOM después de un momento
        setTimeout(() => {
          if (document.body.contains(link)) {
            document.body.removeChild(link);
          }
        }, 1000);
        
      } catch (error) {
        console.error('Error al descargar el PDF del pago:', error);
        this.showWarning('El pago se creó correctamente, pero hubo un problema al descargar el PDF automáticamente. Puede descargarlo manualmente desde la lista de pagos.');
        
        // Método de respaldo solo en caso de error: abrir en nueva ventana
        try {
          const pdfUrl = `/reports/payment/${paymentId}/`;
          console.log('Ejecutando método de respaldo: nueva ventana');
          window.open(pdfUrl, '_blank', 'noopener,noreferrer');
        } catch (fallbackError) {
          console.error('Error en método de respaldo:', fallbackError);
        }
      }
    },

    /**
     * Función de prueba para descargar PDF manualmente
     * @param {number} paymentId - ID del pago para descargar el PDF
     */
    testDownloadPDF(paymentId) {
      console.log('=== PRUEBA DE DESCARGA DE PDF ===');
      console.log(`ID de pago: ${paymentId}`);
      
      if (!paymentId) {
        const testId = prompt('Ingrese el ID del pago para probar la descarga:');
        if (testId) {
          this.downloadPaymentPDF(parseInt(testId));
        }
        return;
      }
      
      this.downloadPaymentPDF(paymentId);
    }
  }
}).mount('#paymentApp');
