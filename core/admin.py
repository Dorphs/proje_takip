from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, DaireBaskanligi, SubeMudurlugu,
    Proje, Gorev, Ilerleme, Dosya, Fotograf
)

# CustomUser için özel admin sınıfı
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Özel kullanıcı yönetimi"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'unvan', 'daire_baskanligi', 'sube_mudurlugu')
    list_filter = ('unvan', 'daire_baskanligi', 'sube_mudurlugu')
    fieldsets = UserAdmin.fieldsets + (
        ('Görev Bilgileri', {'fields': ('unvan', 'daire_baskanligi', 'sube_mudurlugu')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Görev Bilgileri', {'fields': ('unvan', 'daire_baskanligi', 'sube_mudurlugu')}),
    )

# Daire Başkanlığı admin sınıfı
@admin.register(DaireBaskanligi)
class DaireBaskanligiAdmin(admin.ModelAdmin):
    """Daire başkanlığı yönetimi"""
    list_display = ('ad',)
    search_fields = ('ad',)

# Şube Müdürlüğü admin sınıfı
@admin.register(SubeMudurlugu)
class SubeMudurluguAdmin(admin.ModelAdmin):
    """Şube müdürlüğü yönetimi"""
    list_display = ('ad', 'daire_baskanligi')
    list_filter = ('daire_baskanligi',)
    search_fields = ('ad', 'daire_baskanligi__ad')

# Proje için inline görev gösterimi
class GorevInline(admin.TabularInline):
    model = Gorev
    extra = 1

# Proje admin sınıfı
@admin.register(Proje)
class ProjeAdmin(admin.ModelAdmin):
    """Proje yönetimi"""
    list_display = ('ad', 'durum', 'oncelik', 'baslama_tarihi', 'bitis_tarihi', 'olusturan')
    list_filter = ('durum', 'oncelik', 'daire_baskanliklari', 'sube_mudurlukleri')
    search_fields = ('ad', 'aciklama')
    filter_horizontal = ('daire_baskanliklari', 'sube_mudurlukleri')
    date_hierarchy = 'olusturulma_tarihi'

# Görev admin sınıfı
@admin.register(Gorev)
class GorevAdmin(admin.ModelAdmin):
    """Görev yönetimi"""
    list_display = ('ad', 'proje', 'sorumlu', 'durum', 'oncelik', 'baslama_tarihi', 'bitis_tarihi')
    list_filter = ('durum', 'oncelik', 'proje')
    search_fields = ('ad', 'aciklama', 'proje__ad')
    date_hierarchy = 'olusturulma_tarihi'

# İlerleme için inline dosya ve fotoğraf gösterimi
class DosyaInline(admin.TabularInline):
    model = Dosya
    extra = 1

class FotografInline(admin.TabularInline):
    model = Fotograf
    extra = 1

# İlerleme admin sınıfı
@admin.register(Ilerleme)
class IlerlemeAdmin(admin.ModelAdmin):
    """İlerleme yönetimi"""
    list_display = ('proje', 'kaydeden', 'tarih')
    list_filter = ('proje', 'kaydeden')
    search_fields = ('aciklama', 'proje__ad')
    date_hierarchy = 'tarih'

# Dosya admin sınıfı
@admin.register(Dosya)
class DosyaAdmin(admin.ModelAdmin):
    """Dosya yönetimi"""
    list_display = ('ilerleme', 'dosya', 'yukleme_tarihi')
    list_filter = ('ilerleme__proje',)
    search_fields = ('ilerleme__proje__ad',)
    date_hierarchy = 'yukleme_tarihi'

# Fotoğraf admin sınıfı
@admin.register(Fotograf)
class FotografAdmin(admin.ModelAdmin):
    """Fotoğraf yönetimi"""
    list_display = ('ilerleme', 'fotograf', 'yukleme_tarihi')
    list_filter = ('ilerleme__proje',)
    search_fields = ('ilerleme__proje__ad',)
    date_hierarchy = 'yukleme_tarihi'
