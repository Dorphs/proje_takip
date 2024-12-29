from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Kimlik doğrulama URL'leri
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    
    # Ana sayfalar
    path('', views.dashboard, name='dashboard'),
    path('projeler/', views.proje_listesi, name='proje_listesi'),
    path('raporlar/', views.rapor_listesi, name='rapor_listesi'),
    
    # Proje URL'leri
    path('proje/ekle/', views.proje_ekle, name='proje_ekle'),
    path('proje/<int:pk>/', views.proje_detay, name='proje_detay'),
    path('proje/<int:pk>/ilerleme/ekle/', views.ilerleme_ekle, name='ilerleme_ekle'),
    path('proje/<int:pk>/duzenle/', views.proje_duzenle, name='proje_duzenle'),
    path('proje/<int:pk>/sil/', views.proje_sil, name='proje_sil'),
    
    # Görev URL'leri
    path('proje/<int:proje_pk>/gorev/ekle/', views.gorev_ekle, name='gorev_ekle'),
    path('gorev/<int:pk>/duzenle/', views.gorev_duzenle, name='gorev_duzenle'),
    path('gorev/<int:pk>/sil/', views.gorev_sil, name='gorev_sil'),
    
    # İlerleme URL'leri
    path('proje/<int:proje_pk>/ilerleme/ekle/', views.ilerleme_ekle, name='proje_ilerleme_ekle'),
    
    # API endpoints
    path('api/sube-mudurlukleri/<int:daire_id>/', views.get_sube_mudurlukleri, name='get_sube_mudurlukleri'),
    path('api/kullanicilar/<int:daire_id>/<int:sube_id>/', views.get_kullanicilar, name='get_kullanicilar'),
]
