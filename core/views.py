import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import (
    Cleaner,
    CleanerAction,
    CleanerLog,
    Device,
    Rating,
    Reason,
    SurveyResponse,
)


def get_active_device(request):
    """Returns the Device bound to this session if it's still active, else None."""
    device_id = request.session.get("device_id")
    if not device_id:
        return None

    device = Device.objects.filter(device_id=device_id, is_active=True).first()
    if not device:
        request.session.pop("device_id", None)
        return None

    return device


def setup_view(request):
    """One-time device activation. Device must be pre-created by admin."""
    device = get_active_device(request)
    if device:
        return redirect("core:rating")

    error = None
    if request.method == "POST":
        device_id = request.POST.get("device_id", "").strip()
        password = request.POST.get("password", "").strip()

        device = Device.objects.filter(device_id=device_id).first()

        if not device:
            error = "Device ID not found. Contact admin to register this device."
        elif device.password != password:
            error = "Incorrect password."
        else:
            if not device.is_active:
                device.is_active = True
                device.save(update_fields=["is_active"])

            request.session["device_id"] = device.device_id

            return redirect("core:rating")

    return render(request, "survey/setup.html", {"error": error})


def rating_view(request):
    device = get_active_device(request)
    if not device:
        return redirect("core:setup")

    return render(
        request,
        "survey/rating.html",
        {
            "ratings": Rating.choices,
            "hotline": device.hotline,
        },
    )


def get_reasons_view(request, rating):
    """Returns reasons for a given rating as JSON (used by the modal)."""
    device = get_active_device(request)
    if not device:
        return JsonResponse({"error": "Device not active"}, status=403)

    rating = rating.upper()
    reasons = list(
        Reason.objects.filter(rating=rating, is_active=True).values("id", "text")
    )
    return JsonResponse({"rating": rating, "reasons": reasons})


def submit_response(request):
    device = get_active_device(request)
    if not device:
        return JsonResponse({"error": "Device not active"}, status=403)

    if request.method == "POST":
        data = json.loads(request.body)
        rating = data.get("rating", "").upper()
        reason_ids = data.get("reason_ids", [])

        if rating not in dict(Rating.choices):
            return JsonResponse({"error": "Invalid rating"}, status=400)

        survey = SurveyResponse.objects.create(
            rating=rating,
            device=device,
        )
        if reason_ids:
            survey.reasons.set(Reason.objects.filter(id__in=reason_ids))

        return JsonResponse({"success": True})

    return JsonResponse({"error": "Method not allowed"}, status=405)


def cleaner_log_view(request):
    device = get_active_device(request)
    if not device:
        return JsonResponse({"error": "Device not active"}, status=403)

    if request.method == "GET":
        actions = list(
            CleanerAction.objects.filter(is_active=True).values("id", "name")
        )
        return JsonResponse({"actions": actions})

    if request.method == "POST":
        data = json.loads(request.body)
        cleaner_id = data.get("cleaner_id", "").strip()
        pin = data.get("pin", "").strip()
        action_ids = data.get("actions", [])
        comment = data.get("comment", "").strip()

        try:
            cleaner = Cleaner.objects.get(
                cleaner_id=cleaner_id, pin=pin, is_active=True
            )
        except Cleaner.DoesNotExist:
            return JsonResponse({"error": "Invalid cleaner ID or passcode"}, status=400)

        # Verify-only call (no real actions saved)
        if comment == "__verify_only__":
            return JsonResponse({"success": True, "cleaner_name": cleaner.name})

        log = CleanerLog.objects.create(
            cleaner=cleaner,
            device=device,
            comment=comment,
        )
        log.actions.set(CleanerAction.objects.filter(id__in=action_ids))

        return JsonResponse({"success": True, "cleaner_name": cleaner.name})
