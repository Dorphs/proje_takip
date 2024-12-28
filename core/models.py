from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class DaireBaskanligi(models.Model):
    """Daire Başkanlığı modeli"""
    ad = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.ad
    
    class Meta:
        verbose_name = "Daire Başkanlığı"
        verbose_name_plural = "Daire Başkanlıkları"
        ordering = ['ad']

class SubeMudurlugu(models.Model):
    """Şube Müdürlüğü modeli"""
    ad = models.CharField(max_length=100)
    daire_baskanligi = models.ForeignKey(DaireBaskanligi, on_delete=models.CASCADE, related_name='sube_mudurlukleri')
    
    def __str__(self):
        return f"{self.daire_baskanligi.ad} - {self.ad}"
    
    class Meta:
        verbose_name = "Şube Müdürlüğü"
        verbose_name_plural = "Şube Müdürlükleri"
        ordering = ['daire_baskanligi__ad', 'ad']
        unique_together = ['daire_baskanligi', 'ad']

class CustomUser(AbstractUser):
    """Özelleştirilmiş kullanıcı modeli"""
    daire_baskanligi = models.CharField(max_length=100, blank=True, null=True, verbose_name="Daire Başkanlığı")
    sube_mudurlugu = models.CharField(max_length=100, blank=True, null=True, verbose_name="Şube Müdürlüğü")
    unvan = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ünvan")
    yonetici = models.BooleanField(default=False, verbose_name="Yönetici")

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"
        ordering = ['first_name', 'last_name']

    def __str__(self):
        full_name = self.get_full_name()
        if full_name:
            return f"{full_name} ({self.username})"
        return self.username

    def is_yonetici(self):
        """Kullanıcının yönetici olup olmadığını kontrol eder"""
        return self.yonetici or self.is_superuser

    def can_manage_project(self, proje):
        """Kullanıcının projeyi yönetip yönetemeyeceğini kontrol eder"""
        if self.is_superuser:
            return True
        if self.is_yonetici():
            return (self.daire_baskanligi == proje.daire_baskanligi or 
                    self.sube_mudurlugu == proje.sube_mudurlugu)
        return False

    def can_manage_task(self, gorev):
        """Kullanıcının görevi yönetip yönetemeyeceğini kontrol eder"""
        if self.is_superuser:
            return True
        if self.is_yonetici():
            return self.can_manage_project(gorev.proje)
        return self == gorev.atanan or self == gorev.olusturan

class Proje(models.Model):
    """Proje modeli"""
    DURUM_CHOICES = [
        ('BASLAMADI', 'Başlamadı'),
        ('DEVAM', 'Devam Ediyor'),
        ('TAMAMLANDI', 'Tamamlandı'),
    ]

    ad = models.CharField(max_length=200, verbose_name="Proje Adı")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    daire_baskanligi = models.CharField(max_length=100, verbose_name="Daire Başkanlığı", blank=True, null=True)
    sube_mudurlugu = models.CharField(max_length=100, verbose_name="Şube Müdürlüğü", blank=True, null=True)
    baslama_tarihi = models.DateField(verbose_name="Başlama Tarihi")
    bitis_tarihi = models.DateField(verbose_name="Bitiş Tarihi")
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='BASLAMADI', verbose_name="Durum")
    olusturan = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='olusturulan_projeler', verbose_name="Oluşturan")
    atanan_kisiler = models.ManyToManyField(CustomUser, related_name='atanan_projeler', blank=True, verbose_name="Atanan Kişiler")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncelleme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")

    def __str__(self):
        return f"{self.ad} ({self.get_durum_display()})"
    
    class Meta:
        verbose_name = "Proje"
        verbose_name_plural = "Projeler"
        ordering = ['-olusturulma_tarihi']

    def get_tamamlanma_yuzdesi(self):
        """Projenin tamamlanma yüzdesini hesaplar"""
        if not self.gorevler.exists():
            return 0
        tamamlanan = self.gorevler.filter(durum='TAMAMLANDI').count()
        toplam = self.gorevler.count()
        return int((tamamlanan / toplam) * 100)

class Gorev(models.Model):
    """Görev modeli"""
    DURUM_CHOICES = [
        ('BASLAMADI', 'Başlamadı'),
        ('DEVAM', 'Devam Ediyor'),
        ('TAMAMLANDI', 'Tamamlandı'),
    ]

    proje = models.ForeignKey(Proje, on_delete=models.CASCADE, related_name='gorevler', verbose_name="Proje")
    baslik = models.CharField(max_length=200, verbose_name="Başlık")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    atanan = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='atanan_gorevler', verbose_name="Atanan Kişi")
    son_tarih = models.DateField(null=True, blank=True, verbose_name="Son Tarih")
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='BASLAMADI', verbose_name="Durum")
    olusturan = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='olusturulan_gorevler', verbose_name="Oluşturan")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncelleme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")

    def __str__(self):
        return f"{self.baslik} ({self.get_durum_display()})"
    
    class Meta:
        verbose_name = "Görev"
        verbose_name_plural = "Görevler"
        ordering = ['-olusturulma_tarihi']

    def gecikti_mi(self):
        """Görevin gecikip gecikmediğini kontrol eder"""
        if self.son_tarih and self.durum != 'TAMAMLANDI':
            return self.son_tarih < timezone.now().date()
        return False

class Ilerleme(models.Model):
    """İlerleme modeli"""
    proje = models.ForeignKey(Proje, on_delete=models.CASCADE, related_name='ilerlemeler', null=True, blank=True)
    gorev = models.ForeignKey(Gorev, on_delete=models.CASCADE, related_name='ilerlemeler', null=True, blank=True)
    aciklama = models.TextField(verbose_name="Açıklama")
    kaydeden = models.ForeignKey(CustomUser, on_delete=models.PROTECT, verbose_name="Kaydeden")
    tarih = models.DateTimeField(auto_now_add=True, verbose_name="Tarih")
    
    def __str__(self):
        return f"{self.tarih.strftime('%Y-%m-%d %H:%M')} - {self.kaydeden.get_full_name()}"
    
    class Meta:
        verbose_name = "İlerleme"
        verbose_name_plural = "İlerlemeler"
        ordering = ['-tarih']

    def save(self, *args, **kwargs):
        """İlerleme kaydedildiğinde proje veya görev güncelleme tarihini günceller"""
        super().save(*args, **kwargs)
        if self.proje:
            self.proje.guncelleme_tarihi = timezone.now()
            self.proje.save(update_fields=['guncelleme_tarihi'])
        if self.gorev:
            self.gorev.guncelleme_tarihi = timezone.now()
            self.gorev.save(update_fields=['guncelleme_tarihi'])

class Dosya(models.Model):
    """Dosya modeli"""
    ilerleme = models.ForeignKey(Ilerleme, on_delete=models.CASCADE, related_name='dosyalar', verbose_name="İlerleme")
    dosya = models.FileField(upload_to='belgeler/', verbose_name="Dosya")
    yukleme_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Yükleme Tarihi")
    
    def __str__(self):
        return f"{self.ilerleme.proje.ad if self.ilerleme.proje else self.ilerleme.gorev.proje.ad} - {self.dosya.name}"
    
    class Meta:
        verbose_name = "Dosya"
        verbose_name_plural = "Dosyalar"
        ordering = ['-yukleme_tarihi']

class Fotograf(models.Model):
    """Fotoğraf modeli"""
    ilerleme = models.ForeignKey(Ilerleme, on_delete=models.CASCADE, related_name='fotograflar', verbose_name="İlerleme")
    fotograf = models.ImageField(upload_to='fotograflar/', verbose_name="Fotoğraf")
    yukleme_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Yükleme Tarihi")
    
    def __str__(self):
        return f"{self.ilerleme.proje.ad if self.ilerleme.proje else self.ilerleme.gorev.proje.ad} - {self.fotograf.name}"
    
    class Meta:
        verbose_name = "Fotoğraf"
        verbose_name_plural = "Fotoğraflar"
        ordering = ['-yukleme_tarihi']
