Vue.createApp({
  delimiters: ['${', '}'],
  data() {
    return {
      // Reactive state for user profile
      userProfile: JSON.parse(document.getElementById('user-profile-json').textContent || '{}'),
      // Reactive state for password change
      passwordForm: {
        current_password: '',
        new_password: '',
        confirm_password: ''
      },
  // La licencia se maneja directamente desde userProfile.license
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
    // No se requiere sincronización adicional; se trabaja directo con userProfile
  },
  mounted() {
    this.initializeProfile();
  },
  methods: {
    // Initialize profile data from DOM inputs
    initializeProfile() {
      // Usar directamente el JSON embebido (ya asignado en data)
      const sanitize = (val) => {
        if (val === undefined || val === null) return '';
        const s = String(val).trim();
        return (s === 'None' || s === 'null' || s === 'undefined') ? '' : s;
      };

      if (this.userProfile) {
        this.userProfile.first_name = sanitize(this.userProfile.first_name);
        this.userProfile.last_name = sanitize(this.userProfile.last_name);
        this.userProfile.email = sanitize(this.userProfile.email);
        this.userProfile.phone = sanitize(this.userProfile.phone);
        this.userProfile.notes = sanitize(this.userProfile.notes);
        // La imagen para subir se gestiona como archivo, no desde URL
        this.userProfile.picture = null;
        // Asegurar objeto de licencia para bindings del formulario
        if (!this.userProfile.license) {
          this.userProfile.license = {
            license_key: '',
            enterprise: '',
            url_server: ''
          };
        }
      }
    },


    getCsrfToken() {
      return csrf_token;
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
          credentials: 'include',
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
          credentials: 'include',
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

    // Actualiza la licencia
    async updateLicense() {
      this.loading.license = true;
      
      try {
        const lic = (this.userProfile && this.userProfile.license) || {};
        const payload = {
          action: 'update_license',
          license_key: lic.license_key || '',
          enterprise: lic.enterprise || '',
          url_server: lic.url_server || ''
        };

  const response = await fetch('/api/users/update/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
          },
          credentials: 'include',
          body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || data.error || 'Error al actualizar la licencia');
        }

        this.showSuccess('license', 'Licencia actualizada correctamente');
        
        // Actualizar el perfil con la nueva licencia directamente
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