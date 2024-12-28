from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class DaireBaskanligi(models.Model):
    """Daire Başkanlığı modeli"""
    ad = models.CharField(max_length=100)
    
    def __str__(self):
        return self.ad
    
    class Meta:
        verbose_name = "Daire Başkanlığı"
        verbose_name_plural = "Daire Başkanlıkları"

class SubeMudurlugu(models.Model):
    """Şube Müdürlüğü modeli"""
    ad = models.CharField(max_length=100)
    daire_baskanligi = models.ForeignKey(DaireBaskanligi, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.daire_baskanligi.ad} - {self.ad}"
    
    class Meta:
        verbose_name = "Şube Müdürlüğü"
        verbose_name_plural = "Şube Müdürlükleri"

class CustomUser(AbstractUser):
    """Özel kullanıcı modeli"""
    UNVAN_CHOICES = [
        ('GM', 'Genel Müdür'),
        ('DB', 'Daire Başkanı'),
        ('SM', 'Şube Müdürü'),
        ('P', 'Personel'),
    ]
    
    unvan = models.CharField(max_length=2, choices=UNVAN_CHOICES)
    daire_baskanligi = models.ForeignKey(DaireBaskanligi, on_delete=models.SET_NULL, null=True, blank=True)
    sube_mudurlugu = models.ForeignKey(SubeMudurlugu, on_delete=models.SET_NULL, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.unvan == 'GM':
            self.daire_baskanligi = None
            self.sube_mudurlugu = None
        elif self.unvan == 'DB':
            self.sube_mudurlugu = None
        super().save(*args, **kwargs)

class Proje(models.Model):
    """Proje modeli"""
    DURUM_CHOICES = [
        ('Başlamadı', 'Başlamadı'),
        ('Devam Ediyor', 'Devam Ediyor'),
        ('Tamamlandı', 'Tamamlandı'),
    ]
    
    ONCELIK_CHOICES = [
        ('Y', 'Yüksek'),
        ('O', 'Orta'),
        ('D', 'Düşük'),
    ]
    
    ad = models.CharField(max_length=200)
    aciklama = models.TextField()
    daire_baskanliklari = models.ManyToManyField(DaireBaskanligi, related_name='projeler')
    sube_mudurlukleri = models.ManyToManyField(SubeMudurlugu, related_name='projeler')
    baslama_tarihi = models.DateTimeField(default=timezone.now)
    bitis_tarihi = models.DateTimeField()
    oncelik = models.CharField(max_length=1, choices=ONCELIK_CHOICES)
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='Başlamadı')
    olusturan = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.ad
    
    class Meta:
        verbose_name = "Proje"
        verbose_name_plural = "Projeler"
    
    @property
    def ilerleme_yuzdesi(self):
        """Projenin ilerleme yüzdesini hesaplar"""
        tamamlanan_gorevler = self.gorevler.filter(durum='Tamamlandı').count()
        toplam_gorevler = self.gorevler.count()
        if toplam_gorevler == 0:
            return 0
        return int((tamamlanan_gorevler / toplam_gorevler) * 100)

class Gorev(models.Model):
    """Görev modeli"""
    DURUM_CHOICES = [
        ('Başlamadı', 'Başlamadı'),
        ('Devam Ediyor', 'Devam Ediyor'),
        ('Tamamlandı', 'Tamamlandı'),
    ]
    
    ONCELIK_CHOICES = [
        ('Y', 'Yüksek'),
        ('O', 'Orta'),
        ('D', 'Düşük'),
    ]
    
    proje = models.ForeignKey(Proje, on_delete=models.CASCADE, related_name='gorevler')
    ad = models.CharField(max_length=200)
    aciklama = models.TextField()
    sorumlu = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='sorumlu_gorevler')
    baslama_tarihi = models.DateTimeField(default=timezone.now)
    bitis_tarihi = models.DateTimeField()
    oncelik = models.CharField(max_length=1, choices=ONCELIK_CHOICES)
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='Başlamadı')
    olusturan = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='olusturulan_gorevler')
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.proje.ad} - {self.ad}"
    
    class Meta:
        verbose_name = "Görev"
        verbose_name_plural = "Görevler"

class Ilerleme(models.Model):
    """İlerleme modeli"""
    proje = models.ForeignKey(Proje, on_delete=models.CASCADE, related_name='ilerlemeler', null=True, blank=True)
    gorev = models.ForeignKey(Gorev, on_delete=models.CASCADE, related_name='ilerlemeler', null=True, blank=True)
    aciklama = models.TextField()
    kaydeden = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    tarih = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.tarih.strftime('%Y-%m-%d %H:%M')} - {self.kaydeden.get_full_name()}"
    
    class Meta:
        verbose_name = "İlerleme"
        verbose_name_plural = "İlerlemeler"
        ordering = ['-tarih']

class Dosya(models.Model):
    """Dosya modeli"""
    ilerleme = models.ForeignKey(Ilerleme, on_delete=models.CASCADE, related_name='dosyalar')
    dosya = models.FileField(upload_to='belgeler/')
    yukleme_tarihi = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.ilerleme.proje.ad} - {self.dosya.name}"
    
    class Meta:
        verbose_name = "Dosya"
        verbose_name_plural = "Dosyalar"

class Fotograf(models.Model):
    """Fotoğraf modeli"""
    ilerleme = models.ForeignKey(Ilerleme, on_delete=models.CASCADE, related_name='fotograflar')
    fotograf = models.ImageField(upload_to='fotograflar/')
    yukleme_tarihi = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.ilerleme.proje.ad} - {self.fotograf.name}"
    
    class Meta:
        verbose_name = "Fotoğraf"
        verbose_name_plural = "Fotoğraflar"
