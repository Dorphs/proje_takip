from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db.models import Q
from .models import CustomUser, Proje, Gorev, Ilerleme

class CustomUserCreationForm(UserCreationForm):
    """Kullanıcı oluşturma formu"""
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'daire_baskanligi', 'sube_mudurlugu', 'unvan', 'yonetici')

class CustomUserChangeForm(UserChangeForm):
    """Kullanıcı düzenleme formu"""
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'daire_baskanligi', 'sube_mudurlugu', 'unvan', 'yonetici')

class ProjeForm(forms.ModelForm):
    """Proje formu"""
    class Meta:
        model = Proje
        fields = ['ad', 'aciklama', 'daire_baskanligi', 'sube_mudurlugu', 'baslama_tarihi', 'bitis_tarihi', 'durum', 'atanan_kisiler']
        widgets = {
            'baslama_tarihi': forms.DateInput(attrs={'type': 'date'}),
            'bitis_tarihi': forms.DateInput(attrs={'type': 'date'}),
            'atanan_kisiler': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'durum': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            if not user.is_superuser:
                # Yönetici olmayan kullanıcılar sadece kendi daire/müdürlüklerindeki kişileri atayabilir
                self.fields['daire_baskanligi'].initial = user.daire_baskanligi
                self.fields['daire_baskanligi'].disabled = True
                self.fields['sube_mudurlugu'].initial = user.sube_mudurlugu
                self.fields['sube_mudurlugu'].disabled = True
                self.fields['atanan_kisiler'].queryset = CustomUser.objects.filter(
                    Q(daire_baskanligi=user.daire_baskanligi) &
                    Q(sube_mudurlugu=user.sube_mudurlugu)
                )
            else:
                # Süper kullanıcı tüm kullanıcıları görebilir
                self.fields['atanan_kisiler'].queryset = CustomUser.objects.all()

class GorevForm(forms.ModelForm):
    """Görev formu"""
    class Meta:
        model = Gorev
        fields = ['baslik', 'aciklama', 'atanan', 'son_tarih', 'durum']
        widgets = {
            'son_tarih': forms.DateInput(attrs={'type': 'date'}),
            'atanan': forms.Select(attrs={'class': 'form-select'}),
            'durum': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, proje=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if proje and user:
            if user.is_superuser:
                # Süper kullanıcı tüm kullanıcıları görebilir
                self.fields['atanan'].queryset = CustomUser.objects.all()
            elif user.can_manage_project(proje):
                # Yöneticiler kendi birimlerindeki kullanıcıları görebilir
                self.fields['atanan'].queryset = CustomUser.objects.filter(
                    Q(daire_baskanligi=proje.daire_baskanligi) &
                    Q(sube_mudurlugu=proje.sube_mudurlugu)
                )
            else:
                # Normal kullanıcılar sadece kendilerini seçebilir
                self.fields['atanan'].queryset = CustomUser.objects.filter(id=user.id)

class IlerlemeForm(forms.ModelForm):
    """İlerleme formu"""
    class Meta:
        model = Ilerleme
        fields = ['aciklama']
        widgets = {
            'aciklama': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
