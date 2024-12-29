from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Proje, Gorev, Ilerleme, DaireBaskanligi, SubeMudurlugu
from .forms import CustomUserCreationForm, CustomUserChangeForm

# CustomUser için özel admin sınıfı
class CustomUserAdmin(UserAdmin):
    """Özelleştirilmiş kullanıcı yönetimi"""
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'daire_baskanligi', 'sube_mudurlugu']
    list_filter = ['role', 'daire_baskanligi', 'sube_mudurlugu', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'email')}),
        ('Departman Bilgileri', {'fields': ('role', 'daire_baskanligi', 'sube_mudurlugu', 'unvan')}),
        ('İzinler', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'daire_baskanligi', 'sube_mudurlugu', 'unvan'),
        }),
    )
    search_fields = ['username', 'first_name', 'last_name', 'email', 'daire_baskanligi', 'sube_mudurlugu']
    ordering = ['username']

# Proje admin sınıfı
class ProjeAdmin(admin.ModelAdmin):
    """Proje yönetimi"""
    list_display = ['ad', 'daire_baskanligi', 'sube_mudurlugu', 'durum', 'baslama_tarihi', 'bitis_tarihi']
    list_filter = ['durum', 'daire_baskanligi', 'sube_mudurlugu']
    search_fields = ['ad', 'aciklama']
    filter_horizontal = ['atanan_kisiler']
    date_hierarchy = 'baslama_tarihi'

# Görev admin sınıfı
class GorevAdmin(admin.ModelAdmin):
    """Görev yönetimi"""
    list_display = ['baslik', 'proje', 'atanan', 'son_tarih', 'durum']
    list_filter = ['durum', 'proje__daire_baskanligi', 'proje__sube_mudurlugu']
    search_fields = ['baslik', 'aciklama', 'proje__ad']
    date_hierarchy = 'son_tarih'

# İlerleme admin sınıfı
class IlerlemeAdmin(admin.ModelAdmin):
    """İlerleme yönetimi"""
    list_display = ['proje', 'kaydeden', 'tarih']
    list_filter = ['proje__daire_baskanligi', 'proje__sube_mudurlugu']
    search_fields = ['aciklama', 'proje__ad']
    date_hierarchy = 'tarih'

class SubeMudurluguInline(admin.TabularInline):
    model = SubeMudurlugu
    extra = 1

class DaireBaskanligiAdmin(admin.ModelAdmin):
    list_display = ('ad',)
    inlines = [SubeMudurluguInline]

class SubeMudurluguAdmin(admin.ModelAdmin):
    list_display = ('ad', 'daire_baskanligi')
    list_filter = ('daire_baskanligi',)

# Admin sayfasına modelleri kaydet
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(DaireBaskanligi, DaireBaskanligiAdmin)
admin.site.register(SubeMudurlugu, SubeMudurluguAdmin)
admin.site.register(Proje, ProjeAdmin)
admin.site.register(Gorev, GorevAdmin)
admin.site.register(Ilerleme, IlerlemeAdmin)
