from django.http import JsonResponse


def health_check(request):
    """Health check endpoint for Docker / load balancers."""
    return JsonResponse({"status": "ok"})
