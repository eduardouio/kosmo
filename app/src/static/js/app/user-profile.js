// Aplicación Vue.js para el perfil de usuario
(function() {
  'use strict';

  const { createApp, ref, reactive, computed, onMounted, toRaw } = Vue;

  const UserProfileApp = {
    setup() {
      // Estado reactivo
      const userProfile = reactive({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        notes: '',
        picture: null
      });

      const passwordForm = reactive({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });

      // Estados de carga y alertas
      const loading = ref({
        profile: false,
        password: false
      });

      const alerts = reactive({
        profile: {
          show: false,
          type: 'success',
          message: ''
        },
        password: {
          show: false,
          type: 'success',
          message: ''
        }
      });

      // Validaciones computadas
      const isValidProfile = computed(() => {
        return userProfile.email && userProfile.email.length > 0;
      });

      const isValidPassword = computed(() => {
        return passwordForm.current_password &&
               passwordForm.new_password &&
               passwordForm.confirm_password &&
               passwordForm.new_password === passwordForm.confirm_password &&
               passwordForm.new_password.length >= 8;
      });

      const passwordMismatch = computed(() => {
        return passwordForm.new_password !== passwordForm.confirm_password &&
               passwordForm.confirm_password.length > 0;
      });

      // Utilidades
      const getCookie = (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      };

  const getCsrfToken = () => getCookie('csrftoken') || '';

      const showAlert = (alertType, type, message, duration = 5000) => {
        alerts[alertType].show = true;
        alerts[alertType].type = type;
        alerts[alertType].message = message;
        
        setTimeout(() => {
          alerts[alertType].show = false;
        }, duration);
      };

      // Inicializar datos del perfil desde el DOM
      const initializeProfile = () => {
        const sanitize = (val) => {
          if (val === undefined || val === null) return '';
          const s = String(val).trim();
          return (s === 'None' || s === 'null' || s === 'undefined') ? '' : s;
        };
        // Obtener datos del usuario desde los inputs del DOM
        const firstNameInput = document.querySelector('input[name="first_name"]');
        const lastNameInput = document.querySelector('input[name="last_name"]');
        const emailInput = document.querySelector('input[name="email"]');
        const phoneInput = document.querySelector('input[name="phone"]');
        const notesInput = document.querySelector('textarea[name="notes"]');

        if (firstNameInput) userProfile.first_name = sanitize(firstNameInput.value);
        if (lastNameInput) userProfile.last_name = sanitize(lastNameInput.value);
        if (emailInput) userProfile.email = sanitize(emailInput.value);
        if (phoneInput) userProfile.phone = sanitize(phoneInput.value);
        if (notesInput) userProfile.notes = sanitize(notesInput.value);
      };

      // Helper para depurar FormData
      const logFormData = (fd) => {
        try {
          const entries = [];
          for (const [k, v] of fd.entries()) {
            entries.push([k, v instanceof File ? `(File) ${v.name}` : String(v)]);
          }
          console.table(entries);
        } catch (e) {
          console.debug('No se pudo listar FormData:', e);
        }
      };

      // Métodos para actualizar perfil
      const updateProfile = async (e) => {
        if (!isValidProfile.value) {
          showAlert('profile', 'danger', 'Por favor, completa todos los campos requeridos.');
          return;
        }

        loading.value.profile = true;
        alerts.profile.show = false;
        
        try {
          const formEl = e && e.target ? e.target : document.querySelector('#modalEditProfile form');
          const formData = formEl ? new FormData(formEl) : new FormData();
          // Asegurar action y campos clave
          formData.set('action', 'update_profile');

          // Agregar archivo si existe
          if (userProfile.picture) {
            formData.set('picture', userProfile.picture);
          }
          // Mostrar datos del formulario en consola
          logFormData(formData);
      const response = await fetch('/api/users/update/', {
            method: 'POST',
            headers: {
        'X-CSRFToken': getCsrfToken(),
        'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin',
            body: formData
          });

          const data = await response.json();

          if (!response.ok) {
            throw new Error(data.detail || 'Error al actualizar el perfil');
          }

          showAlert('profile', 'success', 'Perfil actualizado correctamente');
          
          // Recargar la página después de 1 segundo
          setTimeout(() => {
            window.location.reload();
          }, 1000);

        } catch (error) {
          showAlert('profile', 'danger', error.message);
        } finally {
          loading.value.profile = false;
        }
      };

      // Métodos para cambiar contraseña
      const changePassword = async () => {
        if (!isValidPassword.value) {
          showAlert('password', 'danger', 'Por favor, completa todos los campos correctamente.');
          return;
        }

        loading.value.password = true;
        alerts.password.show = false;

        try {
          const payload = {
            action: 'change_password',
            current_password: passwordForm.current_password,
            new_password: passwordForm.new_password,
            confirm_password: passwordForm.confirm_password
          };

      const response = await fetch('/api/users/update/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
        'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin',
            body: JSON.stringify(payload)
          });

          const data = await response.json();

          if (!response.ok) {
            throw new Error(data.detail || 'Error al actualizar la contraseña');
          }

          showAlert('password', 'success', 'Contraseña actualizada correctamente');
          
          // Limpiar formulario
          Object.keys(passwordForm).forEach(key => {
            passwordForm[key] = '';
          });

        } catch (error) {
          showAlert('password', 'danger', error.message);
        } finally {
          loading.value.password = false;
        }
      };

      // Manejo de archivos
      const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
          // Validar tipo de archivo
          if (!file.type.startsWith('image/')) {
            showAlert('profile', 'danger', 'Por favor, selecciona solo archivos de imagen.');
            event.target.value = '';
            return;
          }
          
          // Validar tamaño (max 5MB)
          if (file.size > 5 * 1024 * 1024) {
            showAlert('profile', 'danger', 'El archivo es demasiado grande. Máximo 5MB.');
            event.target.value = '';
            return;
          }
          
          userProfile.picture = file;
        }
      };

      // Resetear formularios
      const resetProfileForm = () => {
        initializeProfile();
        userProfile.picture = null;
        const fileInput = document.querySelector('input[name="picture"]');
        if (fileInput) fileInput.value = '';
      };

      const resetPasswordForm = () => {
        Object.keys(passwordForm).forEach(key => {
          passwordForm[key] = '';
        });
      };

      // Hook onMounted
      onMounted(() => {
        initializeProfile();
      });

      return {
        userProfile,
        passwordForm,
        loading,
        alerts,
        isValidProfile,
        isValidPassword,
        passwordMismatch,
        updateProfile,
        changePassword,
        handleFileChange,
        resetProfileForm,
        resetPasswordForm,
        initializeProfile
      };
    }
  };

  // Inicializar la aplicación Vue cuando el DOM esté listo evitando doble montaje
  document.addEventListener('DOMContentLoaded', () => {
    const mountTarget = document.body;
    if (!mountTarget.__vue_app__) {
      const app = createApp(UserProfileApp);
      // Usar delimitadores personalizados ${ }
      if (app && app.config && app.config.compilerOptions) {
        app.config.compilerOptions.delimiters = ['${', '}'];
      }
      app.mount(mountTarget);
      mountTarget.__vue_app__ = true;
    }
  });

})();
