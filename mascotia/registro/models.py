from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class PerfilTutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_tutor')
    sobrenombre = models.CharField(max_length=100, blank=True, null=True, verbose_name='Sobrenombre')
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono')
    ocupacion = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ocupación')
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name='Fecha de Nacimiento')
    calle = models.CharField(max_length=255, blank=True, null=True, verbose_name='Calle')
    numero = models.CharField(max_length=50, blank=True, null=True, verbose_name='Número')
    ciudad = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ciudad')
    comuna = models.CharField(max_length=100, blank=True, null=True, verbose_name='Comuna')
    foto_perfil = models.ImageField(upload_to='perfiles_tutores/', blank=True, null=True, verbose_name='Foto de Perfil')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Tutor'
        verbose_name_plural = 'Perfiles de Tutores'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f'Perfil de {self.nombre_para_mostrar}'
    
    @property
    def perfil_completo(self):
        return bool(self.telefono and self.ocupacion)
    
    def get_telefono_display(self):
        if self.telefono and self.telefono.startswith('+569'):
            return self.telefono[4:]
        return self.telefono
    
    @property
    def nombre_para_mostrar(self):
        if self.sobrenombre and self.sobrenombre.strip():
            return self.sobrenombre
        return self.user.first_name or self.user.username


class Mascota(models.Model):
    ESPECIE_PERRO = 'perro'
    ESPECIE_GATO = 'gato'
    ESPECIE_CHOICES = (
        (ESPECIE_PERRO, 'Perro'),
        (ESPECIE_GATO, 'Gato'),
    )
    
    SEXO_MACHO = 'macho'
    SEXO_HEMBRA = 'hembra'
    SEXO_CHOICES = (
        (SEXO_MACHO, 'Macho'),
        (SEXO_HEMBRA, 'Hembra'),
    )

    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mascotas')
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=10, choices=ESPECIE_CHOICES)
    raza = models.CharField(max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    color_pelaje = models.CharField(max_length=100, blank=True, null=True)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, blank=True, null=True, verbose_name='Sexo')
    esterilizado = models.BooleanField(default=False, verbose_name='Esterilizado')
    microchip = models.CharField(max_length=100, blank=True, null=True)
    foto = models.ImageField(upload_to='mascotas/', blank=True, null=True, verbose_name='Foto de la Mascota')
    activa = models.BooleanField(default=True, verbose_name='Activa')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mascota'
        verbose_name_plural = 'Mascotas'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_especie_display()})"

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return 'Sin información'
        today = timezone.now().date()
        years = today.year - self.fecha_nacimiento.year
        months = today.month - self.fecha_nacimiento.month
        days = today.day - self.fecha_nacimiento.day
        if days < 0:
            months -= 1
        if months < 0:
            years -= 1
            months += 12
        partes = []
        if years > 0:
            partes.append(f"{years} año{'s' if years != 1 else ''}")
        if months > 0:
            partes.append(f"{months} mes{'es' if months != 1 else ''}")
        return ' '.join(partes) if partes else 'Menos de 1 mes'

    @property
    def edad_en_anios(self):
        if not self.fecha_nacimiento:
            return None
        today = timezone.now().date()
        dias = (today - self.fecha_nacimiento).days
        return dias / 365.25 if dias >= 0 else 0


class PesoMascota(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='pesos')
    fecha = models.DateField(default=timezone.now)
    peso = models.DecimalField(max_digits=5, decimal_places=2, help_text='Peso en kilogramos')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de Peso'
        verbose_name_plural = 'Registros de Peso'
        ordering = ['fecha']

    def __str__(self):
        return f"{self.mascota.nombre} - {self.peso} kg ({self.fecha})"


class FichaClinica(models.Model):
    TIPO_SANGRE_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('DEA1.1+', 'DEA1.1+'),
        ('DEA1.1-', 'DEA1.1-'),
        ('DEA1.2+', 'DEA1.2+'),
        ('DEA1.2-', 'DEA1.2-'),
    )

    mascota = models.OneToOneField(Mascota, on_delete=models.CASCADE, related_name='ficha_clinica')
    tipo_sangre = models.CharField(max_length=10, choices=TIPO_SANGRE_CHOICES, blank=True, null=True, verbose_name='Tipo de Sangre')
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='Peso (kg)')
    temperatura = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name='Temperatura (°C)')
    frecuencia_cardiaca = models.IntegerField(blank=True, null=True, verbose_name='Frecuencia Cardíaca (lpm)')
    esterilizado = models.BooleanField(default=False)
    vacunas_al_dia = models.BooleanField(default=False, verbose_name='Vacunas al Día')
    alergias = models.TextField(blank=True, null=True)
    condiciones_cronicas = models.TextField(blank=True, null=True, verbose_name='Condiciones Crónicas')
    medicamentos_actuales = models.TextField(blank=True, null=True, verbose_name='Medicamentos Actuales')
    historial_enfermedades = models.TextField(blank=True, null=True, verbose_name='Historial de Enfermedades')
    ultima_visita = models.DateField(blank=True, null=True, verbose_name='Última Visita')
    proxima_cita = models.DateField(blank=True, null=True, verbose_name='Próxima Cita')
    microchip = models.CharField(max_length=100, blank=True, null=True)
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios Adicionales')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ficha Clínica'
        verbose_name_plural = 'Fichas Clínicas'

    def __str__(self):
        return f"Ficha clínica de {self.mascota.nombre}"
    
    def get_tipo_sangre_display_formatted(self):
        """Retorna el tipo de sangre con formato amigable"""
        if not self.tipo_sangre:
            return 'Sin información'
        
        tipo_map = {
            'DEA1.1+': 'DEA 1.1+ (Perro)',
            'DEA1.1-': 'DEA 1.1- (Perro)',
            'A+': 'Tipo A (Gato)',
            'A-': 'Tipo A (Gato)',
            'B+': 'Tipo B (Gato)',
            'B-': 'Tipo B (Gato)',
            'AB+': 'Tipo AB (Gato)',
            'AB-': 'Tipo AB (Gato)',
            'O+': 'Desconocido',
            'O-': 'Desconocido',
            'DEA1.2+': 'DEA 1.2+ (Perro)',
            'DEA1.2-': 'DEA 1.2- (Perro)',
        }
        return tipo_map.get(self.tipo_sangre, self.get_tipo_sangre_display())
    
    @property
    def tiene_datos(self):
        """Verifica si la ficha tiene datos guardados"""
        if any([
            self.tipo_sangre,
            self.peso is not None,
            self.temperatura is not None,
            self.frecuencia_cardiaca is not None,
            self.esterilizado,
            self.vacunas_al_dia,
            bool(self.alergias and self.alergias.strip()),
            bool(self.condiciones_cronicas and self.condiciones_cronicas.strip()),
            bool(self.medicamentos_actuales and self.medicamentos_actuales.strip()),
            bool(self.historial_enfermedades and self.historial_enfermedades.strip()),
            bool(self.comentarios and self.comentarios.strip()),
        ]):
            return True
        return self.eventos.exists() if hasattr(self, 'eventos') else False


class HistorialFichaClinica(models.Model):
    """Modelo para guardar el historial de actualizaciones de fichas clínicas"""
    ficha_clinica = models.ForeignKey(FichaClinica, on_delete=models.CASCADE, related_name='historial_registros')
    tipo_sangre = models.CharField(max_length=10, choices=FichaClinica.TIPO_SANGRE_CHOICES, blank=True, null=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    temperatura = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    esterilizado = models.BooleanField(default=False)
    vacunas_al_dia = models.BooleanField(default=False)
    vacuna_nombre = models.CharField(max_length=200, blank=True, null=True)
    vacuna_fecha = models.DateField(blank=True, null=True)
    alergias = models.TextField(blank=True, null=True)
    condiciones_cronicas = models.TextField(blank=True, null=True)
    medicamentos_actuales = models.TextField(blank=True, null=True)
    historial_enfermedades = models.TextField(blank=True, null=True)
    comentarios = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Registro Histórico'
        verbose_name_plural = 'Registros Históricos'
        ordering = ['-creado_en']
    
    def __str__(self):
        return f"Registro de {self.ficha_clinica.mascota.nombre} - {self.creado_en.strftime('%d/%m/%Y')}"
    
    def get_tipo_sangre_display(self):
        """Retorna el tipo de sangre con formato amigable"""
        if not self.tipo_sangre:
            return 'Desconocido'
        
        tipo_map = {
            'DEA1.1+': 'DEA 1.1+ (Perro)',
            'DEA1.1-': 'DEA 1.1- (Perro)',
            'A+': 'Tipo A (Gato)',
            'A-': 'Tipo A (Gato)',
            'B+': 'Tipo B (Gato)',
            'B-': 'Tipo B (Gato)',
            'AB+': 'Tipo AB (Gato)',
            'AB-': 'Tipo AB (Gato)',
            'O+': 'Desconocido',
            'O-': 'Desconocido',
            'DEA1.2+': 'DEA 1.2+ (Perro)',
            'DEA1.2-': 'DEA 1.2- (Perro)',
        }
        return tipo_map.get(self.tipo_sangre, self.tipo_sangre)


class EventoClinico(models.Model):
    TIPO_CITA_GENERAL = 'cita_general'
    TIPO_CITA_ESPECIALISTA = 'cita_especialista'
    TIPO_MEDICACION = 'medicacion'
    TIPO_CURACION = 'curacion'
    TIPO_VACUNA = 'vacuna'
    TIPO_DESPARASITACION = 'desparasitacion'
    TIPO_COMENTARIO = 'comentario'
    
    TIPO_EVENTO_CHOICES = (
        (TIPO_CITA_GENERAL, 'Cita General'),
        (TIPO_CITA_ESPECIALISTA, 'Cita Especialista'),
        (TIPO_MEDICACION, 'Medicación'),
        (TIPO_CURACION, 'Curación'),
        (TIPO_VACUNA, 'Vacuna'),
        (TIPO_DESPARASITACION, 'Desparasitación'),
        (TIPO_COMENTARIO, 'Comentario'),
    )
    
    ficha_clinica = models.ForeignKey(FichaClinica, on_delete=models.CASCADE, related_name='eventos')
    fecha_evento = models.DateField()
    hora_evento = models.TimeField(blank=True, null=True, verbose_name='Hora del evento')
    tipo_evento = models.CharField(max_length=50, choices=TIPO_EVENTO_CHOICES, default=TIPO_COMENTARIO)
    descripcion = models.TextField(blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True, verbose_name='Diagnóstico')
    veterinario = models.CharField(max_length=150, blank=True, null=True)
    medicacion = models.TextField(blank=True, null=True)
    proximos_eventos = models.TextField(blank=True, null=True)
    consideraciones = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Evento Clínico'
        verbose_name_plural = 'Eventos Clínicos'
        ordering = ['-fecha_evento']

    def __str__(self):
        return f"{self.get_tipo_evento_display()} - {self.ficha_clinica.mascota.nombre} ({self.fecha_evento})"
    
    def obtener_archivos_adjuntos(self):
        """Retorna todos los archivos adjuntos del evento"""
        return self.archivos_adjuntos.all()
    
    def validar_campos(self):
        """Valida que los campos obligatorios estén completos"""
        if not self.fecha_evento:
            return False
        if not self.tipo_evento:
            return False
        return True


class ArchivoAdjunto(models.Model):
    """Modelo para archivos adjuntos a eventos clínicos"""
    # Formatos permitidos
    FORMATOS_PERMITIDOS_IMAGENES = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    FORMATOS_PERMITIDOS_DOCUMENTOS = ['pdf', 'doc', 'docx', 'txt']
    FORMATOS_PERMITIDOS = FORMATOS_PERMITIDOS_IMAGENES + FORMATOS_PERMITIDOS_DOCUMENTOS
    
    # Tamaño máximo en bytes (10MB)
    TAMANO_MAXIMO = 10 * 1024 * 1024
    
    evento_clinico = models.ForeignKey(EventoClinico, on_delete=models.CASCADE, related_name='archivos_adjuntos')
    nombre = models.CharField(max_length=255, verbose_name='Nombre del archivo')
    archivo = models.FileField(upload_to='archivos_eventos/%Y/%m/%d/', verbose_name='Archivo')
    tipo_archivo = models.CharField(max_length=50, blank=True, null=True, verbose_name='Tipo de archivo')
    tamano = models.BigIntegerField(verbose_name='Tamaño (bytes)')
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de subida')
    
    class Meta:
        verbose_name = 'Archivo Adjunto'
        verbose_name_plural = 'Archivos Adjuntos'
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.nombre} - {self.evento_clinico}"
    
    def obtener_extension(self):
        """Retorna la extensión del archivo"""
        if self.archivo:
            return self.archivo.name.split('.')[-1].lower()
        return ''
    
    def validar_formato(self):
        """Valida que el formato del archivo sea permitido"""
        extension = self.obtener_extension()
        return extension in self.FORMATOS_PERMITIDOS
    
    def es_imagen(self):
        """Verifica si el archivo es una imagen"""
        extension = self.obtener_extension()
        return extension in self.FORMATOS_PERMITIDOS_IMAGENES
    
    def es_documento(self):
        """Verifica si el archivo es un documento"""
        extension = self.obtener_extension()
        return extension in self.FORMATOS_PERMITIDOS_DOCUMENTOS
    
    def obtener_tamano_display(self):
        """Retorna el tamaño del archivo en formato legible"""
        if self.tamano < 1024:
            return f"{self.tamano} B"
        elif self.tamano < 1024 * 1024:
            return f"{self.tamano / 1024:.2f} KB"
        else:
            return f"{self.tamano / (1024 * 1024):.2f} MB"


@receiver(post_save, sender=User)
def crear_perfil_tutor(sender, instance, created, **kwargs):
    if created:
        PerfilTutor.objects.get_or_create(user=instance)


@receiver(post_save, sender=Mascota)
def crear_ficha_clinica(sender, instance, created, **kwargs):
    if created:
        ficha, _ = FichaClinica.objects.get_or_create(mascota=instance)
        if instance.microchip and not ficha.microchip:
            ficha.microchip = instance.microchip
            ficha.save(update_fields=['microchip'])
