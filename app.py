from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "templates" / "index.html"
CONTACT_TEMPLATE_PATH = BASE_DIR / "templates" / "iletisim.html"
ABOUT_TEMPLATE_PATH = BASE_DIR / "templates" / "hakkimizda.html"
SERVICE_TEMPLATE_PATH = BASE_DIR / "templates" / "hizmet.html"
PHONE_DISPLAY = "+90 531 893 85 15"
PHONE_TEL = "+905318938515"
WHATSAPP_NUMBER = "905318938515"

DISTRICTS = [
    "Adalar", "Arnavutk\u00f6y", "Ata\u015fehir", "Avc\u0131lar", "Ba\u011fc\u0131lar", "Bah\u00e7elievler",
    "Bak\u0131rk\u00f6y", "Ba\u015fak\u015fehir", "Bayrampa\u015fa", "Be\u015fikta\u015f", "Beykoz", "Beylikd\u00fcz\u00fc",
    "Beyo\u011flu", "B\u00fcy\u00fck\u00e7ekmece", "\u00c7atalca", "\u00c7ekmek\u00f6y", "Esenler", "Esenyurt",
    "Ey\u00fcpsultan", "Fatih", "Gaziosmanpa\u015fa", "G\u00fcng\u00f6ren", "Kad\u0131k\u00f6y", "Ka\u011f\u0131thane",
    "Kartal", "K\u00fc\u00e7\u00fck\u00e7ekmece", "Maltepe", "Pendik", "Sancaktepe", "Sar\u0131yer",
    "Silivri", "Sultanbeyli", "Sultangazi", "\u015eile", "\u015ei\u015fli", "Tuzla", "\u00dcmraniye",
    "\u00dcsk\u00fcdar", "Zeytinburnu",
]


def slugify(value):
    table = str.maketrans("\u00e7\u011f\u0131\u00f6\u015f\u00fc\u00c7\u011e\u0130\u00d6\u015e\u00dc", "cgiosuCGIOSU")
    return value.translate(table).lower().replace(" ", "-")


DISTRICT_BY_SLUG = {slugify(name): name for name in DISTRICTS}

NEIGHBORHOODS_BY_DISTRICT = {
    "Güngören": ["Merter", "Tozkoparan", "Haznedar", "Güneştepe", "Gençosman", "Sanayi"],
    "Bağcılar": ["Mahmutbey", "Güneşli", "Bağlar", "Yıldıztepe", "Kirazlı", "Kazım Karabekir"],
    "Bahçelievler": ["Şirinevler", "Soğanlı", "Kocasinan", "Yenibosna", "Siyavuşpaşa", "Zafer"],
    "Bakırköy": ["Ataköy", "Yeşilköy", "Florya", "Zuhuratbaba", "Cevizlik", "Kartaltepe"],
    "Esenler": ["Menderes", "Tuna", "Nine Hatun", "Havaalanı", "Oruçreis", "Kemer"],
    "Bayrampaşa": ["Altıntepsi", "Cevatpaşa", "Kocatepe", "Muratpaşa", "Yıldırım", "Terazidere"],
    "Kadıköy": ["Koşuyolu", "Fenerbahçe", "Caddebostan", "Bostancı", "Göztepe", "Osmanağa"],
    "Maltepe": ["Altayçeşme", "Cevizli", "Fındıklı", "İdealtepe", "Küçükyalı", "Zümrütevler"],
    "Kartal": ["Atalar", "Cevizli", "Esentepe", "Orhantepe", "Soğanlık", "Yakacık"],
    "Ataşehir": ["İçerenköy", "Kayışdağı", "Küçükbakkalköy", "Barbaros", "Ferhatpaşa", "Atatürk"],
}

NEIGHBORHOODS_BY_DISTRICT.update({
    "Adalar": ["Büyükada", "Heybeliada", "Burgazada", "Kınalıada"],
    "Arnavutköy": ["Arnavutköy Merkez", "Haraççı", "Hadımköy", "Bolluca", "Taşoluk"],
    "Avcılar": ["Ambarlı", "Cihangir", "Denizköşkler", "Firuzköy", "Mustafa Kemal Paşa"],
    "Ba\u015fak\u015fehir": ["Bah\u00e7e\u015fehir 1. K\u0131s\u0131m", "Bah\u00e7e\u015fehir 2. K\u0131s\u0131m", "Ba\u015fak\u015fehir Merkez", "Ba\u011flarba\u015f\u0131", "Kayaba\u015f\u0131", "Kaya\u015fehir"],
    "Beşiktaş": ["Abbasağa", "Balmumcu", "Etiler", "Levent", "Ortaköy", "Yıldız"],
    "Beykoz": ["Anadoluhisarı", "Çubuklu", "Kanlıca", "Paşabahçe", "Rüzgarlıbahçe", "Tokatköy"],
    "Beylikdüzü": ["Adnan Kahveci", "Barış", "Büyükşehir", "Kavaklı", "Gürpınar", "Yakuplu"],
    "Beyoğlu": ["Cihangir", "Galata", "Hacıahmet", "Kaptanpaşa", "Kasımpaşa", "Piyalepaşa"],
    "Büyükçekmece": ["Alkent 2000", "Beykent", "Güzelce", "Kumburgaz", "Mimaroba", "Tepecik"],
    "Çatalca": ["Çatalca Merkez", "Ferhatpaşa", "Atatürk", "Kaleiçi", "Muratbey"],
    "Çekmeköy": ["Alemdağ", "Çamlık", "Çatalmeşe", "Merkez", "Mehmet Akif", "Taşdelen"],
    "Esenyurt": ["Akçaburgaz", "Bağlarçeşme", "Beymer", "Mehterçeşme", "Saadet", "Yenikent"],
    "Eyüpsultan": ["Alibeyköy", "Göktürk Merkez", "İslambey", "Kemerburgaz", "Rami Yeni", "Topçular"],
    "Fatih": ["Aksaray", "Balat", "Cankurtaran", "Fener", "Kocamustafapaşa", "Sultanahmet"],
    "Gaziosmanpaşa": ["Bağlarbaşı", "Karadeniz", "Karayolları", "Küçükköy", "Merkez", "Yıldıztabya"],
    "Kağıthane": ["Çağlayan", "Gültepe", "Hamidiye", "Merkez", "Seyrantepe", "Talatpaşa"],
    "Küçükçekmece": ["Atakent", "Cennet", "Halkalı Merkez", "İnönü", "Kanarya", "Sefaköy"],
    "Pendik": ["Çamçeşme", "Esenyalı", "Fevzi Çakmak", "Kaynarca", "Kurtköy", "Yenişehir"],
    "Sancaktepe": ["Abdurrahmangazi", "Atatürk", "Emek", "Meclis", "Sarıgazi", "Yenidoğan"],
    "Sarıyer": ["Ayazağa", "Büyükdere", "Emirgan", "İstinye", "Maslak", "Tarabya"],
    "Silivri": ["Alipaşa", "Büyükçavuşlu", "Çanta", "Mimarsinan", "Selimpaşa", "Yeni"],
    "Sultanbeyli": ["Abdurrahmangazi", "Adil", "Battalgazi", "Hasanpaşa", "Mimar Sinan", "Turgut Reis"],
    "Sultangazi": ["50. Yıl", "Cebeci", "Esentepe", "Gazi", "Habipler", "Uğur Mumcu"],
    "Şile": ["Ağva Merkez", "Balibey", "Çavuş", "Hacılı", "İmrenli", "Üvezli"],
    "Şişli": ["19 Mayıs", "Bomonti", "Esentepe", "Halaskargazi", "Kuştepe", "Mecidiyeköy"],
    "Tuzla": ["Aydınlı", "Cami", "Evliya Çelebi", "İçmeler", "Mescit", "Şifa"],
    "Ümraniye": ["Atakent", "Çakmak", "Dudullu", "Ihlamurkuyu", "Site", "Yamanevler"],
    "Üsküdar": ["Acıbadem", "Altunizade", "Beylerbeyi", "Bulgurlu", "Çengelköy", "Kuzguncuk"],
    "Zeytinburnu": ["Beştelsiz", "Kazlıçeşme", "Maltepe", "Merkezefendi", "Seyitnizam", "Veliefendi"],
})

NEIGHBORHOODS_BY_SLUG = {slugify(name): neighborhoods for name, neighborhoods in NEIGHBORHOODS_BY_DISTRICT.items()}

NEIGHBORHOOD_COPY_VARIANTS = [
    ("Kap\u0131da kald\u0131ysan\u0131z ilk ad\u0131m", "Anahtar\u0131n i\u00e7eride kalmas\u0131 veya kilidin d\u00f6nmemesi gibi durumlarda {neighborhood} b\u00f6lgesine mobil kap\u0131 a\u00e7ma deste\u011fi sa\u011fl\u0131yoruz.", "Kap\u0131 a\u00e7\u0131lamazsa servis \u00fccreti talep etmiyoruz."),
    ("G\u00fcvenli kilit de\u011fi\u015fimi", "Ta\u015f\u0131nma, anahtar kayb\u0131 veya g\u00fcvenlik endi\u015fesinde {neighborhood} ve {district} genelinde kilit g\u00f6be\u011fi ile barel de\u011fi\u015fimi yap\u0131yoruz.", "Uygun kilit se\u00e7imini kap\u0131 tipini kontrol ettikten sonra birlikte belirliyoruz."),
    ("Apartman ve site kap\u0131lar\u0131", "{neighborhood} mahallesindeki apartman, site ve bina giri\u015flerinde kap\u0131 a\u00e7ma ile kilit ar\u0131zas\u0131 i\u00e7in yerinde destek veriyoruz.", "M\u00fcdahale \u00f6ncesi yap\u0131lacak i\u015flemi ve \u00fccret bilgisini a\u00e7\u0131k\u00e7a payla\u015f\u0131yoruz."),
    ("Gece de ula\u015f\u0131labilir mobil ekip", "Gece veya hafta sonu kap\u0131da kald\u0131\u011f\u0131n\u0131zda {neighborhood} i\u00e7in 7/24 acil \u00e7ilingir y\u00f6nlendirmesi yap\u0131yoruz.", "Konumunuzu ve kap\u0131 tipinizi telefonda dinleyerek uygun ekipmanla geliyoruz."),
    ("Ev ve i\u015f yeri i\u00e7in pratik \u00e7\u00f6z\u00fcm", "{district} {neighborhood} b\u00f6lgesinde ev, ofis ve d\u00fckkan kap\u0131lar\u0131 i\u00e7in acil kap\u0131 a\u00e7ma ve kilit de\u011fi\u015fimi hizmeti sunuyoruz.", "Hasars\u0131z m\u00fcdahaleyi, kap\u0131 ve kilit sisteminin durumuna g\u00f6re planl\u0131yoruz."),
    ("Ara\u00e7 anahtar\u0131nda mobil destek", "Ara\u00e7 anahtar\u0131n\u0131z i\u00e7eride kald\u0131ysa veya kumanda sorunu ya\u015f\u0131yorsan\u0131z {neighborhood} b\u00f6lgesine oto \u00e7ilingir deste\u011fi g\u00f6nderiyoruz.", "Marka, model ve konum bilgisiyle daha do\u011fru y\u00f6nlendirme yapabiliyoruz."),
    ("Anahtar kayb\u0131 sonras\u0131 g\u00fcvenlik", "{neighborhood} ve yak\u0131n\u0131nda anahtar kayb\u0131 sonras\u0131 kilit yenileme, barel de\u011fi\u015fimi ve yedek anahtar \u00e7\u00f6z\u00fcmleri sunuyoruz.", "Yeni anahtar\u0131n\u0131z\u0131n g\u00fcvenli\u011fi i\u00e7in mevcut kilit sistemini de\u011ferlendiriyoruz."),
    ("Hasars\u0131z m\u00fcdahale anlay\u0131\u015f\u0131", "{district} il\u00e7esinin {neighborhood} mahallesinde kap\u0131, kilit ve \u00e7elik kasa sorunlar\u0131na uygun ekipmanla m\u00fcdahale ediyoruz.", "Amac\u0131m\u0131z gereksiz par\u00e7a de\u011fi\u015fimi yapmadan sorunu g\u00fcvenli bi\u00e7imde \u00e7\u00f6zmektir."),
]


def repair_text(value):
    """Repair legacy mojibake while keeping already-correct text intact."""
    if not isinstance(value, str):
        return value
    try:
        return value.encode("latin1").decode("utf-8")
    except UnicodeError:
        return value


def title_case_tr(value):
    """Format Turkish place names without breaking dotted and dotless i."""
    lower_map = str.maketrans({"I": "ı", "İ": "i"})
    upper_map = str.maketrans({"i": "İ", "ı": "I"})
    words = value.translate(lower_map).lower().split()
    return " ".join(word[:1].translate(upper_map) + word[1:] for word in words)
def title_case_tr(value):
    lower_map = str.maketrans({"I": "\u0131", "\u0130": "i"})
    upper_map = str.maketrans({"i": "\u0130", "\u0131": "I"})
    words = value.translate(lower_map).lower().split()
    return " ".join(word[:1].translate(upper_map).upper() + word[1:] for word in words)


SERVICE_PAGES = {
    "acil-cilingir": {
        "name": "İstanbul Acil Çilingir",
        "description": "İstanbul genelinde 7/24 acil çilingir, hasarsız kapı açma ve hızlı mobil servis.",
        "intro": "Kapıda kaldığınızda, kilidiniz arızalandığında veya anahtarınızı kaybettiğinizde İstanbul genelinde hızlı ve güvenilir destek sağlıyoruz.",
        "sections": [("7/24 acil çilingir desteği", "Ev, iş yeri ve bina kapılarında günün her saatinde mobil ekibimizi bulunduğunuz konuma yönlendiriyoruz."), ("Hasarsız kapı açma", "Çelik kapı, apartman kapısı ve oda kapılarında uygun ekipmanla, gereksiz zarar vermeden müdahale ediyoruz."), ("İşlem öncesi bilgilendirme", "Yapılabilecek işlemi ve tahmini ücreti müdahale öncesinde açıkça anlatıyoruz. Kapı açılamazsa servis ücreti talep etmiyoruz.")],
    },
    "kapi-acma": {
        "name": "Kapı Açma Hizmeti",
        "description": "Çelik kapı, ev ve iş yeri kapısı açma hizmeti. İstanbul genelinde 7/24 hasarsız müdahale.",
        "intro": "Anahtar içeride kaldıysa, kilit dönmüyorsa veya kapınız kapandıysa kapı türüne uygun profesyonel yöntemle yardımcı oluyoruz.",
        "sections": [("Ev ve iş yeri kapısı açma", "Daire, ofis, apartman ve iş yeri kapılarına mobil ekiplerle ulaşarak güvenli açma hizmeti veriyoruz."), ("Çelik kapı açma", "Çelik kapılarda kilit ve kapı yapısını gözeterek kontrollü, hasarsız müdahale hedefliyoruz."), ("Kapı açılamazsa ücret yok", "Müdahale sonucunda kapı açılamazsa müşterilerimizden servis ücreti istemiyoruz.")],
    },
    "kilit-degisimi": {
        "name": "Kilit Değişimi",
        "description": "İstanbul kilit değişimi ve kilit göbeği/barel yenileme hizmeti. Güvenli ve hızlı montaj.",
        "intro": "Taşınma, anahtar kaybı veya güvenlik endişesi sonrasında kapınızın kilit sistemini yerinde yeniliyoruz.",
        "sections": [("Kilit göbeği ve barel değişimi", "Mevcut ölçüyü kontrol ederek kapınıza uygun kilit göbeği veya barel seçimi yapıyoruz."), ("Yüksek güvenlikli seçenekler", "İhtiyacınıza ve kapı tipinize göre güvenlik seviyesi yüksek kilit alternatifleri sunuyoruz."), ("Yerinde hızlı montaj", "İstanbul genelinde mobil servis ile kilit değişimini kısa sürede tamamlıyor, eski kilidinizi güvenli şekilde teslim alıyoruz.")],
    },
    "oto-cilingir": {
        "name": "Oto Çilingir",
        "description": "İstanbul oto çilingir ve araç kapısı açma hizmeti. 7/24 mobil destek.",
        "intro": "Araç anahtarınız içeride kaldığında, kaybolduğunda veya kumandanız çalışmadığında bulunduğunuz konuma mobil oto çilingir gönderiyoruz.",
        "sections": [("Araç kapısı açma", "Araç kapısına ve kilit sistemine gereksiz zarar vermeden profesyonel ekipmanla müdahale ediyoruz."), ("Yedek anahtar ve kumanda", "Uygun araçlarda yedek anahtar, kumanda ve anahtar kopyalama çözümleri sunuyoruz."), ("Marka ve model bilgisi", "Daha hızlı yönlendirme için çağrı sırasında aracınızın marka, model ve bulunduğunuz konumu öğreniyoruz.")],
    },
    "celik-kasa-acma": {
        "name": "Çelik Kasa Açma",
        "description": "İstanbul çelik kasa açma hizmeti. Şifre, anahtar ve kilit arızalarında profesyonel destek.",
        "intro": "Anahtarı kaybolan, şifresi unutulan veya kilidi arızalanan çelik kasalar için kontrollü ve güvenli açma desteği sağlıyoruz.",
        "sections": [("Ev ve iş yeri kasaları", "Kasa türünü ve kilit sistemini değerlendirerek uygun müdahale yöntemini belirliyoruz."), ("Kilit ve şifre sorunları", "Anahtar kaybı, şifre unutulması ve kilit arızalarında kasanın içeriğini korumaya öncelik veriyoruz."), ("Açma sonrası güvenlik", "Gerekirse kasa kilidi veya şifre sistemi için yenileme seçeneklerini de görüşüyoruz.")],
    },
    "anahtar-kopyalama": {
        "name": "Anahtar Kopyalama",
        "description": "Ev, iş yeri ve araç anahtarı kopyalama hizmeti. Hızlı ve güvenilir anahtar çözümleri.",
        "intro": "Yedek anahtar ihtiyacınız için ev, iş yeri ve uygun araç anahtarlarında hızlı kopyalama çözümleri sunuyoruz.",
        "sections": [("Ev ve iş yeri anahtarları", "Günlük kullanım anahtarları ve bina giriş anahtarları için hassas kopyalama hizmeti veriyoruz."), ("Özel anahtar sistemleri", "Güvenlikli anahtarlar için kopyalama şartlarını ve uygun çözümü işlem öncesinde açıklıyoruz."), ("Yerinde destek", "İhtiyacın türüne göre mobil servis ile bulunduğunuz konuma yönlendirme yapabiliyoruz.")],
    },
}


def render_template(path, template_path=TEMPLATE_PATH):
    template = template_path.read_text(encoding="utf-8")
    if any(marker in template for marker in ("\u00c3", "\u00c4", "\u00e2")):
        try:
            template = template.encode("latin1").decode("utf-8")
        except UnicodeError:
            pass
    if template_path == TEMPLATE_PATH:
        template = re.sub(r'<script type="application/ld\+json">.*?</script>', '<script type="application/ld+json">{{LOCAL_SCHEMA}}</script>', template, count=1, flags=re.S)
    path_parts = path.strip("/").split("/")
    slug = path_parts[1].removesuffix("-cilingir") if len(path_parts) == 2 and path_parts[0] == "istanbul" else (path_parts[1] if len(path_parts) >= 3 and path_parts[0] == "istanbul" else "")
    neighborhood_slug = path_parts[2].removesuffix("-cilingir") if len(path_parts) >= 3 and path_parts[0] == "istanbul" else ""
    area = DISTRICT_BY_SLUG.get(slug, "")
    area_name = title_case_tr(area or "\u0130STANBUL")
    neighborhood_name = next((title_case_tr(name) for name in NEIGHBORHOODS_BY_SLUG.get(slug, []) if slugify(name) == neighborhood_slug), "")
    service_slug = path.removeprefix("/hizmetler/").removesuffix(".html") if path.startswith("/hizmetler/") else ""
    service = SERVICE_PAGES.get(service_slug)
    if service:
        service = {
            **service,
            "name": repair_text(service["name"]),
            "description": repair_text(service["description"]),
            "intro": repair_text(service["intro"]),
            "sections": [(repair_text(title), repair_text(body)) for title, body in service["sections"]],
        }
    service_content = "".join(f'<article class="service-detail"><h2>{escape(title)}</h2><p>{escape(body)}</p></article>' for title, body in (service["sections"] if service else []))
    area_seo_content = f'<h2>{escape(area_name)} JET Çilingir | İstanbul’da Güvenilir Acil Servis</h2><p>{escape(area_name)} ve çevresinde kapıda kalma, kilit arızası veya anahtar kaybı gibi durumlarda JET Çilingir olarak hızlı mobil destek sağlıyoruz. İhtiyacınızı telefonda dinleyip bulunduğunuz konuma en yakın ekibi yönlendiriyoruz.</p><p>Ev, iş yeri ve apartman kapısı açma; çelik kapı kilidi, kilit göbeği ve barel değişimi; oto çilingir ve çelik kasa açma hizmetleri sunuyoruz. Müdahale öncesinde yapılabilecek işlemi ve ücret bilgisini açıkça paylaşıyoruz.</p><p>Amacımız, {escape(area_name)} bölgesinde güvenli ve hasarsız çözümler sunmak. Kapı açılamadığı durumlarda müşterilerimizden servis ücreti talep etmiyor, 7/24 ulaşılabilir bir çilingir desteği sağlıyoruz.</p>'
    area_seo_content = repair_text(area_seo_content)
    service_areas = [{"@type": "City", "name": "İstanbul"}] + [{"@type": "AdministrativeArea", "name": name} for name in DISTRICTS]
    if neighborhood_name:
        service_areas.append({"@type": "Place", "name": neighborhood_name})
    business_schema = {
        "@type": "Locksmith",
        "@id": f"https://www.jetcilingir34.com{path}#business",
        "name": "JET Çilingir",
        "url": f"https://www.jetcilingir34.com{path if path != '/index.html' else '/'}",
        "telephone": PHONE_TEL,
        "email": "info@jetcilingir34.com",
        "areaServed": service_areas,
        "serviceType": ["Acil çilingir", "Kapı açma", "Kilit değişimi", "Oto çilingir", "Çelik kasa açma"],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"}],
    }
    faq_schema = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": "Kapı açılmazsa servis ücreti var mı?", "acceptedAnswer": {"@type": "Answer", "text": "Hayır. Kapıyı açamadığımız durumlarda müşterilerimizden servis ücreti talep etmiyoruz. İşlem başlamadan önce yapılabilecek müdahale ve ücret konusunda sizi bilgilendiriyoruz."}}]}, ensure_ascii=False)
    breadcrumb_items = [{"@type": "ListItem", "position": 1, "name": "Anasayfa", "item": "https://www.jetcilingir34.com/"}]
    if area:
        breadcrumb_items.append({"@type": "ListItem", "position": 2, "name": f"{area_name} Çilingir", "item": f"https://www.jetcilingir34.com/istanbul/{slug}-cilingir"})
    if neighborhood_name:
        breadcrumb_items.append({"@type": "ListItem", "position": 3, "name": f"{neighborhood_name} Çilingir", "item": f"https://www.jetcilingir34.com{path}"})
    local_schema = json.dumps({"@context": "https://schema.org", "@graph": [business_schema, {"@type": "BreadcrumbList", "itemListElement": breadcrumb_items}]}, ensure_ascii=False)
    breadcrumb_html = ""
    if area:
        breadcrumb_html = f'<nav class="breadcrumbs" aria-label="Sayfa yolu"><a href="/">Anasayfa</a><span>›</span><a href="/istanbul/{slug}-cilingir">{escape(area_name)} Çilingir</a>' + (f'<span>›</span><strong>{escape(neighborhood_name)} Çilingir</strong>' if neighborhood_name else "") + "</nav>"
    neighborhoods = NEIGHBORHOODS_BY_SLUG.get(slug, [])
    neighborhood_content = ""
    if neighborhoods:
        neighborhood_links = "".join(f"<span>{escape(name)} Çilingir</span>" for name in neighborhoods)
        neighborhood_content = f'<section class="neighborhoods" aria-labelledby="mahalleler-baslik"><h2 id="mahalleler-baslik">{escape(area_name)} Mahallelerinde Çilingir Hizmeti</h2><p>{escape(area_name)} ilçesinin seçili mahallelerinde kapı açma, kilit değişimi ve oto çilingir için mobil servis desteği sağlıyoruz.</p><div class="neighborhood-grid">{neighborhood_links}</div></section>'
    neighborhood_content = repair_text(neighborhood_content)
    if neighborhoods:
        neighborhood_links = "".join(f'<a href="/istanbul/{slug}/{slugify(name)}-cilingir"><span>{escape(name)} \u00c7ilingir</span></a>' for name in neighborhoods)
        neighborhood_content = f'<section class="neighborhoods" aria-labelledby="mahalleler-baslik"><h2 id="mahalleler-baslik">{escape(area_name)} Mahallelerinde \u00c7ilingir Hizmeti</h2><p>{escape(area_name)} il\u00e7esinin se\u00e7ili mahallelerinde kap\u0131 a\u00e7ma, kilit de\u011fi\u015fimi ve oto \u00e7ilingir i\u00e7in mobil servis deste\u011fi sa\u011fl\u0131yoruz.</p><div class="neighborhood-grid">{neighborhood_links}</div></section>'
    if neighborhood_name:
        variant_index = sum(ord(char) for char in f"{slug}-{neighborhood_slug}") % len(NEIGHBORHOOD_COPY_VARIANTS)
        variant_heading, variant_body, variant_note = NEIGHBORHOOD_COPY_VARIANTS[variant_index]
        variant_body = variant_body.format(neighborhood=escape(neighborhood_name), district=escape(area_name))
        variant_note = variant_note.format(neighborhood=escape(neighborhood_name), district=escape(area_name))
        neighborhood_content = f'<section class="neighborhoods" aria-labelledby="mahalleler-baslik"><h2 id="mahalleler-baslik">{escape(neighborhood_name)} {escape(area_name)} Çilingir | {variant_heading}</h2><p>{variant_body}</p><p>{variant_note} 7/24 mobil ekip için hemen arayabilir veya WhatsApp üzerinden konum gönderebilirsiniz.</p><div class="neighborhood-grid">{neighborhood_links}</div></section>'
    area_links = "".join(
        f'<a href="/istanbul/{slugify(name)}-cilingir">{escape(name)} Çilingir</a>'
        for name in DISTRICTS
    )
    area_links = area_links.replace("\u00c3\u2021", "\u00c7")
    network_items = "".join(
        f'<a class="network-item" href="/istanbul/{slugify(name)}-cilingir"><span class="network-number">{index:02d}</span><span><b>{escape(name)}</b></span></a>'
        for index, name in enumerate(DISTRICTS, 1)
    )
    chips = lambda names: "".join(f'<div class="brand-chip">{escape(name)}</div>' for name in names)
    values = {
        "{{PHONE_DISPLAY}}": PHONE_DISPLAY,
        "{{PHONE_TEL}}": PHONE_TEL,
        "{{WHATSAPP_NUMBER}}": WHATSAPP_NUMBER,
        "{{AREA_NAME}}": area_name,
        "{{AREA_NAME_UPPER}}": area_name.upper(),
        "{{PAGE_TITLE}}": f"{neighborhood_name + ' ' if neighborhood_name else ''}{area_name} JET \u00c7ilingir | 7/24 Acil \u00c7ilingir",
        "{{META_DESCRIPTION}}": f"{area_name} 7/24 acil çilingir hizmeti. JET Çilingir; kapı açma, kilit değişimi ve oto çilingir desteğiyle hızlıca yanınızda.",
        "{{AREA_LINKS}}": area_links,
        "{{NETWORK_ITEMS}}": network_items,
        "{{SCHEMA_NAME}}": f"JET Cilingir {area_name}",
        "{{CANONICAL_URL}}": f"https://www.jetcilingir34.com{path if path != '/index.html' else '/'}",
        "{{BRAND_CHIPS}}": chips(["Kale Kilit", "Mul-T-Lock", "Yale Kilit", "Yuma Kilit", "Daf Kilit", "Ito Kilit", "Mauer Kilit", "Desi Alarm & Kilit", "Dortek Kilit", "Keso Kilit", "Cisa Kilit", "Abloy Kilit", "Mottura Kilit", "Fiam Kilit", "Securisme Kilit", "Tri-Circle Kilit"]),
        "{{SAFE_CHIPS}}": chips(["Kiratli Kasa", "Eurosafe Kasa", "Kale Celik Kasa", "Gazi Kasa", "Valberg Kasa", "Sentry Safe", "Yale Dijital Kasa", "Burg Wachter", "Besa Kasa", "Chubbsafes", "Mas Kasa", "Kaba Kasa Sistemleri"]),
        "{{AUTO_CHIPS}}": chips(["Volkswagen", "BMW", "Mercedes", "Fiat", "Renault", "Ford", "Toyota", "Hyundai"]),
        "{{SERVICE_NAME}}": service["name"] if service else "",
        "{{SERVICE_DESCRIPTION}}": service["description"] if service else "",
        "{{SERVICE_INTRO}}": service["intro"] if service else "",
        "{{SERVICE_CONTENT}}": service_content,
        "{{AREA_SEO_CONTENT}}": area_seo_content,
        "{{AREA_NEIGHBORHOODS}}": neighborhood_content,
        "{{LOCAL_SCHEMA}}": local_schema,
        "{{FAQ_SCHEMA}}": faq_schema,
        "{{BREADCRUMB_HTML}}": breadcrumb_html,
    }
    values["{{META_DESCRIPTION}}"] = f"{neighborhood_name + ' ' if neighborhood_name else ''}{area_name} 7/24 acil \u00e7ilingir hizmeti. JET \u00c7ilingir; kap\u0131 a\u00e7ma, kilit de\u011fi\u015fimi ve oto \u00e7ilingir deste\u011fiyle h\u0131zl\u0131ca yan\u0131n\u0131zda."
    for marker, value in values.items():
        template = template.replace(marker, value)
    return template.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path.rstrip("/") or "/"
        if path == "/index.html":
            self.send_response(301)
            self.send_header("Location", "/")
            self.end_headers()
            return
        if path == "/robots.txt":
            content = b"User-agent: *\nAllow: /\nSitemap: https://www.jetcilingir34.com/sitemap.xml\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if path == "/sitemap.xml":
            district_urls = [f"https://www.jetcilingir34.com/istanbul/{slugify(name)}-cilingir" for name in DISTRICTS]
            neighborhood_urls = [f"https://www.jetcilingir34.com/istanbul/{slug}/{slugify(neighborhood)}-cilingir" for slug, neighborhoods in NEIGHBORHOODS_BY_SLUG.items() for neighborhood in neighborhoods]
            urls = ["https://www.jetcilingir34.com/", "https://www.jetcilingir34.com/hakkimizda.html", "https://www.jetcilingir34.com/iletisim.html"] + [f"https://www.jetcilingir34.com/hizmetler/{slug}.html" for slug in SERVICE_PAGES] + district_urls + neighborhood_urls
            xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">" + "".join(f"<url><loc>{url}</loc><changefreq>weekly</changefreq></url>" for url in urls) + "</urlset>"
            content = xml.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/xml; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if path == "/iletisim.html":
            content = render_template(path, CONTACT_TEMPLATE_PATH)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if path == "/hakkimizda.html":
            content = render_template(path, ABOUT_TEMPLATE_PATH)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if path.startswith("/hizmetler/") and path.endswith(".html"):
            service_slug = path.removeprefix("/hizmetler/").removesuffix(".html")
            if service_slug not in SERVICE_PAGES:
                self.send_error(404, "Not found")
                return
            content = render_template(path, SERVICE_TEMPLATE_PATH)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        parts = path.strip("/").split("/")
        district_valid = len(parts) == 2 and parts[0] == "istanbul" and parts[1].endswith("-cilingir") and parts[1].removesuffix("-cilingir") in DISTRICT_BY_SLUG
        neighborhood_valid = len(parts) == 3 and parts[0] == "istanbul" and parts[1] in DISTRICT_BY_SLUG and parts[2].endswith("-cilingir") and parts[2].removesuffix("-cilingir") in {slugify(name) for name in NEIGHBORHOODS_BY_SLUG.get(parts[1], [])}
        valid = path == "/" or district_valid or neighborhood_valid
        if not valid:
            self.send_error(404, "Not found")
            return
        content = render_template(path)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, fmt, *args):
        pass


def run():
    ThreadingHTTPServer(("0.0.0.0", 5000), Handler).serve_forever()


if __name__ == "__main__":
    run()
