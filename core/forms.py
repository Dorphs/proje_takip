from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Proje, Gorev, Ilerleme

class CustomUserCreationForm(UserCreationForm):
    """Özel kullanıcı oluşturma formu"""
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name', 'unvan', 'daire_baskanligi', 'sube_mudurlugu')

class ProjeForm(forms.ModelForm):
    """Proje formu"""
    class Meta:
        model = Proje
        fields = ['ad', 'aciklama', 'daire_baskanliklari', 'sube_mudurlukleri', 
                 'baslama_tarihi', 'bitis_tarihi', 'oncelik', 'durum']
        widgets = {
            'baslama_tarihi': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'bitis_tarihi': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'daire_baskanliklari': forms.CheckboxSelectMultiple(),
            'sube_mudurlukleri': forms.CheckboxSelectMultiple(),
        }

class GorevForm(forms.ModelForm):
    """Görev formu"""
    class Meta:
        model = Gorev
        fields = ['ad', 'aciklama', 'sorumlu', 'baslama_tarihi', 'bitis_tarihi', 'oncelik', 'durum']
        widgets = {
            'baslama_tarihi': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'bitis_tarihi': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sorumlu seçimini personel ünvanına sahip kullanıcılarla sınırla
        self.fields['sorumlu'].queryset = CustomUser.objects.filter(unvan='P')

class IlerlemeForm(forms.ModelForm):
    """İlerleme formu"""
    dosyalar = forms.FileField(required=False)
    fotograflar = forms.ImageField(required=False)
    
    class Meta:
        model = Ilerleme
        fields = ['aciklama']
