# debug_urls.py - Coloca este archivo en la raíz del proyecto
import os
import django
from django.urls import get_resolver

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def show_urls(urllist, depth=0):
    for entry in urllist:
        pattern = entry.pattern.regex.pattern
        if hasattr(entry, 'url_patterns'):
            print("  " * depth + f"📂 {pattern}")
            show_urls(entry.url_patterns, depth + 1)
        else:
            print("  " * depth + f"📄 {pattern}")

if __name__ == "__main__":
    resolver = get_resolver(None)
    show_urls(resolver.url_patterns)