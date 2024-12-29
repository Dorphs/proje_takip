from django.contrib import admin
from .models import DaireBaskanligi, SubeMudurlugu, CustomUser, Proje, Gorev, Ilerleme, Dosya, Fotograf

@admin.register(DaireBaskanligi)
class DaireBaskanligi(admin.ModelAdmin):
    """Daire Başkanlığı yönetimi"""
    list_display = ['ad']
    search_fields = ['ad']

@admin.register(SubeMudurlugu)
class SubeMudurluguAdmin(admin.ModelAdmin):
    """Şube Müdürlüğü yönetimi"""
    list_display = ['ad', 'daire_baskanligi']
    list_filter = ['daire_baskanligi']
    search_fields = ['ad', 'daire_baskanligi__ad']

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Kullanıcı yönetimi"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'daire_baskanligi', 'sube_mudurlugu']
    list_filter = ['role', 'daire_baskanligi', 'sube_mudurlugu']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filter_horizontal = ['groups', 'user_permissions']

@admin.register(Proje)
class ProjeAdmin(admin.ModelAdmin):
    """Proje yönetimi"""
    list_display = ['ad', 'daire_baskanligi', 'sube_mudurlugu', 'durum', 'baslama_tarihi', 'bitis_tarihi']
    list_filter = ['durum', 'daire_baskanligi', 'sube_mudurlugu']
    search_fields = ['ad', 'aciklama']
    filter_horizontal = ['atanan_kisiler']
    date_hierarchy = 'baslama_tarihi'

@admin.register(Gorev)
class GorevAdmin(admin.ModelAdmin):
    """Görev yönetimi"""
    list_display = ['baslik', 'proje', 'atanan', 'son_tarih', 'durum']
    list_filter = ['durum', 'proje__daire_baskanligi', 'proje__sube_mudurlugu']
    search_fields = ['baslik', 'aciklama', 'proje__ad']
    date_hierarchy = 'son_tarih'

@admin.register(Ilerleme)
class IlerlemeAdmin(admin.ModelAdmin):
    """İlerleme yönetimi"""
    list_display = ['proje', 'kaydeden', 'tarih']
    list_filter = ['proje__daire_baskanligi', 'proje__sube_mudurlugu']
    search_fields = ['aciklama', 'proje__ad']
    date_hierarchy = 'tarih'

@admin.register(Dosya)
class DosyaAdmin(admin.ModelAdmin):
    """Dosya yönetimi"""
    list_display = ['ilerleme', 'yukleme_tarihi']
    list_filter = ['yukleme_tarihi']
    date_hierarchy = 'yukleme_tarihi'

@admin.register(Fotograf)
class FotografAdmin(admin.ModelAdmin):
    """Fotoğraf yönetimi"""
    list_display = ['ilerleme', 'yukleme_tarihi']
    list_filter = ['yukleme_tarihi']
    date_hierarchy = 'yukleme_tarihi'
