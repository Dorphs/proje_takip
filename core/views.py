from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from django.contrib import messages
from .forms import ProjeForm, GorevForm, IlerlemeForm, CustomUserCreationForm
from .models import Proje, Gorev, Ilerleme, DaireBaskanligi, SubeMudurlugu, CustomUser

@login_required
def dashboard(request):
    """Dashboard görünümü"""
    user = request.user
    
    if user.unvan == 'GM':
        projeler = Proje.objects.all()
    elif user.unvan == 'DB':
        projeler = Proje.objects.filter(daire_baskanliklari=user.daire_baskanligi)
    elif user.unvan == 'SM':
        projeler = Proje.objects.filter(sube_mudurlukleri=user.sube_mudurlugu)
    else:  # Personel
        projeler = Proje.objects.filter(gorev__sorumlu=user).distinct()
    
    context = {
        'projeler': projeler,
        'bekleyen_projeler': projeler.filter(durum='Başlamadı').count(),
        'devam_eden_projeler': projeler.filter(durum='Devam Ediyor').count(),
        'tamamlanan_projeler': projeler.filter(durum='Tamamlandı').count(),
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def proje_listesi(request):
    """Proje listesi görünümü"""
    user = request.user
    search_query = request.GET.get('search', '')
    durum_filter = request.GET.get('durum', '')
    oncelik_filter = request.GET.get('oncelik', '')
    
    if user.unvan == 'GM':
        projeler = Proje.objects.all()
    elif user.unvan == 'DB':
        projeler = Proje.objects.filter(daire_baskanliklari=user.daire_baskanligi)
    elif user.unvan == 'SM':
        projeler = Proje.objects.filter(sube_mudurlukleri=user.sube_mudurlugu)
    else:  # Personel
        projeler = Proje.objects.filter(gorev__sorumlu=user).distinct()
    
    if search_query:
        projeler = projeler.filter(Q(ad__icontains=search_query) | Q(aciklama__icontains=search_query))
    if durum_filter:
        projeler = projeler.filter(durum=durum_filter)
    if oncelik_filter:
        projeler = projeler.filter(oncelik=oncelik_filter)
    
    context = {
        'projeler': projeler,
        'search_query': search_query,
        'durum_filter': durum_filter,
        'oncelik_filter': oncelik_filter,
    }
    return render(request, 'core/proje_listesi.html', context)

@login_required
def proje_detay(request, pk):
    """Proje detay görünümü"""
    proje = get_object_or_404(Proje, pk=pk)
    gorevler = proje.gorevler.all()
    ilerlemeler = proje.ilerlemeler.all().order_by('-tarih')
    
    context = {
        'proje': proje,
        'gorevler': gorevler,
        'ilerlemeler': ilerlemeler,
    }
    return render(request, 'core/proje_detay.html', context)

@login_required
def proje_ekle(request):
    """Proje ekleme görünümü"""
    if request.user.unvan != 'GM':
        messages.error(request, 'Bu işlem için yetkiniz bulunmamaktadır.')
        return redirect('proje_listesi')
    
    if request.method == 'POST':
        form = ProjeForm(request.POST)
        if form.is_valid():
            proje = form.save(commit=False)
            proje.olusturan = request.user
            proje.save()
            form.save_m2m()  # Many-to-many ilişkileri kaydet
            messages.success(request, 'Proje başarıyla oluşturuldu.')
            return redirect('proje_detay', pk=proje.pk)
    else:
        form = ProjeForm()
    
    context = {
        'form': form,
        'title': 'Yeni Proje Oluştur'
    }
    return render(request, 'core/proje_form.html', context)

@login_required
def proje_duzenle(request, pk):
    """Proje düzenleme görünümü"""
    if request.user.unvan != 'GM':
        messages.error(request, 'Bu işlem için yetkiniz bulunmamaktadır.')
        return redirect('proje_listesi')
    
    proje = get_object_or_404(Proje, pk=pk)
    if request.method == 'POST':
        form = ProjeForm(request.POST, instance=proje)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proje başarıyla güncellendi.')
            return redirect('proje_detay', pk=proje.pk)
    else:
        form = ProjeForm(instance=proje)
    
    context = {
        'form': form,
        'title': 'Proje Düzenle'
    }
    return render(request, 'core/proje_form.html', context)

@login_required
def gorev_ekle(request, proje_pk):
    """Görev ekleme görünümü"""
    proje = get_object_or_404(Proje, pk=proje_pk)
    
    if request.method == 'POST':
        form = GorevForm(request.POST)
        if form.is_valid():
            gorev = form.save(commit=False)
            gorev.proje = proje
            gorev.olusturan = request.user
            gorev.save()
            messages.success(request, 'Görev başarıyla oluşturuldu.')
            return redirect('proje_detay', pk=proje_pk)
    else:
        form = GorevForm()
    
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
    
    if request.method == 'POST':
        form = GorevForm(request.POST, instance=gorev)
        if form.is_valid():
            form.save()
            messages.success(request, 'Görev başarıyla güncellendi.')
            return redirect('proje_detay', pk=gorev.proje.pk)
    else:
        form = GorevForm(instance=gorev)
    
    context = {
        'form': form,
        'gorev': gorev,
        'title': 'Görev Düzenle'
    }
    return render(request, 'core/gorev_form.html', context)

@login_required
def ilerleme_ekle(request, proje_pk):
    """İlerleme ekleme görünümü"""
    proje = get_object_or_404(Proje, pk=proje_pk)
    
    if request.method == 'POST':
        form = IlerlemeForm(request.POST, request.FILES)
        if form.is_valid():
            ilerleme = form.save(commit=False)
            ilerleme.proje = proje
            ilerleme.kaydeden = request.user
            ilerleme.save()
            
            # Dosyaları kaydet
            for dosya in request.FILES.getlist('dosyalar'):
                ilerleme.dosyalar.create(dosya=dosya)
            
            # Fotoğrafları kaydet
            for fotograf in request.FILES.getlist('fotograflar'):
                ilerleme.fotograflar.create(fotograf=fotograf)
            
            messages.success(request, 'İlerleme kaydı başarıyla oluşturuldu.')
            return redirect('proje_detay', pk=proje_pk)
    else:
        form = IlerlemeForm()
    
    context = {
        'form': form,
        'proje': proje,
        'title': 'İlerleme Kaydı Ekle'
    }
    return render(request, 'core/ilerleme_form.html', context)

@login_required
def rapor_listesi(request):
    """Rapor listesi görünümü"""
    user = request.user
    
    if user.unvan == 'GM':
        projeler = Proje.objects.all()
        daire_baskanliklari = DaireBaskanligi.objects.all()
        context = {
            'daire_baskanliklari': daire_baskanliklari,
            'bekleyen_projeler': projeler.filter(durum='Başlamadı').count(),
            'devam_eden_projeler': projeler.filter(durum='Devam Ediyor').count(),
            'tamamlanan_projeler': projeler.filter(durum='Tamamlandı').count(),
        }
    elif user.unvan == 'DB':
        projeler = Proje.objects.filter(daire_baskanliklari=user.daire_baskanligi)
        sube_mudurlukleri = SubeMudurlugu.objects.filter(daire_baskanligi=user.daire_baskanligi)
        context = {
            'sube_mudurlukleri': sube_mudurlukleri,
            'bekleyen_projeler': projeler.filter(durum='Başlamadı').count(),
            'devam_eden_projeler': projeler.filter(durum='Devam Ediyor').count(),
            'tamamlanan_projeler': projeler.filter(durum='Tamamlandı').count(),
        }
    elif user.unvan == 'SM':
        projeler = Proje.objects.filter(sube_mudurlukleri=user.sube_mudurlugu)
        context = {
            'sube_projeleri': projeler,
            'bekleyen_projeler': projeler.filter(durum='Başlamadı').count(),
            'devam_eden_projeler': projeler.filter(durum='Devam Ediyor').count(),
            'tamamlanan_projeler': projeler.filter(durum='Tamamlandı').count(),
        }
    else:
        messages.error(request, 'Bu sayfaya erişim yetkiniz bulunmamaktadır.')
        return redirect('dashboard')
    
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
