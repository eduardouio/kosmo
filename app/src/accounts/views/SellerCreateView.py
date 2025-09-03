from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.urls import reverse_lazy
from accounts.models.CustomUserModel import CustomUserModel
from common.AdminOnlyMixin import AdminOnlyMixin


class SellerCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control form-control-sm'})
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control form-control-sm'})
    )

    class Meta:
        model = CustomUserModel
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'goal_sales', 'goal_stems', 'is_active'
        ]
        widgets = {
            'first_name': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'phone': forms.TextInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'goal_sales': forms.NumberInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'goal_stems': forms.NumberInput(
                attrs={'class': 'form-control form-control-sm'}
            ),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.roles = 'VENDEDOR'
        password = self.cleaned_data.get('password1')
        if password:
            instance.set_password(password)
        if commit:
            instance.save()
        return instance


class SellerCreateView(LoginRequiredMixin, AdminOnlyMixin, CreateView):
    model = CustomUserModel
    form_class = SellerCreateForm
    template_name = 'forms/seller_form.html'

    def get_success_url(self):
        return f"{reverse_lazy('sellers_list')}?action=created"
