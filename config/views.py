from django.http import HttpResponse
from django.urls import reverse


def robots_txt(request):
    base_url = 'https://www.yiepay.net'
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /api_v1/',
        'Disallow: /accounts/password_reset/',
        'Disallow: /accounts/password_change/',
        'Sitemap: {}/sitemap.xml'.format(base_url),
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


def sitemap_xml(request):
    base_url = 'https://www.yiepay.net'
    paths = [
        reverse('home'),
        reverse('new_user'),
        reverse('contact'),
    ]
    urls = '\n'.join(
        (
            '  <url>\n'
            '    <loc>{}{}</loc>\n'
            '    <changefreq>weekly</changefreq>\n'
            '    <priority>{}</priority>\n'
            '  </url>'
        ).format(base_url, path, '1.0' if path == '/' else '0.6')
        for path in paths
    )
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '{}\n'
        '</urlset>'
    ).format(urls)
    return HttpResponse(content, content_type='application/xml')
