from django.views import View
from django.http import JsonResponse
from django.db.models import Q

from partners.models import Partner


class PartnerSearchView(View):
    """Devuelve JSON con partners que coincidan con q (nombre o short_name)."""

    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '').strip()
        results = []
        if q:
            qs = (
                Partner.objects.filter(is_active=True)
                .filter(Q(name__icontains=q) | Q(short_name__icontains=q))
                .order_by('name')[:15]
            )
            for p in qs:
                results.append({
                    'id': p.id,
                    'name': p.name,
                    'short_name': p.short_name or '',
                    'tax_id': p.business_tax_id,
                })
        return JsonResponse({'results': results})
