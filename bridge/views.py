from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .services import WooBridgeService
import json

def INDEX(request):
    return HttpResponse("Hello, world. You're at the bridge index.")

@csrf_exempt
def CREATE_ORDER(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    try:
        body = json.loads(request.body)

        items = body.get("items", [])

        # Prefix billing keys
        billing = {
            f"billing_{k}": v
            for k, v in body.get("billing", {}).items()
        }

        # Prefix shipping keys
        shipping = {
            f"shipping_{k}": v
            for k, v in body.get("shipping", {}).items()
        }

        service = WooBridgeService()
        redirect_url = service.process_order(items, billing, shipping)

        return JsonResponse({
            "status": "success",
            "payment_url": redirect_url
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)