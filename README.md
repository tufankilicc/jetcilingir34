# JET Çilingir Evi

Statik Vercel yayını için hazırlanmış JET Çilingir Evi web sitesi.

## Yerel sayfaları yeniden üretme

Python kuruluysa proje klasöründe:

```powershell
python build.py
```

Bu komut tüm HTML sayfalarını `public` klasörüne, sitemap ve robots dosyalarını da aynı klasöre üretir.

## Vercel ayarları

- Yayın klasörü: `public`
- Build komutu: gerekmez
- Framework: `Other`

`vercel.json` bu ayarları otomatik olarak tanımlar.

## Önemli adresler

- Ana sayfa: `/`
- Hakkımızda: `/hakkimizda.html`
- İletişim: `/iletisim.html`
- Hizmetler: `/hizmetler/`
- İlçe sayfaları: `/istanbul/gungoren-cilingir`
- Mahalle sayfaları: `/istanbul/gungoren/merter-cilingir`
