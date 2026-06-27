from django.core.management.base import BaseCommand
from django.conf import settings
from portfolio.models import WebsiteTemplate
from django.core.files.base import ContentFile
from playwright.sync_api import sync_playwright
import os
import time

class Command(BaseCommand):
    help = 'Auto-generate thumbnails for all website templates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            type=str,
            help='Generate thumbnail for a single template by slug',
        )
        parser.add_argument(
            '--width',
            type=int,
            default=1280,
            help='Viewport width (default: 1280)',
        )
        parser.add_argument(
            '--height',
            type=int,
            default=800,
            help='Viewport height (default: 800)',
        )

    def handle(self, *args, **options):
        slug   = options.get('slug')
        width  = options['width']
        height = options['height']

        if slug:
            templates = WebsiteTemplate.objects.filter(slug=slug)
            if not templates.exists():
                self.stderr.write(self.style.ERROR(f'No template found with slug: {slug}'))
                return
        else:
            templates = WebsiteTemplate.objects.all()

        if not templates.exists():
            self.stderr.write(self.style.WARNING('No templates found. Add some in admin first.'))
            return

        self.stdout.write(self.style.MIGRATE_HEADING(
            f'\n🎨 Generating thumbnails for {templates.count()} template(s)...\n'
        ))

        with sync_playwright() as p:
            browser = p.chromium.launch()

            for site in templates:
                if not site.template_name:
                    self.stdout.write(self.style.WARNING(f'  ⚠ Skipping "{site.title}" — no template_name set'))
                    continue

                template_path = os.path.join(settings.BASE_DIR, 'templates', site.template_name)

                if not os.path.exists(template_path):
                    self.stdout.write(self.style.WARNING(f'  ⚠ Skipping "{site.title}" — file not found: {template_path}'))
                    continue

                self.stdout.write(f'  📸 Screenshotting: {site.title}')

                try:
                    page = browser.new_page(viewport={'width': width, 'height': height})

                    # Hide the showcase bar before screenshotting
                    file_url = f'file://{template_path}'
                    page.goto(file_url, wait_until='networkidle', timeout=15000)

                    # Wait for fonts and images
                    time.sleep(1.5)

                    # Hide the fixed showcase bar so it doesn't appear in thumbnail
                    page.evaluate("""
                        const bar = document.querySelector('.showcase-bar, [class*="showcase"]');
                        if (bar) bar.style.display = 'none';
                        const spacer = document.querySelector('body > div:last-of-type');
                        if (spacer) spacer.style.display = 'none';
                    """)

                    # Take screenshot
                    screenshot_bytes = page.screenshot(
                        full_page=False,
                        clip={'x': 0, 'y': 0, 'width': width, 'height': height}
                    )

                    # Save to model thumbnail field
                    filename = f'thumbnails/{site.slug}.png'

                    # Delete old thumbnail if exists
                    if site.thumbnail:
                        old_path = os.path.join(settings.MEDIA_ROOT, str(site.thumbnail))
                        if os.path.exists(old_path):
                            os.remove(old_path)

                    site.thumbnail.save(
                        f'{site.slug}.png',
                        ContentFile(screenshot_bytes),
                        save=True
                    )

                    self.stdout.write(self.style.SUCCESS(f'  ✅ Done: {site.title} → {filename}'))
                    page.close()

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ❌ Failed: {site.title} — {str(e)}'))

            browser.close()

        self.stdout.write(self.style.SUCCESS('\n✨ All thumbnails generated!\n'))
