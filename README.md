# Proje Takip Sistemi

Django tabanlı proje ve görev takip sistemi.

## Özellikler

- Kullanıcı yetkilendirme sistemi
- Proje oluşturma ve yönetme
- Görev atama ve takibi
- İlerleme raporları
- Dosya ve fotoğraf yükleme
- Dashboard ve istatistikler

## Kurulum

1. Projeyi klonlayın:
```bash
git clone <repository-url>
cd proje_takip
```

2. Virtual environment oluşturun ve aktif edin:
```bash
python -m venv venv
# Windows için:
venv\Scripts\activate
# Linux/Mac için:
source venv/bin/activate
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. Veritabanı migrasyonlarını yapın:
```bash
python manage.py migrate
```

5. Süper kullanıcı oluşturun:
```bash
python manage.py createsuperuser
```

6. Sunucuyu başlatın:
```bash
python manage.py runserver
```

## Kullanım

1. Admin paneline giriş yapın: `http://127.0.0.1:8000/admin/`
2. Daire Başkanlıkları ve Şube Müdürlükleri ekleyin
3. Kullanıcıları oluşturun ve yetkilendirin
4. Proje ve görevleri yönetin

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
