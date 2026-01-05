from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.inicio_view, name='inicio'),
    path('inicio/', RedirectView.as_view(pattern_name='inicio', permanent=False)),
    path('login/', views.login_view, name='login'),
    path('recuperar-clave/', views.recuperar_clave_view, name='recuperar_clave'),
    path('registro/', views.registro_view, name='registro'),
    path('home/', views.home_view, name='home'),
    path('perfil-tutor/', views.perfil_view, name='perfil_tutor'),
    path('completar-perfil/', views.completar_perfil_view, name='completar_perfil'),
    path('registro-mascota/', views.registro_mascota_view, name='registro_mascota'),
    path('registrar_mascotas/', RedirectView.as_view(pattern_name='registro_mascota', permanent=True)),
    path('mascotas/<int:mascota_id>/historial/', RedirectView.as_view(pattern_name='bitacora_mascota', permanent=True)),
    path('mascotas/<int:mascota_id>/bitacora/', views.bitacora_mascota_view, name='bitacora_mascota'),
    path('mascotas/<int:mascota_id>/perfil/', views.perfil_mascota_view, name='perfil_mascota'),
    path('mascotas/<int:mascota_id>/desactivar/', views.desactivar_mascota_view, name='desactivar_mascota'),
    path('mascotas/<int:mascota_id>/agregar-peso/', views.agregar_peso_mascota_view, name='agregar_peso_mascota'),
    path('mascotas/<int:mascota_id>/actualizar-foto/', views.actualizar_foto_mascota_view, name='actualizar_foto_mascota'),
    path('actualizar-foto-perfil/', views.actualizar_foto_perfil_banner_view, name='actualizar_foto_perfil_banner'),
    path('logout/', views.logout_view, name='logout'),
]