import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
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

            # Request fullscreen on form submit (handled in template JS)
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


def reason_view(request, rating):
    device = get_active_device(request)
    if not device:
        return redirect("core:setup")

    rating = rating.upper()
    reasons = Reason.objects.filter(rating=rating, is_active=True)
    return render(
        request,
        "survey/reason.html",
        {
            "rating": rating,
            "rating_display": dict(Rating.choices).get(rating, rating),
            "reasons": reasons,
            "hotline": device.hotline,
        },
    )


def submit_response(request):
    device = get_active_device(request)
    if not device:
        return redirect("core:setup")

    if request.method == "POST":
        rating = request.POST.get("rating")
        reason_id = request.POST.get("reason_id")
        reason = get_object_or_404(Reason, id=reason_id) if reason_id else None

        SurveyResponse.objects.create(
            rating=rating,
            reason=reason,
            device=device,
        )
        return redirect("core:thank_you")

    return redirect("core:rating")


def thank_you_view(request):
    device = get_active_device(request)
    if not device:
        return redirect("core:setup")

    return render(
        request,
        "survey/thank_you.html",
        {
            "hotline": device.hotline,
        },
    )


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
        passcode = data.get("passcode", "").strip()
        action_ids = data.get("actions", [])
        comment = data.get("comment", "").strip()

        try:
            cleaner = Cleaner.objects.get(
                cleaner_id=cleaner_id, passcode=passcode, is_active=True
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
