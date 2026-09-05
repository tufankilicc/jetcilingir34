from pathlib import Path
from datetime import datetime, timezone
import re
import shutil

import app


BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"
PUBLIC_DOMAIN = "https://www.jetcilingir34.com"
BUILD_DATE = datetime.now(timezone.utc).date().isoformat()
YANDEX_VERIFICATION_FILE = "yandex_d894ac1085b171db.html"
YANDEX_VERIFICATION_HTML = "<html><body>Verification: d894ac1085b171db</body></html>\n"


def clean_text(content):
    content = re.sub(r"https?://(?:www\\.)?jetcilingir\\.[A-Za-z]{2,}", PUBLIC_DOMAIN, content)
    return re.sub(r"info@jetcilingir\\.[A-Za-z]{2,}", "info@jetcilingir34.com", content)


def write_page(url_path, template_path, output_path):
    content = app.render_template(url_path, template_path).decode("utf-8")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(clean_text(content), encoding="utf-8")


def main():
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    PUBLIC_DIR.mkdir()
    shutil.copytree(BASE_DIR / "assets", PUBLIC_DIR / "assets")

    write_page("/", app.TEMPLATE_PATH, PUBLIC_DIR / "index.html")
    write_page("/hakkimizda.html", app.ABOUT_TEMPLATE_PATH, PUBLIC_DIR / "hakkimizda.html")
    write_page("/iletisim.html", app.CONTACT_TEMPLATE_PATH, PUBLIC_DIR / "iletisim.html")
    write_page("/404.html", BASE_DIR / "templates" / "404.html", PUBLIC_DIR / "404.html")

    service_urls = []
    for slug in app.SERVICE_PAGES:
        url_path = f"/hizmetler/{slug}.html"
        write_page(url_path, app.SERVICE_TEMPLATE_PATH, PUBLIC_DIR / "hizmetler" / f"{slug}.html")
        service_urls.append(f"{PUBLIC_DOMAIN}{url_path}")

    district_urls = []
    neighborhood_urls = []
    for district in app.DISTRICTS:
        district_slug = app.slugify(district)
        district_path = f"/istanbul/{district_slug}-cilingir"
        write_page(district_path, app.TEMPLATE_PATH, PUBLIC_DIR / "istanbul" / f"{district_slug}-cilingir" / "index.html")
        district_urls.append(f"{PUBLIC_DOMAIN}{district_path}")
        for neighborhood in app.NEIGHBORHOODS_BY_SLUG.get(district_slug, []):
            neighborhood_slug = app.slugify(neighborhood)
            neighborhood_path = f"/istanbul/{district_slug}/{neighborhood_slug}-cilingir"
            write_page(neighborhood_path, app.TEMPLATE_PATH, PUBLIC_DIR / "istanbul" / district_slug / f"{neighborhood_slug}-cilingir" / "index.html")
            neighborhood_urls.append(f"{PUBLIC_DOMAIN}{neighborhood_path}")

    urls = [f"{PUBLIC_DOMAIN}/", f"{PUBLIC_DOMAIN}/hakkimizda.html", f"{PUBLIC_DOMAIN}/iletisim.html"] + service_urls + district_urls + neighborhood_urls
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{url}</loc><lastmod>{BUILD_DATE}</lastmod><changefreq>weekly</changefreq></url>" for url in urls) + "</urlset>\n"
    (PUBLIC_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (PUBLIC_DIR / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {PUBLIC_DOMAIN}/sitemap.xml\n", encoding="utf-8")
    (PUBLIC_DIR / YANDEX_VERIFICATION_FILE).write_text(YANDEX_VERIFICATION_HTML, encoding="utf-8")
    print(f"Generated {len(urls)} pages in {PUBLIC_DIR}")


if __name__ == "__main__":
    main()
