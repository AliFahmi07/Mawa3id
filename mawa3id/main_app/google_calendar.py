# main_app/google_calendar.py

#####################################################
#This code is generated using AI for API connection.
#####################################################


from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar.events"
TOKEN_URI = "https://oauth2.googleapis.com/token"


def _get_owner(booking):
    return booking.slot.business.owner


def _get_google_credentials_for_user(user):
    app = SocialApp.objects.get(provider="google")
    account = SocialAccount.objects.get(user=user, provider="google")
    token = SocialToken.objects.get(account=account)

    refresh_token = token.token_secret or None

    return Credentials(
        token=token.token,
        refresh_token=refresh_token,
        token_uri=TOKEN_URI,
        client_id=app.client_id,
        client_secret=app.secret,
        scopes=[CALENDAR_SCOPE],
    )


def _event_body_from_booking(booking):
    slot = booking.slot
    start_dt = slot.start
    end_dt = start_dt + timedelta(minutes=slot.duration)

    start_iso = timezone.localtime(start_dt).isoformat()
    end_iso = timezone.localtime(end_dt).isoformat()

    service_name = slot.service.name if slot.service_id else "Appointment"

    return {
        "summary": f"{service_name} — {slot.business.name}",
        "description": booking.notes or "",
        "start": {"dateTime": start_iso, "timeZone": settings.TIME_ZONE},
        "end": {"dateTime": end_iso, "timeZone": settings.TIME_ZONE},
    }


def create_event_for_booking(booking, calendar_id="primary"):
    owner = _get_owner(booking)
    creds = _get_google_credentials_for_user(owner)
    service = build("calendar", "v3", credentials=creds)

    body = _event_body_from_booking(booking)
    created = service.events().insert(calendarId=calendar_id, body=body).execute()

    booking.google_calendar_id = calendar_id
    booking.google_event_id = created["id"]
    booking.save(update_fields=["google_calendar_id", "google_event_id"])

    return created
