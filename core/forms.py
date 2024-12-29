from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db.models import Q
from .models import CustomUser, Proje, Gorev, Ilerleme, SubeMudurlugu, DaireBaskanligi

class CustomUserCreationForm(UserCreationForm):
    """Kullanıcı oluşturma formu"""
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'daire_baskanligi', 'sube_mudurlugu', 'unvan')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sube_mudurlugu'].queryset = SubeMudurlugu.objects.none()
        
        if 'daire_baskanligi' in self.data:
            try:
                daire_id = int(self.data.get('daire_baskanligi'))
                self.fields['sube_mudurlugu'].queryset = SubeMudurlugu.objects.filter(daire_baskanligi_id=daire_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.daire_baskanligi:
            self.fields['sube_mudurlugu'].queryset = self.instance.daire_baskanligi.sube_mudurlukleri.all()

class CustomUserChangeForm(UserChangeForm):
    """Kullanıcı düzenleme formu"""
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'daire_baskanligi', 'sube_mudurlugu', 'unvan')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sube_mudurlugu'].queryset = SubeMudurlugu.objects.none()
        
        if 'daire_baskanligi' in self.data:
            try:
                daire_id = int(self.data.get('daire_baskanligi'))
                self.fields['sube_mudurlugu'].queryset = SubeMudurlugu.objects.filter(daire_baskanligi_id=daire_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.daire_baskanligi:
            self.fields['sube_mudurlugu'].queryset = self.instance.daire_baskanligi.sube_mudurlukleri.all()

class ProjeForm(forms.ModelForm):
    """Proje formu"""
    class Meta:
        model = Proje
        fields = ['ad', 'daire_baskanligi', 'sube_mudurlugu', 'baslama_tarihi', 
                 'bitis_tarihi', 'durum', 'oncelik', 'aciklama']
        widgets = {
            'ad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Proje adını girin'
            }),
            'daire_baskanligi': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Daire başkanlığı seçin'
            }),
            'sube_mudurlugu': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Şube müdürlüğü seçin'
            }),
            'baslama_tarihi': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'bitis_tarihi': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'durum': forms.Select(attrs={
                'class': 'form-select'
            }),
            'oncelik': forms.Select(attrs={
                'class': 'form-select'
            }),
            'aciklama': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Proje açıklamasını girin'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        # Şube müdürlüğü queryset'ini başlangıçta boşalt
        self.fields['sube_mudurlugu'].queryset = SubeMudurlugu.objects.none()

        # Eğer instance varsa veya POST isteği ise
        if instance or (args and args[0] and 'daire_baskanligi' in args[0]):
            try:
                daire_id = instance.daire_baskanligi_id if instance else int(args[0]['daire_baskanligi'])
                self.fields['sube_mudurlugu'].queryset = SubeMudurlugu.objects.filter(
                    daire_baskanligi_id=daire_id
                )
            except (ValueError, TypeError, KeyError):
                pass

class GorevForm(forms.ModelForm):
    """Görev formu"""
    daire_baskanligi = forms.ModelChoiceField(
        queryset=DaireBaskanligi.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Daire Başkanlığı"
    )
    sube_mudurlugu = forms.ModelChoiceField(
        queryset=SubeMudurlugu.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'disabled': 'disabled'}),
        label="Şube Müdürlüğü"
    )

    class Meta:
        model = Gorev
        fields = ['baslik', 'aciklama', 'son_tarih', 'durum', 'atanan']
        widgets = {
            'baslik': forms.TextInput(attrs={'class': 'form-control'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control'}),
            'son_tarih': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'durum': forms.Select(attrs={'class': 'form-select'}),
            'atanan': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, proje=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if proje:
            # Projenin daire başkanlığı ve şube müdürlüğüne göre kullanıcıları filtrele
            self.fields['atanan'].queryset = CustomUser.objects.filter(
                daire_baskanligi=proje.daire_baskanligi,
                sube_mudurlugu=proje.sube_mudurlugu
            )
            # Daire başkanlığı ve şube müdürlüğü alanlarını otomatik doldur
            self.fields['daire_baskanligi'].initial = proje.daire_baskanligi
            self.fields['sube_mudurlugu'].initial = proje.sube_mudurlugu
            self.fields['sube_mudurlugu'].queryset = SubeMudurlugu.objects.filter(
                daire_baskanligi=proje.daire_baskanligi
            )

class IlerlemeForm(forms.ModelForm):
    """İlerleme formu"""
    class Meta:
        model = Ilerleme
        fields = ['aciklama']
        widgets = {
            'aciklama': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
