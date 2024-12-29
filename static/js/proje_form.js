document.addEventListener('DOMContentLoaded', function() {
    console.log("Proje form script loaded");

    // Select2 initialization
    $('.select2').select2({
        theme: 'bootstrap-5',
        width: '100%',
        language: 'tr'
    });

    const daireSelect = document.getElementById('id_daire_baskanligi');
    const subeSelect = document.getElementById('id_sube_mudurlugu');

    if (daireSelect && subeSelect) {
        console.log("Form elements found");

        // Daire başkanlığı değiştiğinde
        daireSelect.addEventListener('change', function() {
            const daireId = this.value;
            console.log("Selected daire:", daireId);

            // Şube müdürlüğü seçimini temizle
            $(subeSelect).val(null).trigger('change');

            if (daireId) {
                // AJAX isteği gönder
                fetch(`/api/sube-mudurlukleri/${daireId}/`)
                    .then(response => {
                        console.log("Response status:", response.status);
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log("Received data:", data);
                        
                        // Seçenekleri temizle
                        subeSelect.innerHTML = '<option value="">Şube müdürlüğü seçin</option>';
                        
                        // Yeni seçenekleri ekle
                        data.forEach(sube => {
                            const option = document.createElement('option');
                            option.value = sube.id;
                            option.textContent = sube.ad;
                            subeSelect.appendChild(option);
                        });
                        
                        // Select2'yi güncelle
                        $(subeSelect).trigger('change');
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        subeSelect.innerHTML = '<option value="">Hata oluştu</option>';
                    });
            } else {
                // Daire seçili değilse şube seçimini temizle
                subeSelect.innerHTML = '<option value="">Önce daire başkanlığı seçin</option>';
                $(subeSelect).trigger('change');
            }
        });

        // Sayfa yüklendiğinde daire başkanlığı seçili ise şube müdürlüklerini yükle
        if (daireSelect.value) {
            daireSelect.dispatchEvent(new Event('change'));
        }
    }

    // Form validation
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    }
});
