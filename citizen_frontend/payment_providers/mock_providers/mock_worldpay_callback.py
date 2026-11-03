from django.views.decorators.http import require_POST


@require_POST
def callback(request):
    pass
