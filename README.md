# Proje Takip Sistemi

Django tabanlı bir proje takip sistemi. Kurumsal yapıda proje ve görev yönetimini kolaylaştırmak için tasarlanmıştır.

## Özellikler

- Kullanıcı rolleri (Genel Müdür, Daire Başkanı, Şube Müdürü, Personel)
- Proje yönetimi
- Görev takibi
- İlerleme raporları
- Dosya ve fotoğraf yükleme
- Detaylı raporlama

## Kurulum

1. Python 3.8+ yüklü olmalıdır
2. Sanal ortam oluşturun ve aktif edin:
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. Veritabanını oluşturun:
```bash
python manage.py migrate
```

5. Superuser oluşturun:
```bash
python manage.py createsuperuser
```

6. Sunucuyu başlatın:
```bash
python manage.py runserver
```

## Kullanım

1. Admin paneline giriş yapın (`http://127.0.0.1:8000/admin`)
2. Daire Başkanlıkları ve Şube Müdürlükleri oluşturun
3. Personel ekleyin ve rollerini atayın
4. Projeler oluşturun ve görevleri atayın

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
