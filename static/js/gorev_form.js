document.addEventListener('DOMContentLoaded', function() {
    console.log("Gorev form script loaded");
    const daireSelect = document.getElementById('id_daire_baskanligi');
    const subeSelect = document.getElementById('id_sube_mudurlugu');
    const atananSelect = document.getElementById('id_atanan');

    console.log("Daire select:", daireSelect);
    console.log("Sube select:", subeSelect);
    console.log("Atanan select:", atananSelect);

    if (daireSelect && subeSelect && atananSelect) {
        // Başlangıçta şube müdürlüğü seçimini devre dışı bırak
        subeSelect.disabled = true;

        daireSelect.addEventListener('change', function() {
            const daireId = this.value;
            console.log("Daire ID changed:", daireId);
            
            // Şube müdürlüğü ve atanan kişi seçeneklerini temizle
            subeSelect.innerHTML = '<option value="">---------</option>';
            atananSelect.innerHTML = '<option value="">---------</option>';
            
            if (daireId) {
                // Şube müdürlüğü seçimini aktif hale getir
                subeSelect.disabled = false;

                // AJAX isteği gönder
                const url = `/api/sube-mudurlukleri/${daireId}/`;
                console.log("Fetching from:", url);

                fetch(url)
                    .then(response => {
                        console.log("Response:", response);
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log("Data received:", data);
                        data.forEach(sube => {
                            const option = document.createElement('option');
                            option.value = sube.id;
                            option.textContent = sube.ad;
                            subeSelect.appendChild(option);
                        });
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        subeSelect.disabled = true;
                    });
            } else {
                subeSelect.disabled = true;
                atananSelect.disabled = true;
            }
        });

        subeSelect.addEventListener('change', function() {
            const subeId = this.value;
            const daireId = daireSelect.value;
            console.log("Sube ID changed:", subeId);
            
            // Atanan kişi seçeneklerini temizle
            atananSelect.innerHTML = '<option value="">---------</option>';
            
            if (subeId && daireId) {
                // AJAX isteği gönder
                const url = `/api/kullanicilar/${daireId}/${subeId}/`;
                console.log("Fetching users from:", url);

                fetch(url)
                    .then(response => {
                        console.log("Response:", response);
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log("Users received:", data);
                        data.forEach(user => {
                            const option = document.createElement('option');
                            option.value = user.id;
                            option.textContent = `${user.first_name} ${user.last_name}`;
                            atananSelect.appendChild(option);
                        });
                        atananSelect.disabled = false;
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        atananSelect.disabled = true;
                    });
            } else {
                atananSelect.disabled = true;
            }
        });

        // Sayfa yüklendiğinde daire başkanlığı seçili ise şube müdürlüklerini yükle
        if (daireSelect.value) {
            daireSelect.dispatchEvent(new Event('change'));
        }
    }
});
