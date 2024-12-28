from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from django.contrib import messages
from .forms import ProjeForm, GorevForm, IlerlemeForm, CustomUserCreationForm
from .models import Proje, Gorev, Ilerleme, CustomUser
from django.utils import timezone

@login_required
def dashboard(request):
    """Dashboard görünümü"""
    user = request.user
    
    # Proje filtreleme
    if user.is_superuser:
        projeler = Proje.objects.all()
        gorevler = Gorev.objects.all()
    elif user.is_yonetici():
        # Yöneticiler kendi birimlerindeki tüm projeleri görebilir
        projeler = Proje.objects.filter(
            Q(daire_baskanligi=user.daire_baskanligi) |
            Q(sube_mudurlugu=user.sube_mudurlugu)
        )
        gorevler = Gorev.objects.filter(
            Q(proje__daire_baskanligi=user.daire_baskanligi) |
            Q(proje__sube_mudurlugu=user.sube_mudurlugu)
        )
    else:
        # Normal kullanıcılar atandıkları projeleri ve görevleri görebilir
        projeler = Proje.objects.filter(
            Q(atanan_kisiler=user) |
            Q(gorevler__atanan=user) |
            Q(olusturan=user)
        ).distinct()
        gorevler = Gorev.objects.filter(
            Q(atanan=user) |
            Q(olusturan=user)
        ).distinct()
    
    # İstatistikleri hesapla
    context = {
        'projeler': projeler.order_by('-baslama_tarihi')[:5],  # Son 5 proje
        'bekleyen_projeler': projeler.filter(durum='BASLAMADI').count(),
        'devam_eden_projeler': projeler.filter(durum='DEVAM').count(),
        'tamamlanan_projeler': projeler.filter(durum='TAMAMLANDI').count(),
        'toplam_proje': projeler.count(),
        'bekleyen_gorevler': gorevler.filter(durum='BASLAMADI').count(),
        'devam_eden_gorevler': gorevler.filter(durum='DEVAM').count(),
        'tamamlanan_gorevler': gorevler.filter(durum='TAMAMLANDI').count(),
        'toplam_gorev': gorevler.count(),
        'geciken_gorevler': gorevler.filter(
            Q(son_tarih__lt=timezone.now().date()) &
            ~Q(durum='TAMAMLANDI')
        ).count(),
        'gorevler': gorevler.order_by('-olusturulma_tarihi')[:5]  # Son 5 görev
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def proje_listesi(request):
    """Proje listesi görünümü"""
    user = request.user
    search_query = request.GET.get('search', '')
    durum_filter = request.GET.get('durum', '')
    
    if user.is_superuser:
        projeler = Proje.objects.all()
    elif user.is_yonetici():
        projeler = Proje.objects.filter(
            Q(daire_baskanligi=user.daire_baskanligi) |
            Q(sube_mudurlugu=user.sube_mudurlugu)
        )
    else:
        projeler = Proje.objects.filter(
            Q(atanan_kisiler=user) |
            Q(gorevler__atanan=user)
        ).distinct()
    
    if search_query:
        projeler = projeler.filter(
            Q(ad__icontains=search_query) |
            Q(aciklama__icontains=search_query) |
            Q(daire_baskanligi__icontains=search_query) |
            Q(sube_mudurlugu__icontains=search_query)
        )
    if durum_filter:
        projeler = projeler.filter(durum=durum_filter)
    
    context = {
        'projeler': projeler,
        'search_query': search_query,
        'durum_filter': durum_filter,
    }
    return render(request, 'core/proje_listesi.html', context)

@login_required
def proje_detay(request, pk):
    """Proje detay görünümü"""
    proje = get_object_or_404(Proje, pk=pk)
    gorevler = proje.gorevler.all().order_by('-olusturulma_tarihi')
    ilerlemeler = proje.ilerlemeler.all().order_by('-tarih')
    
    context = {
        'proje': proje,
        'gorevler': gorevler,
        'ilerlemeler': ilerlemeler,
        'now': timezone.now(),
    }
    return render(request, 'core/proje_detay.html', context)

@login_required
def proje_ekle(request):
    """Proje ekleme görünümü"""
    if not (request.user.is_superuser or request.user.is_yonetici()):
        messages.error(request, 'Bu işlem için yetkiniz bulunmamaktadır.')
        return redirect('proje_listesi')
    
    if request.method == 'POST':
        form = ProjeForm(request.POST, user=request.user)
        if form.is_valid():
            proje = form.save(commit=False)
            proje.olusturan = request.user
            if not request.user.is_superuser:
                proje.daire_baskanligi = request.user.daire_baskanligi
                proje.sube_mudurlugu = request.user.sube_mudurlugu
            proje.save()
            form.save_m2m()
            messages.success(request, 'Proje başarıyla oluşturuldu.')
            return redirect('proje_detay', pk=proje.pk)
    else:
        form = ProjeForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Yeni Proje Oluştur'
    }
    return render(request, 'core/proje_form.html', context)

@login_required
def proje_duzenle(request, pk):
    """Proje düzenleme görünümü"""
    proje = get_object_or_404(Proje, pk=pk)
    
    if not (request.user.is_superuser or request.user.can_manage_project(proje)):
        messages.error(request, 'Bu işlem için yetkiniz bulunmamaktadır.')
        return redirect('proje_listesi')
    
    if request.method == 'POST':
        form = ProjeForm(request.POST, instance=proje, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proje başarıyla güncellendi.')
            return redirect('proje_detay', pk=proje.pk)
    else:
        form = ProjeForm(instance=proje, user=request.user)
    
    context = {
        'form': form,
        'title': 'Proje Düzenle'
    }
    return render(request, 'core/proje_form.html', context)

@login_required
def gorev_ekle(request, proje_pk):
    """Görev ekleme görünümü"""
    proje = get_object_or_404(Proje, pk=proje_pk)
    
    if not (request.user.is_superuser or request.user.can_manage_project(proje) or request.user in proje.atanan_kisiler.all()):
        messages.error(request, 'Bu işlem için yetkiniz bulunmamaktadır.')
        return redirect('proje_detay', pk=proje_pk)
    
    if request.method == 'POST':
        form = GorevForm(request.POST, proje=proje, user=request.user)
        if form.is_valid():
            gorev = form.save(commit=False)
            gorev.proje = proje
            gorev.olusturan = request.user
            gorev.save()
            messages.success(request, 'Görev başarıyla oluşturuldu.')
            return redirect('proje_detay', pk=proje_pk)
    else:
        form = GorevForm(proje=proje, user=request.user)
    
    context = {
        'form': form,
        'proje': proje,
        'title': 'Yeni Görev Oluştur'
    }
    return render(request, 'core/gorev_form.html', context)

@login_required
def gorev_duzenle(request, pk):
    """Görev düzenleme görünümü"""
    gorev = get_object_or_404(Gorev, pk=pk)
    proje = gorev.proje
    
    if not (request.user.is_superuser or request.user.can_manage_project(proje) or request.user == gorev.atanan or request.user == gorev.olusturan):
        messages.error(request, 'Bu işlem için yetkiniz bulunmamaktadır.')
        return redirect('proje_detay', pk=proje.pk)
    
    if request.method == 'POST':
        form = GorevForm(request.POST, instance=gorev, proje=proje, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Görev başarıyla güncellendi.')
            return redirect('proje_detay', pk=proje.pk)
    else:
        form = GorevForm(instance=gorev, proje=proje, user=request.user)
    
    context = {
        'form': form,
        'gorev': gorev,
        'title': 'Görev Düzenle'
    }
    return render(request, 'core/gorev_form.html', context)

@login_required
def gorev_sil(request, pk):
    """Görev silme görünümü"""
    gorev = get_object_or_404(Gorev, pk=pk)
    proje = gorev.proje
    
    if not (request.user.is_superuser or request.user.can_manage_project(proje) or request.user == gorev.olusturan):
        messages.error(request, 'Bu işlem için yetkiniz bulunmamaktadır.')
        return redirect('proje_detay', pk=proje.pk)
    
    if request.method == 'POST':
        gorev.delete()
        messages.success(request, 'Görev başarıyla silindi.')
        return redirect('proje_detay', pk=proje.pk)
    
    context = {
        'gorev': gorev,
    }
    return render(request, 'core/gorev_sil.html', context)

@login_required
def ilerleme_ekle(request, pk):
    """İlerleme ekleme görünümü"""
    proje = get_object_or_404(Proje, pk=pk)
    
    if not (request.user.is_superuser or request.user.can_manage_project(proje) or 
            request.user in proje.atanan_kisiler.all() or 
            proje.gorevler.filter(atanan=request.user).exists()):
        messages.error(request, 'Bu işlem için yetkiniz bulunmamaktadır.')
        return redirect('proje_detay', pk=pk)
    
    if request.method == 'POST':
        form = IlerlemeForm(request.POST)
        if form.is_valid():
            ilerleme = form.save(commit=False)
            ilerleme.proje = proje
            ilerleme.kaydeden = request.user
            ilerleme.save()
            messages.success(request, 'İlerleme kaydı başarıyla eklendi.')
            return redirect('proje_detay', pk=pk)
    else:
        form = IlerlemeForm()
    
    context = {
        'form': form,
        'proje': proje,
        'title': 'İlerleme Ekle'
    }
    return render(request, 'core/ilerleme_form.html', context)

@login_required
def proje_sil(request, pk):
    """Proje silme görünümü"""
    proje = get_object_or_404(Proje, pk=pk)
    
    if not (request.user.is_superuser or request.user.can_manage_project(proje)):
        messages.error(request, 'Bu işlem için yetkiniz bulunmamaktadır.')
        return redirect('proje_detay', pk=pk)
    
    if request.method == 'POST':
        proje.delete()
        messages.success(request, 'Proje başarıyla silindi.')
        return redirect('proje_listesi')
    
    context = {
        'proje': proje,
    }
    return render(request, 'core/proje_sil.html', context)

@login_required
def rapor_listesi(request):
    """Rapor listesi görünümü"""
    user = request.user
    
    if not (user.is_superuser or user.is_yonetici()):
        messages.error(request, 'Bu sayfaya erişim yetkiniz bulunmamaktadır.')
        return redirect('dashboard')
    
    if user.is_superuser:
        projeler = Proje.objects.all()
        gorevler = Gorev.objects.all()
    else:
        projeler = Proje.objects.filter(
            Q(daire_baskanligi=user.daire_baskanligi) |
            Q(sube_mudurlugu=user.sube_mudurlugu)
        )
        gorevler = Gorev.objects.filter(
            Q(proje__daire_baskanligi=user.daire_baskanligi) |
            Q(proje__sube_mudurlugu=user.sube_mudurlugu)
        )
    
    # Proje istatistikleri
    proje_istatistikleri = {
        'toplam': projeler.count(),
        'bekleyen': projeler.filter(durum='BASLAMADI').count(),
        'devam_eden': projeler.filter(durum='DEVAM').count(),
        'tamamlanan': projeler.filter(durum='TAMAMLANDI').count(),
    }
    
    # Görev istatistikleri
    gorev_istatistikleri = {
        'toplam': gorevler.count(),
        'bekleyen': gorevler.filter(durum='BASLAMADI').count(),
        'devam_eden': gorevler.filter(durum='DEVAM').count(),
        'tamamlanan': gorevler.filter(durum='TAMAMLANDI').count(),
        'geciken': gorevler.filter(
            Q(son_tarih__lt=timezone.now().date()) &
            ~Q(durum='TAMAMLANDI')
        ).count(),
    }
    
    # Kullanıcı istatistikleri
    if user.is_superuser:
        kullanicilar = CustomUser.objects.all()
    else:
        kullanicilar = CustomUser.objects.filter(
            Q(daire_baskanligi=user.daire_baskanligi) |
            Q(sube_mudurlugu=user.sube_mudurlugu)
        )
    
    kullanici_istatistikleri = []
    for kullanici in kullanicilar:
        kullanici_gorevleri = gorevler.filter(atanan=kullanici)
        if kullanici_gorevleri.exists():
            istatistik = {
                'kullanici': kullanici,
                'toplam_gorev': kullanici_gorevleri.count(),
                'tamamlanan_gorev': kullanici_gorevleri.filter(durum='TAMAMLANDI').count(),
                'devam_eden_gorev': kullanici_gorevleri.filter(durum='DEVAM').count(),
                'bekleyen_gorev': kullanici_gorevleri.filter(durum='BASLAMADI').count(),
                'geciken_gorev': kullanici_gorevleri.filter(
                    Q(son_tarih__lt=timezone.now().date()) &
                    ~Q(durum='TAMAMLANDI')
                ).count(),
            }
            kullanici_istatistikleri.append(istatistik)
    
    context = {
        'proje_istatistikleri': proje_istatistikleri,
        'gorev_istatistikleri': gorev_istatistikleri,
        'kullanici_istatistikleri': kullanici_istatistikleri,
    }
    return render(request, 'core/rapor_listesi.html', context)

def register(request):
    """Kullanıcı kayıt görünümü"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
