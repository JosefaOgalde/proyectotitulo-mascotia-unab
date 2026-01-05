from django.contrib import admin
from .models import PerfilTutor, Mascota, PesoMascota, FichaClinica, EventoClinico, HistorialFichaClinica, ArchivoAdjunto


@admin.register(PerfilTutor)
class PerfilTutorAdmin(admin.ModelAdmin):
    list_display = ('user', 'sobrenombre', 'telefono', 'ocupacion', 'ciudad', 'perfil_completo_display', 'fecha_creacion')
    list_filter = ('ciudad', 'fecha_creacion', 'ocupacion')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'sobrenombre', 'telefono', 'ocupacion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    def perfil_completo_display(self, obj):
        return obj.perfil_completo
    perfil_completo_display.short_description = 'Perfil completo'
    perfil_completo_display.boolean = True
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user', 'sobrenombre')
        }),
        ('Información Personal', {
            'fields': ('telefono', 'ocupacion', 'fecha_nacimiento')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'ciudad')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'especie', 'raza', 'tutor', 'fecha_nacimiento', 'color_pelaje')
    list_filter = ('especie', 'color_pelaje')
    search_fields = ('nombre', 'raza', 'tutor__username', 'tutor__email')
    autocomplete_fields = ('tutor',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


@admin.register(PesoMascota)
class PesoMascotaAdmin(admin.ModelAdmin):
    list_display = ('mascota', 'peso', 'fecha')
    list_filter = ('mascota__especie', 'fecha')
    search_fields = ('mascota__nombre',)
    date_hierarchy = 'fecha'


@admin.register(FichaClinica)
class FichaClinicaAdmin(admin.ModelAdmin):
    list_display = ('mascota', 'esterilizado', 'microchip', 'creado_en')
    search_fields = ('mascota__nombre', 'microchip', 'alergias')
    list_filter = ('esterilizado',)


@admin.register(EventoClinico)
class EventoClinicoAdmin(admin.ModelAdmin):
    list_display = ('ficha_clinica', 'fecha_evento', 'tipo_evento', 'veterinario')
    search_fields = ('ficha_clinica__mascota__nombre', 'tipo_evento', 'descripcion', 'diagnostico', 'veterinario')
    list_filter = ('fecha_evento', 'tipo_evento')
    date_hierarchy = 'fecha_evento'


@admin.register(HistorialFichaClinica)
class HistorialFichaClinicaAdmin(admin.ModelAdmin):
    list_display = ('ficha_clinica', 'peso', 'temperatura', 'creado_en')
    list_filter = ('creado_en',)
    search_fields = ('ficha_clinica__mascota__nombre',)
    date_hierarchy = 'creado_en'
    readonly_fields = ('creado_en',)


@admin.register(ArchivoAdjunto)
class ArchivoAdjuntoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'evento_clinico', 'tipo_archivo', 'tamano', 'fecha_subida')
    list_filter = ('tipo_archivo', 'fecha_subida')
    search_fields = ('nombre', 'evento_clinico__ficha_clinica__mascota__nombre')
    date_hierarchy = 'fecha_subida'
    readonly_fields = ('fecha_subida', 'tamano')
