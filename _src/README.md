# AnberTech ana sitesi: kaynak dosyalar

Site `python3 _src/build.py` ile üretilir (depo kökünden). Üretilen `index.html` ve `<dil>/index.html` dosyaları elle düzenlenmez.

- `i18n/<dil>.json`: 33 dilin metinleri (kaynak `tr.json` ve `en.json`)
- `symbols.svg`: App Store, Google Play ve ok simgeleri
- Uygulama sitelerinin dil listesi, rehber adresleri ve Not Hesaplayıcı'nın dillere göre adı kardeş depolardan okunur: `../TurnuVolt`, `../NotHesaplayici`, `../Kuafix`. Bu depolar aynı klasörde olmalı. Bir dil o uygulamanın sitesinde yoksa İngilizce sayfasına bağlanılır.
- Bir uygulamanın fiyatı, dil sayısı ya da platformu değişirse `i18n/*.json` içindeki `*_txt`, `*_plat` ve `faq` metinleri ile `build.py` içindeki `build_llms` güncellenir.
- Android yayına çıkınca `build.py` > `APPS` içinde ilgili uygulamaya `play` adresi eklenir; "Yakında" rozeti kendiliğinden kalkar.
