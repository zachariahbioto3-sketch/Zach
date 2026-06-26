from django.shortcuts import render, get_object_or_404
from .models import WebsiteTemplate

def home(request):
    category = request.GET.get('category', '')
    templates = WebsiteTemplate.objects.all()
    if category:
        templates = templates.filter(category=category)
    categories = WebsiteTemplate.objects.values_list('category', 'category').distinct()
    return render(request, 'portfolio/home.html', {
        'templates': templates,
        'categories': categories,
        'active_category': category,
    })

def preview(request, slug):
    site = get_object_or_404(WebsiteTemplate, slug=slug)
    # Render the stored template if it exists, else fallback
    try:
        return render(request, site.template_name, {'site': site})
    except Exception:
        return render(request, 'portfolio/preview_fallback.html', {'site': site})
