from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import Usuario, Mensaje


class UsuarioCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ('email', 'nombre', 'phone_number')  

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.rol = 'cliente'
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico')  
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'phone_number']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa tu nombre'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+57 123 456 7890'
            }),
        }
        labels = {
            'nombre': 'Nombre',
            'email': 'Correo Electrónico',
            'phone_number': 'Teléfono'
        }

class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ["nombre", "correo", "asunto", "mensaje"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tu nombre"}),
            "correo": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Tu correo"}),
            "asunto": forms.TextInput(attrs={"class": "form-control", "placeholder": "Asunto"}),
            "mensaje": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Escribe tu mensaje"}),
        }