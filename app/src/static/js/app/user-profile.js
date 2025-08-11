Vue.createApp({
  delimiters: ['${', '}'],
  data() {
    // Tomar el JSON inicial para hidratar ambos estados
    const jsonEl = document.getElementById('user-profile-json');
    const initialProfile = jsonEl && jsonEl.textContent ? JSON.parse(jsonEl.textContent) : {};
    return {
      // Reactive state for user profile
      userProfile: initialProfile,
      // Reactive state for password change
      passwordForm: {
        current_password: '',
        new_password: '',
        confirm_password: ''
      },
      // Formulario de licencia (binding de modal Licencia)
      licenseForm: {
        license_key: (initialProfile.license && initialProfile.license.license_key) || '',
        enterprise: (initialProfile.license && initialProfile.license.enterprise) || '',
        url_server: (initialProfile.license && initialProfile.license.url_server) || ''
      },
      // Loading states
      loading: {
        profile: false,
        password: false,
        license: false
      },
      // Alerts for profile, password, and license
      alerts: {
        profile: {
          show: false,
          type: 'success',
          message: '',
          icon: 'fa-check-circle'
        },
        password: {
          show: false,
          type: 'success',
          message: '',
          icon: 'fa-check-circle'
        },
        license: {
          show: false,
          type: 'success',
          message: '',
          icon: 'fa-check-circle'
        }
      },
      // Bootstrap modal instances
      editProfileModal: null,
      changePasswordModal: null,
      licenseModal: null
    };
  },
  computed: {
    isValidProfile() {
      return this.userProfile.email && this.userProfile.email.length > 0;
    },
    isValidPassword() {
      return (
        this.passwordForm.current_password &&
        this.passwordForm.new_password &&
        this.passwordForm.confirm_password &&
        this.passwordForm.new_password === this.passwordForm.confirm_password &&
        this.passwordForm.new_password.length >= 8
      );
    },
    passwordMismatch() {
      return (
        this.passwordForm.new_password !== this.passwordForm.confirm_password &&
        this.passwordForm.confirm_password.length > 0
      );
    }
  },
  watch: {
    // Mantener sincronizado el formulario de licencia si cambia la licencia en el perfil
    'userProfile.license': {
      handler(newVal) {
        this.syncLicenseForm(newVal);
      },
      deep: true
    }
  },
  mounted() {
    this.initializeProfile();
    // Sincronizar formulario de licencia al iniciar
    this.syncLicenseForm(this.userProfile && this.userProfile.license);
  },
  methods: {
    // Initialize profile data from DOM inputs
    initializeProfile() {
      // Prefer JSON embedded by Django via json_script
      try {
        const jsonEl = document.getElementById('user-profile-json');
        if (jsonEl && jsonEl.textContent) {
          const data = JSON.parse(jsonEl.textContent);
          const sanitize = (val) => {
            if (val === undefined || val === null) return '';
            const s = String(val).trim();
            return (s === 'None' || s === 'null' || s === 'undefined') ? '' : s;
          };
          this.userProfile.first_name = sanitize(data.first_name);
          this.userProfile.last_name = sanitize(data.last_name);
          this.userProfile.email = sanitize(data.email);
          this.userProfile.phone = sanitize(data.phone);
          this.userProfile.notes = sanitize(data.notes);
          // Do not set picture from URL; keep it null for uploads only
          this.userProfile.picture = null;
          return; // Done
        }
      } catch (e) {
        console.warn('No se pudo parsear user_profile_json, se usará fallback del DOM.', e);
      }

      const sanitize = (val) => {
        if (val === undefined || val === null) return '';
        const s = String(val).trim();
        return (s === 'None' || s === 'null' || s === 'undefined') ? '' : s;
      };

      // Get values from form inputs
      const firstNameInput = document.querySelector('input[name="first_name"]');
      const lastNameInput = document.querySelector('input[name="last_name"]');
      const emailInput = document.querySelector('input[name="email"]');
      const phoneInput = document.querySelector('input[name="phone"]');
      const notesInput = document.querySelector('textarea[name="notes"]');

      if (firstNameInput) this.userProfile.first_name = sanitize(firstNameInput.value);
      if (lastNameInput) this.userProfile.last_name = sanitize(lastNameInput.value);
      if (emailInput) this.userProfile.email = sanitize(emailInput.value);
      if (phoneInput) this.userProfile.phone = sanitize(phoneInput.value);
      if (notesInput) this.userProfile.notes = sanitize(notesInput.value);
    },

    // Get CSRF token from DOM
    getCsrfToken() {
      const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
      if (csrfInput) {
        return csrfInput.value;
      }
      
      // Fallback to cookie method
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, 'csrftoken='.length) === 'csrftoken=') {
            cookieValue = decodeURIComponent(cookie.substring('csrftoken='.length));
            break;
          }
        }
      }
      return cookieValue || '';
    },

    // Show alert for profile or password
    showAlert(type, message, alertType = 'success') {
      const icons = {
        success: 'fa-check-circle',
        danger: 'fa-exclamation-circle'
      };
      
      this.alerts[type].show = true;
      this.alerts[type].type = alertType;
      this.alerts[type].message = message;
      this.alerts[type].icon = icons[alertType] || 'fa-info-circle';
      
      // Auto-hide after 5 seconds
      setTimeout(() => {
        this.alerts[type].show = false;
      }, 5000);
    },

    // Show error alert
    showError(type, message) {
      this.showAlert(type, message, 'danger');
    },

    // Show success alert
    showSuccess(type, message) {
      this.showAlert(type, message, 'success');
    },

    // Update profile
    async updateProfile(event) {
      if (!this.isValidProfile) {
        this.showError('profile', 'Por favor, completa todos los campos requeridos.');
        return;
      }

      this.loading.profile = true;
      this.alerts.profile.show = false;

      try {
        // Get the form element from the event or find it in DOM
        const formEl = event.target;
        const formData = new FormData(formEl);
        
        // Add action identifier
        formData.set('action', 'update_profile');
        
        // Add picture if selected
        if (this.userProfile.picture) {
          formData.set('picture', this.userProfile.picture);
        }

        console.log('Updating profile with data:', {
          first_name: formData.get('first_name'),
          last_name: formData.get('last_name'),
          email: formData.get('email'),
          phone: formData.get('phone'),
          has_picture: !!this.userProfile.picture
        });

        const response = await fetch('/api/users/update/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': this.getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
          },
          credentials: 'same-origin',
          body: formData
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || data.error || 'Error al actualizar el perfil');
        }

        this.showSuccess('profile', 'Perfil actualizado correctamente');
        
        // Close modal and reload page after success
        setTimeout(() => {
          if (this.editProfileModal) {
            this.editProfileModal.hide();
          }
          window.location.reload();
        }, 1500);

      } catch (error) {
        console.error('Error updating profile:', error);
        this.showError('profile', error.message);
      } finally {
        this.loading.profile = false;
      }
    },

    // Change password
    async changePassword() {
      if (!this.isValidPassword) {
        this.showError('password', 'Por favor, completa todos los campos correctamente.');
        return;
      }

      this.loading.password = true;
      this.alerts.password.show = false;

      try {
        const payload = {
          action: 'change_password',
          current_password: this.passwordForm.current_password,
          new_password: this.passwordForm.new_password,
          confirm_password: this.passwordForm.confirm_password
        };

        console.log('Changing password...');

        const response = await fetch('/api/users/update/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
          },
          credentials: 'same-origin',
          body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || data.error || 'Error al actualizar la contraseña');
        }

        this.showSuccess('password', 'Contraseña actualizada correctamente');
        this.resetPasswordForm();
        
        // Close modal after success
        setTimeout(() => {
          if (this.changePasswordModal) {
            this.changePasswordModal.hide();
          }
        }, 2000);

      } catch (error) {
        console.error('Error changing password:', error);
        this.showError('password', error.message);
      } finally {
        this.loading.password = false;
      }
    },

    // Sincroniza el formulario del modal de licencia con el perfil
    syncLicenseForm(license) {
      if (!license) {
        this.licenseForm.license_key = '';
        this.licenseForm.enterprise = '';
        this.licenseForm.url_server = '';
        return;
      }
      this.licenseForm.license_key = license.license_key || '';
      this.licenseForm.enterprise = license.enterprise || '';
      this.licenseForm.url_server = license.url_server || '';
    },
    
    // Actualiza la licencia
    async updateLicense() {
      this.loading.license = true;
      
      try {
        const payload = {
          action: 'update_license',
          license_key: this.licenseForm.license_key,
          enterprise: this.licenseForm.enterprise,
          url_server: this.licenseForm.url_server
        };

        const response = await fetch('/api/users/license/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
          },
          credentials: 'same-origin',
          body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || data.error || 'Error al actualizar la licencia');
        }

        this.showSuccess('license', 'Licencia actualizada correctamente');
        
        // Actualizar el perfil con la nueva licencia
        if (data.license) {
          this.userProfile.has_license = true;
          this.userProfile.license = data.license;
        }
        
        // Cerrar modal después de éxito
        setTimeout(() => {
          if (this.licenseModal) {
            this.licenseModal.hide();
          }
          // Recargar página para mostrar nueva licencia
          window.location.reload();
        }, 2000);

      } catch (error) {
        console.error('Error updating license:', error);
        this.showError('license', error.message);
      } finally {
        this.loading.license = false;
      }
    },

    // Handle file input change
    handleFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
          this.showError('profile', 'Por favor, selecciona solo archivos de imagen.');
          event.target.value = '';
          return;
        }

        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
          this.showError('profile', 'El archivo es demasiado grande. Máximo 5MB.');
          event.target.value = '';
          return;
        }

        this.userProfile.picture = file;
        this.showSuccess('profile', `Archivo "${file.name}" seleccionado correctamente`);
      }
    },

    // Reset profile form
    resetProfileForm() {
      this.initializeProfile();
      this.userProfile.picture = null;
      
      // Clear file input
      const fileInput = document.querySelector('input[name="picture"]');
      if (fileInput) fileInput.value = '';
      
      this.alerts.profile.show = false;
    },

    // Reset password form
    resetPasswordForm() {
      this.passwordForm.current_password = '';
      this.passwordForm.new_password = '';
      this.passwordForm.confirm_password = '';
      this.alerts.password.show = false;
    }
  }
}).mount('#userProfileApp');