from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import PerfilTutor, Mascota, FichaClinica, EventoClinico, ArchivoAdjunto


class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control w-full',
            'placeholder': 'tu@email.com',
            'autocomplete': 'off'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control w-full',
            'placeholder': 'Juan'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-control w-full',
            'placeholder': 'Pérez'
        })
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control w-full',
            'placeholder': '••••••••',
            'minlength': '6',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control w-full',
            'placeholder': '••••••••',
            'minlength': '6',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        if 'username' in self.fields:
            self.fields['username'].widget = forms.HiddenInput()
            self.fields['username'].required = False
        
        # Asegurar que los campos estén vacíos cuando no hay datos POST
        if not args and not kwargs.get('data'):
            self.fields['email'].initial = ''
            self.fields['password1'].initial = ''
            self.fields['password2'].initial = ''
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('Este correo electrónico ya está registrado.')
            if User.objects.filter(username=email).exists():
                raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if email:
            cleaned_data['username'] = email
        return cleaned_data
    
    def save(self, commit=True):
        email = self.cleaned_data['email']
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name']
        )
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control w-full',
            'placeholder': 'tu@email.com',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control w-full',
            'placeholder': '••••••••'
        })
    )


class RecuperarClaveForm(forms.Form):
    email = forms.EmailField(
        label='Correo Electrónico',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control w-full',
            'placeholder': 'tu@email.com'
        })
    )
    nueva_password = forms.CharField(
        label='Ingresa nueva contraseña',
        required=True,
        min_length=4,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control w-full',
            'placeholder': '••••',
            'minlength': '4'
        })
    )
    confirmar_password = forms.CharField(
        label='Reingresa nueva contraseña',
        required=True,
        min_length=4,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control w-full',
            'placeholder': '••••',
            'minlength': '4'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        nueva_password = cleaned_data.get('nueva_password')
        confirmar_password = cleaned_data.get('confirmar_password')
        
        if nueva_password and confirmar_password:
            if nueva_password != confirmar_password:
                raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data


class UserForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Nombre Completo',
        widget=forms.TextInput(attrs={
            'class': 'form-control w-full',
            'placeholder': 'Juan Pérez'
        })
    )
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control w-full',
            'placeholder': 'tu@email.com'
        })
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'email')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email


class PerfilTutorForm(forms.ModelForm):
    sobrenombre = forms.CharField(
        max_length=100,
        required=False,
        label='Sobrenombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control w-full',
            'placeholder': '¿Cómo prefieres que te llamemos?'
        })
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label='Teléfono',
        widget=forms.TextInput(attrs={
            'class': 'form-control w-full',
            'placeholder': '12345678',
            'pattern': '[0-9]{8}',
            'title': 'Ingresa 8 dígitos (se agregará +569 automáticamente)',
            'maxlength': '8'
        }),
        help_text='Ingresa solo los 8 dígitos. El prefijo +569 se agregará automáticamente.'
    )
    ocupacion = forms.CharField(
        max_length=100,
        required=False,
        label='Ocupación',
        widget=forms.TextInput(attrs={
            'class': 'form-control w-full',
            'placeholder': 'Ej: Profesor, Ingeniero, Estudiante, etc.'
        })
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        label='Fecha de Nacimiento',
        widget=forms.DateInput(attrs={
            'class': 'form-control w-full',
            'type': 'date'
        })
    )
    calle = forms.CharField(
        max_length=255,
        required=False,
        label='Calle',
        widget=forms.TextInput(attrs={
            'class': 'form-control w-full',
            'placeholder': 'Ej: Av. Libertador Bernardo O\'Higgins'
        })
    )
    numero = forms.CharField(
        max_length=50,
        required=False,
        label='Número',
        widget=forms.TextInput(attrs={
            'class': 'form-control w-full',
            'placeholder': 'Ej: 123'
        })
    )
    ciudad = forms.ChoiceField(
        required=False,
        label='Ciudad',
        choices=[('', 'Selecciona una ciudad')],
        widget=forms.Select(attrs={
            'class': 'form-control w-full',
            'id': 'id_ciudad'
        })
    )
    comuna = forms.CharField(
        required=False,
        label='Comuna',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control w-full',
            'id': 'id_comuna',
            'style': 'display: none;'
        })
    )
    foto_perfil = forms.ImageField(
        required=False,
        label='Foto de Perfil',
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'style': 'display: none;',
            'id': 'id_foto_perfil'
        })
    )
    
    class Meta:
        model = PerfilTutor
        fields = ('sobrenombre', 'telefono', 'ocupacion', 'fecha_nacimiento', 'calle', 'numero', 'ciudad', 'comuna', 'foto_perfil')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Definir ciudades de Chile (regiones principales)
        ciudades_chile = [
            ('', 'Selecciona una ciudad'),
            ('Arica', 'Arica'),
            ('Iquique', 'Iquique'),
            ('Antofagasta', 'Antofagasta'),
            ('Calama', 'Calama'),
            ('Copiapó', 'Copiapó'),
            ('La Serena', 'La Serena'),
            ('Coquimbo', 'Coquimbo'),
            ('Valparaíso', 'Valparaíso'),
            ('Viña del Mar', 'Viña del Mar'),
            ('Santiago', 'Santiago'),
            ('Rancagua', 'Rancagua'),
            ('Talca', 'Talca'),
            ('Chillán', 'Chillán'),
            ('Concepción', 'Concepción'),
            ('Los Ángeles', 'Los Ángeles'),
            ('Temuco', 'Temuco'),
            ('Valdivia', 'Valdivia'),
            ('Osorno', 'Osorno'),
            ('Puerto Montt', 'Puerto Montt'),
            ('Coyhaique', 'Coyhaique'),
            ('Punta Arenas', 'Punta Arenas'),
        ]
        self.fields['ciudad'].choices = ciudades_chile
        
        # Si hay una instancia con ciudad, cargar comunas
        if self.instance and self.instance.pk and self.instance.ciudad:
            ciudad_actual = self.instance.ciudad
            self.fields['ciudad'].initial = ciudad_actual
            comunas = self._get_comunas_por_ciudad(ciudad_actual)
            if comunas:
                self.fields['comuna'].choices = comunas
                self.fields['comuna'].widget.attrs['disabled'] = False
                if self.instance.comuna:
                    self.fields['comuna'].initial = self.instance.comuna
    
    def _get_comunas_por_ciudad(self, ciudad):
        """Retorna las comunas según la ciudad seleccionada"""
        comunas_por_ciudad = {
            'Arica': [
                ('', 'Selecciona una comuna'),
                ('Arica', 'Arica'),
                ('Camarones', 'Camarones'),
            ],
            'Iquique': [
                ('', 'Selecciona una comuna'),
                ('Iquique', 'Iquique'),
                ('Alto Hospicio', 'Alto Hospicio'),
                ('Pozo Almonte', 'Pozo Almonte'),
                ('Camiña', 'Camiña'),
                ('Colchane', 'Colchane'),
                ('Huara', 'Huara'),
                ('Pica', 'Pica'),
            ],
            'Antofagasta': [
                ('', 'Selecciona una comuna'),
                ('Antofagasta', 'Antofagasta'),
                ('Mejillones', 'Mejillones'),
                ('Sierra Gorda', 'Sierra Gorda'),
                ('Taltal', 'Taltal'),
            ],
            'Calama': [
                ('', 'Selecciona una comuna'),
                ('Calama', 'Calama'),
                ('Ollagüe', 'Ollagüe'),
                ('San Pedro de Atacama', 'San Pedro de Atacama'),
            ],
            'Copiapó': [
                ('', 'Selecciona una comuna'),
                ('Copiapó', 'Copiapó'),
                ('Caldera', 'Caldera'),
                ('Tierra Amarilla', 'Tierra Amarilla'),
            ],
            'La Serena': [
                ('', 'Selecciona una comuna'),
                ('La Serena', 'La Serena'),
                ('Coquimbo', 'Coquimbo'),
                ('Andacollo', 'Andacollo'),
                ('La Higuera', 'La Higuera'),
                ('Paihuano', 'Paihuano'),
                ('Vicuña', 'Vicuña'),
            ],
            'Coquimbo': [
                ('', 'Selecciona una comuna'),
                ('Coquimbo', 'Coquimbo'),
                ('La Serena', 'La Serena'),
            ],
            'Valparaíso': [
                ('', 'Selecciona una comuna'),
                ('Valparaíso', 'Valparaíso'),
                ('Casablanca', 'Casablanca'),
                ('Concón', 'Concón'),
                ('Juan Fernández', 'Juan Fernández'),
                ('Puchuncaví', 'Puchuncaví'),
                ('Quintero', 'Quintero'),
                ('Viña del Mar', 'Viña del Mar'),
            ],
            'Viña del Mar': [
                ('', 'Selecciona una comuna'),
                ('Viña del Mar', 'Viña del Mar'),
                ('Valparaíso', 'Valparaíso'),
            ],
            'Santiago': [
                ('', 'Selecciona una comuna'),
                ('Santiago', 'Santiago'),
                ('Cerrillos', 'Cerrillos'),
                ('Cerro Navia', 'Cerro Navia'),
                ('Conchalí', 'Conchalí'),
                ('El Bosque', 'El Bosque'),
                ('Estación Central', 'Estación Central'),
                ('Huechuraba', 'Huechuraba'),
                ('Independencia', 'Independencia'),
                ('La Cisterna', 'La Cisterna'),
                ('La Florida', 'La Florida'),
                ('La Granja', 'La Granja'),
                ('La Pintana', 'La Pintana'),
                ('La Reina', 'La Reina'),
                ('Las Condes', 'Las Condes'),
                ('Lo Barnechea', 'Lo Barnechea'),
                ('Lo Espejo', 'Lo Espejo'),
                ('Lo Prado', 'Lo Prado'),
                ('Macul', 'Macul'),
                ('Maipú', 'Maipú'),
                ('Ñuñoa', 'Ñuñoa'),
                ('Pedro Aguirre Cerda', 'Pedro Aguirre Cerda'),
                ('Peñalolén', 'Peñalolén'),
                ('Providencia', 'Providencia'),
                ('Pudahuel', 'Pudahuel'),
                ('Quilicura', 'Quilicura'),
                ('Quinta Normal', 'Quinta Normal'),
                ('Recoleta', 'Recoleta'),
                ('Renca', 'Renca'),
                ('San Joaquín', 'San Joaquín'),
                ('San Miguel', 'San Miguel'),
                ('San Ramón', 'San Ramón'),
                ('Vitacura', 'Vitacura'),
            ],
            'Rancagua': [
                ('', 'Selecciona una comuna'),
                ('Rancagua', 'Rancagua'),
                ('Codegua', 'Codegua'),
                ('Coinco', 'Coinco'),
                ('Coltauco', 'Coltauco'),
                ('Doñihue', 'Doñihue'),
                ('Graneros', 'Graneros'),
                ('Las Cabras', 'Las Cabras'),
                ('Machalí', 'Machalí'),
                ('Malloa', 'Malloa'),
                ('Mostazal', 'Mostazal'),
                ('Olivar', 'Olivar'),
                ('Peumo', 'Peumo'),
                ('Pichidegua', 'Pichidegua'),
                ('Quinta de Tilcoco', 'Quinta de Tilcoco'),
                ('Rengo', 'Rengo'),
                ('Requínoa', 'Requínoa'),
                ('San Vicente', 'San Vicente'),
            ],
            'Talca': [
                ('', 'Selecciona una comuna'),
                ('Talca', 'Talca'),
                ('Constitución', 'Constitución'),
                ('Curepto', 'Curepto'),
                ('Empedrado', 'Empedrado'),
                ('Maule', 'Maule'),
                ('Pelarco', 'Pelarco'),
                ('Pencahue', 'Pencahue'),
                ('Río Claro', 'Río Claro'),
                ('San Clemente', 'San Clemente'),
                ('San Rafael', 'San Rafael'),
            ],
            'Chillán': [
                ('', 'Selecciona una comuna'),
                ('Chillán', 'Chillán'),
                ('Bulnes', 'Bulnes'),
                ('Chillán Viejo', 'Chillán Viejo'),
                ('El Carmen', 'El Carmen'),
                ('Pemuco', 'Pemuco'),
                ('Pinto', 'Pinto'),
                ('Quillón', 'Quillón'),
                ('San Ignacio', 'San Ignacio'),
                ('Yungay', 'Yungay'),
            ],
            'Concepción': [
                ('', 'Selecciona una comuna'),
                ('Concepción', 'Concepción'),
                ('Coronel', 'Coronel'),
                ('Chiguayante', 'Chiguayante'),
                ('Florida', 'Florida'),
                ('Hualpén', 'Hualpén'),
                ('Hualqui', 'Hualqui'),
                ('Lota', 'Lota'),
                ('Penco', 'Penco'),
                ('San Pedro de la Paz', 'San Pedro de la Paz'),
                ('Santa Juana', 'Santa Juana'),
                ('Talcahuano', 'Talcahuano'),
                ('Tomé', 'Tomé'),
            ],
            'Los Ángeles': [
                ('', 'Selecciona una comuna'),
                ('Los Ángeles', 'Los Ángeles'),
                ('Antuco', 'Antuco'),
                ('Cabrero', 'Cabrero'),
                ('Laja', 'Laja'),
                ('Mulchén', 'Mulchén'),
                ('Nacimiento', 'Nacimiento'),
                ('Negrete', 'Negrete'),
                ('Quilaco', 'Quilaco'),
                ('Quilleco', 'Quilleco'),
                ('San Rosendo', 'San Rosendo'),
                ('Santa Bárbara', 'Santa Bárbara'),
                ('Tucapel', 'Tucapel'),
                ('Yumbel', 'Yumbel'),
            ],
            'Temuco': [
                ('', 'Selecciona una comuna'),
                ('Temuco', 'Temuco'),
                ('Carahue', 'Carahue'),
                ('Cholchol', 'Cholchol'),
                ('Cunco', 'Cunco'),
                ('Curarrehue', 'Curarrehue'),
                ('Freire', 'Freire'),
                ('Galvarino', 'Galvarino'),
                ('Gorbea', 'Gorbea'),
                ('Lautaro', 'Lautaro'),
                ('Loncoche', 'Loncoche'),
                ('Melipeuco', 'Melipeuco'),
                ('Nueva Imperial', 'Nueva Imperial'),
                ('Padre Las Casas', 'Padre Las Casas'),
                ('Perquenco', 'Perquenco'),
                ('Pitrufquén', 'Pitrufquén'),
                ('Pucón', 'Pucón'),
                ('Saavedra', 'Saavedra'),
                ('Teodoro Schmidt', 'Teodoro Schmidt'),
                ('Toltén', 'Toltén'),
                ('Vilcún', 'Vilcún'),
                ('Villarrica', 'Villarrica'),
            ],
            'Valdivia': [
                ('', 'Selecciona una comuna'),
                ('Valdivia', 'Valdivia'),
                ('Corral', 'Corral'),
                ('Lanco', 'Lanco'),
                ('Los Lagos', 'Los Lagos'),
                ('Máfil', 'Máfil'),
                ('Mariquina', 'Mariquina'),
                ('Paillaco', 'Paillaco'),
                ('Panguipulli', 'Panguipulli'),
            ],
            'Osorno': [
                ('', 'Selecciona una comuna'),
                ('Osorno', 'Osorno'),
                ('Puerto Octay', 'Puerto Octay'),
                ('Purranque', 'Purranque'),
                ('Puyehue', 'Puyehue'),
                ('Río Negro', 'Río Negro'),
                ('San Juan de la Costa', 'San Juan de la Costa'),
                ('San Pablo', 'San Pablo'),
            ],
            'Puerto Montt': [
                ('', 'Selecciona una comuna'),
                ('Puerto Montt', 'Puerto Montt'),
                ('Calbuco', 'Calbuco'),
                ('Cochamó', 'Cochamó'),
                ('Fresia', 'Fresia'),
                ('Frutillar', 'Frutillar'),
                ('Los Muermos', 'Los Muermos'),
                ('Llanquihue', 'Llanquihue'),
                ('Maullín', 'Maullín'),
                ('Puerto Varas', 'Puerto Varas'),
            ],
            'Coyhaique': [
                ('', 'Selecciona una comuna'),
                ('Coyhaique', 'Coyhaique'),
                ('Lago Verde', 'Lago Verde'),
            ],
            'Punta Arenas': [
                ('', 'Selecciona una comuna'),
                ('Punta Arenas', 'Punta Arenas'),
                ('Laguna Blanca', 'Laguna Blanca'),
                ('Río Verde', 'Río Verde'),
                ('San Gregorio', 'San Gregorio'),
            ],
        }
        return comunas_por_ciudad.get(ciudad, [('', 'Selecciona primero una ciudad')])
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if telefono:
            telefono = telefono.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            if telefono.isdigit():
                if len(telefono) == 8:
                    telefono = '+569' + telefono
                elif len(telefono) == 9 and telefono.startswith('9'):
                    telefono = '+56' + telefono
                elif len(telefono) == 11 and telefono.startswith('569'):
                    telefono = '+' + telefono
                else:
                    raise forms.ValidationError('El teléfono debe tener 8 dígitos (se agregará +569 automáticamente)')
            elif telefono.startswith('+569'):
                if len(telefono) != 12 or not telefono[4:].isdigit():
                    raise forms.ValidationError('El teléfono debe tener el formato +56912345678')
            elif telefono.startswith('569'):
                if len(telefono) == 11:
                    telefono = '+' + telefono
                else:
                    raise forms.ValidationError('El teléfono debe tener 11 dígitos después de 569')
            else:
                raise forms.ValidationError('Formato de teléfono no válido. Ingresa solo 8 dígitos o el formato completo +56912345678')
            
            if not telefono.startswith('+569') or len(telefono) != 12 or not telefono[4:].isdigit():
                raise forms.ValidationError('El teléfono debe tener el formato +56912345678')
        return telefono


class MascotaForm(forms.ModelForm):
    fecha_nacimiento = forms.DateField(
        required=False,
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={
            'class': 'form-control w-full',
            'type': 'date',
            'id': 'fecha_nacimiento_input'
        }),
        help_text='Si conoces la fecha exacta, selecciónala aquí'
    )
    
    usar_edad_aproximada = forms.BooleanField(
        required=False,
        label='No recuerdo la fecha exacta',
        widget=forms.CheckboxInput(attrs={
            'class': 'toggle-edad-aproximada',
            'id': 'usar_edad_aproximada'
        })
    )
    
    edad_anios_aproximados = forms.IntegerField(
        required=False,
        label='Edad aproximada (años)',
        min_value=0,
        max_value=30,
        widget=forms.NumberInput(attrs={
            'class': 'form-control w-full campo-edad-aproximada',
            'placeholder': 'Ej: 2',
            'id': 'edad_anios_aproximados',
            'min': '0',
            'max': '30'
        }),
        help_text='Ingresa los años aproximados de edad'
    )
    
    edad_meses_aproximados = forms.IntegerField(
        required=False,
        label='Edad aproximada (meses adicionales)',
        min_value=0,
        max_value=11,
        widget=forms.NumberInput(attrs={
            'class': 'form-control w-full campo-edad-aproximada',
            'placeholder': 'Ej: 6',
            'id': 'edad_meses_aproximados',
            'min': '0',
            'max': '11'
        }),
        help_text='Meses adicionales (opcional, de 0 a 11)'
    )

    raza = forms.ChoiceField(
        required=False,
        label='Raza',
        choices=[('', 'Seleccionar raza')],
        widget=forms.Select(attrs={
            'class': 'form-control w-full',
            'id': 'id_raza'
        })
    )
    
    class Meta:
        model = Mascota
        fields = ('nombre', 'especie', 'raza', 'fecha_nacimiento', 'color_pelaje', 'sexo', 'esterilizado', 'foto')
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control w-full',
                'placeholder': 'Nombre de tu mascota'
            }),
            'especie': forms.Select(attrs={
                'class': 'form-control w-full',
                'id': 'id_especie'
            }),
            'color_pelaje': forms.TextInput(attrs={
                'class': 'form-control w-full',
                'placeholder': 'Ej: Blanco y negro'
            }),
            'sexo': forms.Select(attrs={
                'class': 'form-control w-full',
                'id': 'id_sexo'
            }),
            'esterilizado': forms.CheckboxInput(attrs={
                'class': 'form-control',
                'id': 'id_esterilizado'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar razas según la especie seleccionada
        especie = self.initial.get('especie') or (self.data.get('especie') if self.data else None)
        if especie:
            self.fields['raza'].choices = self._get_razas_choices(especie)
        else:
            self.fields['raza'].choices = [('', 'Selecciona primero la especie')]
    
    def _get_razas_choices(self, especie):
        """Retorna las opciones de raza según la especie"""
        if especie == 'perro':
            razas_perro = [
                ('Labrador Retriever', 'Labrador Retriever'),
                ('Golden Retriever', 'Golden Retriever'),
                ('Pastor Alemán', 'Pastor Alemán'),
                ('Bulldog Francés', 'Bulldog Francés'),
                ('Bulldog Inglés', 'Bulldog Inglés'),
                ('Beagle', 'Beagle'),
                ('Poodle', 'Poodle'),
                ('Rottweiler', 'Rottweiler'),
                ('Yorkshire Terrier', 'Yorkshire Terrier'),
                ('Boxer', 'Boxer'),
                ('Dachshund', 'Dachshund'),
                ('Siberian Husky', 'Siberian Husky'),
                ('Chihuahua', 'Chihuahua'),
                ('Border Collie', 'Border Collie'),
                ('Shih Tzu', 'Shih Tzu'),
                ('Maltés', 'Maltés'),
                ('Mestizo', 'Mestizo'),
                ('No lo sé', 'No lo sé'),
            ]
            return [('', 'Seleccionar raza')] + razas_perro
        elif especie == 'gato':
            razas_gato = [
                ('Persa', 'Persa'),
                ('Maine Coon', 'Maine Coon'),
                ('British Shorthair', 'British Shorthair'),
                ('Ragdoll', 'Ragdoll'),
                ('Siamés', 'Siamés'),
                ('Bengalí', 'Bengalí'),
                ('Abisinio', 'Abisinio'),
                ('Sphynx', 'Sphynx'),
                ('Scottish Fold', 'Scottish Fold'),
                ('American Shorthair', 'American Shorthair'),
                ('Ruso Azul', 'Ruso Azul'),
                ('Noruego del Bosque', 'Noruego del Bosque'),
                ('Mestizo', 'Mestizo'),
                ('No lo sé', 'No lo sé'),
            ]
            return [('', 'Seleccionar raza')] + razas_gato
        return [('', 'Seleccionar raza')]
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        usar_edad_aproximada = cleaned_data.get('usar_edad_aproximada')
        edad_anios = cleaned_data.get('edad_anios_aproximados')
        edad_meses = cleaned_data.get('edad_meses_aproximados')
        
        if not fecha_nacimiento and not usar_edad_aproximada:
            raise forms.ValidationError('Debes proporcionar la fecha de nacimiento o seleccionar edad aproximada.')
        
        if usar_edad_aproximada:
            if edad_anios is None:
                raise forms.ValidationError('Debes ingresar los años aproximados de edad.')
            
            if edad_anios < 0 or edad_anios > 30:
                raise forms.ValidationError('Los años deben estar entre 0 y 30.')
            
            if edad_meses is not None:
                if edad_meses < 0 or edad_meses > 11:
                    raise forms.ValidationError('Los meses adicionales deben estar entre 0 y 11.')
            
            if edad_anios == 0 and (edad_meses is None or edad_meses == 0):
                raise forms.ValidationError('Debes ingresar al menos 1 mes de edad aproximada.')
            
            if fecha_nacimiento:
                cleaned_data['fecha_nacimiento'] = None
            
            today = timezone.now().date()
            dias_aproximados = (edad_anios * 365) + ((edad_meses or 0) * 30)
            fecha_aproximada = today - timedelta(days=dias_aproximados)
            cleaned_data['fecha_nacimiento'] = fecha_aproximada
        
        return cleaned_data


class FichaClinicaForm(forms.ModelForm):
    tipo_sangre = forms.ChoiceField(
        required=False,
        label='Tipo de Sangre',
        choices=[
            ('', 'Seleccionar tipo'),
            ('DEA1.1+', 'DEA 1.1+ (Perro)'),
            ('DEA1.1-', 'DEA 1.1- (Perro)'),
            ('TIPO_A', 'Tipo A (Gato)'),
            ('TIPO_B', 'Tipo B (Gato)'),
            ('TIPO_AB', 'Tipo AB (Gato)'),
            ('DESCONOCIDO', 'Desconocido'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control w-full',
            'placeholder': 'Seleccionar tipo'
        })
    )
    peso = forms.DecimalField(
        required=False,
        label='Peso (kg)',
        help_text='Puedes ingresar un valor aproximado.',
        widget=forms.NumberInput(attrs={
            'class': 'form-control w-full',
            'placeholder': 'Ej: 5.5',
            'step': '0.1'
        })
    )
    temperatura = forms.DecimalField(
        required=False,
        label='Temperatura (°C)',
        help_text='Deja vacío si no tienes esta información',
        widget=forms.NumberInput(attrs={
            'class': 'form-control w-full',
            'placeholder': 'Ej: 38.5 (opcional)',
            'step': '0.1'
        })
    )
    no_tengo_temperatura = forms.BooleanField(
        required=False,
        label='No tengo esta información',
        widget=forms.CheckboxInput(attrs={
            'class': 'toggle-no-info',
            'id': 'no_tengo_temperatura'
        })
    )
    esterilizado = forms.ChoiceField(
        required=False,
        label='Esterilizado',
        choices=[
            ('', 'Seleccionar opción'),
            ('si', 'Sí'),
            ('no', 'No'),
            ('desconocido', 'Desconocido'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control w-full',
            'id': 'id_esterilizado'
        })
    )
    vacunas_estado = forms.ChoiceField(
        required=False,
        label='Vacunas',
        choices=[('', 'Seleccionar opción')],
        widget=forms.Select(attrs={
            'class': 'form-control w-full',
            'id': 'id_vacunas_estado'
        })
    )
    vacuna_otra_texto = forms.CharField(
        required=False,
        label='Especificar otra vacuna',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control w-full',
            'id': 'id_vacuna_otra_texto',
            'placeholder': 'Escribe el nombre de la vacuna',
            'style': 'display:none;'
        })
    )
    ultima_vacuna_fecha = forms.DateField(
        required=False,
        label='Fecha de la Última Vacuna',
        widget=forms.DateInput(attrs={
            'class': 'form-control w-full',
            'type': 'date',
            'id': 'id_ultima_vacuna_fecha',
            'disabled': True
        }),
        help_text='Opcional - Solo se habilita al seleccionar una vacuna específica'
    )

    class Meta:
        model = FichaClinica
        fields = (
            'tipo_sangre', 'peso', 'temperatura',
            'alergias', 'condiciones_cronicas',
            'medicamentos_actuales', 'historial_enfermedades', 'microchip', 'comentarios'
        )
        widgets = {
            'alergias': forms.Textarea(attrs={
                'class': 'form-control w-full',
                'rows': 4,
                'placeholder': 'Describa las alergias conocidas de la mascota. Escribe "No tengo información" o "N/A" si no conoces esta información.'
            }),
            'condiciones_cronicas': forms.Textarea(attrs={
                'class': 'form-control w-full',
                'rows': 4,
                'placeholder': 'Ej: Diabetes, artritis, problemas cardíacos. Escribe "No tengo información" o "N/A" si no conoces esta información.'
            }),
            'medicamentos_actuales': forms.Textarea(attrs={
                'class': 'form-control w-full',
                'rows': 4,
                'placeholder': 'Nombre del medicamento, dosis y frecuencia. Escribe "No tengo información" o "N/A" si no conoces esta información.'
            }),
            'historial_enfermedades': forms.Textarea(attrs={
                'class': 'form-control w-full',
                'rows': 4,
                'placeholder': 'Historial de enfermedades previas y tratamientos. Escribe "No tengo información" o "N/A" si no conoces esta información.'
            }),
            'microchip': forms.TextInput(attrs={
                'class': 'form-control w-full',
                'placeholder': 'Ej: M000001',
                'readonly': True,
                'style': 'background-color: #f5f5f5; cursor: not-allowed;'
            }),
            'comentarios': forms.Textarea(attrs={
                'class': 'form-control w-full',
                'rows': 4,
                'placeholder': 'Observaciones generales sobre la salud de la mascota.'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        mascota = kwargs.pop('mascota', None)
        es_nuevo_registro = kwargs.pop('es_nuevo_registro', False)
        super().__init__(*args, **kwargs)
        
        # Si es un nuevo registro (no el primero), ocultar campos fijos
        if es_nuevo_registro and self.instance and self.instance.pk:
            # Si ya tiene datos (no es el primer registro), ocultar campos fijos
            # Ocultar campos fijos siempre que sea un nuevo registro (ya tiene datos previos)
            if 'tipo_sangre' in self.fields:
                self.fields['tipo_sangre'].widget = forms.HiddenInput()
            if 'esterilizado' in self.fields:
                self.fields['esterilizado'].widget = forms.HiddenInput()
        
        # Mapear valores existentes de tipo_sangre al nuevo formato
        if self.instance and self.instance.pk and self.instance.tipo_sangre:
            tipo_sangre_actual = self.instance.tipo_sangre
            if tipo_sangre_actual in ['DEA1.1+', 'DEA1.1-']:
                # Ya está en el formato correcto
                pass
            elif tipo_sangre_actual == 'A+':
                self.initial['tipo_sangre'] = 'TIPO_A'
            elif tipo_sangre_actual == 'B+':
                self.initial['tipo_sangre'] = 'TIPO_B'
            elif tipo_sangre_actual == 'AB+':
                self.initial['tipo_sangre'] = 'TIPO_AB'
            else:
                self.initial['tipo_sangre'] = 'DESCONOCIDO'
        
        # Configurar opciones de vacunas según la especie
        if mascota:
            if mascota.especie == Mascota.ESPECIE_PERRO:
                vacunas_choices = [
                    ('', 'Seleccionar opción'),
                    ('Polivalente', 'Polivalente'),
                    ('Antirrábica', 'Antirrábica'),
                    ('Bordetella', 'Bordetella'),
                    ('Leptospirosis', 'Leptospirosis'),
                    ('Parvovirus', 'Parvovirus'),
                    ('Moquillo', 'Moquillo'),
                    ('Hepatitis', 'Hepatitis'),
                    ('Otra', 'Otra'),
                    ('no', 'No'),
                    ('desconocido', 'Desconocido'),
                ]
            else:  # Gato
                vacunas_choices = [
                    ('', 'Seleccionar opción'),
                    ('Triple felina', 'Triple felina'),
                    ('Antirrábica', 'Antirrábica'),
                    ('Leucemia felina', 'Leucemia felina'),
                    ('Peritonitis infecciosa', 'Peritonitis infecciosa'),
                    ('Rinotraqueitis', 'Rinotraqueitis'),
                    ('Calicivirus', 'Calicivirus'),
                    ('Panleucopenia', 'Panleucopenia'),
                    ('Otra', 'Otra'),
                    ('no', 'No'),
                    ('desconocido', 'Desconocido'),
                ]
            self.fields['vacunas_estado'].choices = vacunas_choices
            
            # Mapear valores existentes de vacunas
            if es_nuevo_registro and self.instance and self.instance.pk:
                # Verificar si hay información de vacunas en comentarios primero
                if self.instance.comentarios and 'Última vacuna:' in self.instance.comentarios:
                    import re
                    match = re.search(r'Última vacuna: ([^-]+)', self.instance.comentarios)
                    if match:
                        vacuna_nombre = match.group(1).strip()
                        if vacuna_nombre in [choice[0] for choice in vacunas_choices]:
                            self.initial['vacunas_estado'] = vacuna_nombre
                        else:
                            self.initial['vacunas_estado'] = 'desconocido'
                    else:
                        self.initial['vacunas_estado'] = 'desconocido'
                elif self.instance.vacunas_al_dia:
                    # Si está al día pero no hay vacuna específica, usar "desconocido" por ahora
                    self.initial['vacunas_estado'] = 'desconocido'
                else:
                    self.initial['vacunas_estado'] = 'desconocido'
            
            # Mapear valores existentes de esterilizado (solo en nuevos registros para no preseleccionar)
            if es_nuevo_registro and self.instance and self.instance.pk:
                if self.instance.esterilizado is True:
                    self.initial['esterilizado'] = 'si'
                elif self.instance.esterilizado is False:
                    self.initial['esterilizado'] = 'no'
                else:
                    self.initial['esterilizado'] = 'desconocido'
    
    def clean(self):
        cleaned_data = super().clean()
        esterilizado = cleaned_data.get('esterilizado', '')
        vacunas_estado = cleaned_data.get('vacunas_estado', '')
        ultima_vacuna_fecha = cleaned_data.get('ultima_vacuna_fecha')
        no_tengo_temperatura = cleaned_data.get('no_tengo_temperatura', False)
        temperatura = cleaned_data.get('temperatura')
        
        # Si marca "no tengo temperatura", limpiar el campo temperatura
        if no_tengo_temperatura:
            cleaned_data['temperatura'] = None
        
        # Manejar esterilizado - convertir a boolean para el modelo
        # Si el campo está oculto (es un nuevo registro), mantener el valor existente
        if 'esterilizado' not in cleaned_data or not cleaned_data.get('esterilizado'):
            if self.instance and self.instance.pk:
                cleaned_data['esterilizado'] = self.instance.esterilizado
            else:
                cleaned_data['esterilizado'] = False
        else:
            esterilizado = cleaned_data.get('esterilizado')
            if esterilizado == 'si':
                cleaned_data['esterilizado'] = True
            elif esterilizado == 'no':
                cleaned_data['esterilizado'] = False
            else:  # desconocido
                cleaned_data['esterilizado'] = False  # Por defecto False, pero guardamos en comentarios
        
        # Manejar vacunas
        vacunas_especificas = ['Polivalente', 'Antirrábica', 'Bordetella', 'Leptospirosis', 
                              'Parvovirus', 'Moquillo', 'Hepatitis', 'Otra',
                              'Triple felina', 'Leucemia felina', 'Peritonitis infecciosa',
                              'Rinotraqueitis', 'Calicivirus', 'Panleucopenia']
        
        if vacunas_estado in vacunas_especificas:
            cleaned_data['vacunas_al_dia'] = True
            # Si es "Otra", usar el texto personalizado
            nombre_vacuna = vacunas_estado
            if vacunas_estado == 'Otra':
                vacuna_otra_texto = cleaned_data.get('vacuna_otra_texto', '').strip()
                if vacuna_otra_texto:
                    nombre_vacuna = vacuna_otra_texto
                else:
                    nombre_vacuna = 'Otra (sin especificar)'
            
            # Guardar información de la vacuna en comentarios
            comentarios_actual = cleaned_data.get('comentarios', '') or ''
            # Limpiar información anterior de vacunas si existe
            if 'Última vacuna:' in comentarios_actual:
                import re
                comentarios_actual = re.sub(r'Última vacuna:.*?(?=\n|$)', '', comentarios_actual).strip()
            info_vacuna = f"Última vacuna: {nombre_vacuna}"
            if ultima_vacuna_fecha:
                info_vacuna += f" - Fecha: {ultima_vacuna_fecha.strftime('%d/%m/%Y')}"
            if comentarios_actual:
                cleaned_data['comentarios'] = f"{comentarios_actual}\n{info_vacuna}".strip()
            else:
                cleaned_data['comentarios'] = info_vacuna
        elif vacunas_estado == 'no':
            cleaned_data['vacunas_al_dia'] = False
        else:  # desconocido o vacío
            cleaned_data['vacunas_al_dia'] = False
        
        # Manejar tipo_sangre
        # Si el campo está oculto (es un nuevo registro), mantener el valor existente
        tipo_sangre = cleaned_data.get('tipo_sangre')
        if not tipo_sangre and self.instance and self.instance.pk:
            # Si no se proporcionó tipo_sangre y hay una instancia, mantener el valor existente
            cleaned_data['tipo_sangre'] = self.instance.tipo_sangre
            tipo_sangre = self.instance.tipo_sangre
        
        if tipo_sangre:
            if tipo_sangre == 'DESCONOCIDO':
                cleaned_data['tipo_sangre'] = None
            elif tipo_sangre == 'TIPO_A':
                cleaned_data['tipo_sangre'] = 'A+'
            elif tipo_sangre == 'TIPO_B':
                cleaned_data['tipo_sangre'] = 'B+'
            elif tipo_sangre == 'TIPO_AB':
                cleaned_data['tipo_sangre'] = 'AB+'
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Asegurar que esterilizado y vacunas_al_dia se guarden correctamente
        esterilizado = self.cleaned_data.get('esterilizado')
        vacunas_al_dia = self.cleaned_data.get('vacunas_al_dia', False)
        
        if isinstance(esterilizado, bool):
            instance.esterilizado = esterilizado
        instance.vacunas_al_dia = vacunas_al_dia
        
        if commit:
            instance.save()
        return instance


class EventoClinicoForm(forms.ModelForm):
    fecha_evento = forms.DateField(
        required=True,
        label='Fecha del evento',
        widget=forms.DateInput(attrs={
            'class': 'form-control w-full',
            'type': 'date'
        })
    )
    hora_evento = forms.TimeField(
        required=False,
        label='Hora del evento',
        widget=forms.TimeInput(attrs={
            'class': 'form-control w-full',
            'type': 'time',
            'style': 'width:100%; padding:0.4rem 0.4rem 0.4rem 2rem; border:1px solid #e0e0e0; border-radius:0.25rem; font-size:0.55rem; background-color:#ffffff;'
        })
    )
    tipo_evento = forms.ChoiceField(
        required=True,
        label='Tipo de evento',
        choices=[
            ('', 'Seleccionar tipo'),
            ('cita_general', 'Cita General'),
            ('cita_especialista', 'Cita Especialista'),
            ('medicacion', 'Medicación'),
            ('curacion', 'Curación'),
            ('vacuna', 'Vacuna'),
            ('desparasitacion', 'Desparasitación'),
            ('comentario', 'Comentario'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control w-full'
        })
    )
    archivos = forms.FileField(
        required=False,
        label='Archivos adjuntos',
        widget=forms.FileInput(attrs={
            'class': 'form-control w-full',
            'accept': '.jpg,.jpeg,.png,.gif,.webp,.pdf,.doc,.docx,.txt',
            'id': 'id_archivos_evento'
        }),
        help_text='Puedes adjuntar imágenes (JPG, PNG, GIF, WEBP) o documentos (PDF, DOC, DOCX, TXT). Máximo 10MB por archivo. Puedes seleccionar múltiples archivos.'
    )

    class Meta:
        model = EventoClinico
        fields = ('fecha_evento', 'hora_evento', 'tipo_evento', 'descripcion', 'diagnostico', 'veterinario', 'medicacion', 'consideraciones')
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control w-full',
                'rows': 3,
                'placeholder': 'Descripción del evento, observaciones...'
            }),
            'diagnostico': forms.Textarea(attrs={
                'class': 'form-control w-full',
                'rows': 3,
                'placeholder': 'Diagnóstico del evento clínico (opcional)'
            }),
            'veterinario': forms.TextInput(attrs={
                'class': 'form-control w-full',
                'placeholder': 'Nombre del veterinario (opcional)'
            }),
            'medicacion': forms.Textarea(attrs={
                'class': 'form-control w-full',
                'rows': 3,
                'placeholder': 'Medicamentos, dosis, frecuencia... (opcional)'
            }),
            'consideraciones': forms.Textarea(attrs={
                'class': 'form-control w-full',
                'rows': 6,
                'placeholder': 'Consideraciones especiales, observaciones, recomendaciones... (opcional)'
            }),
        }
    
    def clean(self):
        """Valida los archivos adjuntos si existen"""
        cleaned_data = super().clean()
        
        # Los archivos se validan en la vista porque FileField no funciona bien con múltiples archivos
        return cleaned_data
    
    def save(self, commit=True, archivos_adjuntos=None):
        """Guarda el evento y los archivos adjuntos"""
        evento = super().save(commit=commit)
        
        if commit and archivos_adjuntos:
            # Guardar archivos adjuntos pasados desde la vista
            for archivo in archivos_adjuntos:
                extension = archivo.name.split('.')[-1].lower() if '.' in archivo.name else ''
                ArchivoAdjunto.objects.create(
                    evento_clinico=evento,
                    nombre=archivo.name,
                    archivo=archivo,
                    tipo_archivo=extension,
                    tamano=archivo.size
                )
        
        return evento
