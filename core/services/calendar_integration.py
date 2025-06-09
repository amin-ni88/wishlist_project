from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.conf import settings
from core.models import WishList
from datetime import datetime, timedelta
import os.path
import pickle
from typing import Optional


class CalendarIntegration:
    """Service for integrating wishlists with calendar services"""

    SCOPES = ['https://www.googleapis.com/auth/calendar.events']
    CALENDAR_COLORS = {
        'birthday': '2',  # Light blue
        'anniversary': '4',  # Purple
        'wedding': '6',  # Orange
        'other': '1',  # Light green
    }

    @staticmethod
    def get_credentials(user_id: int) -> Optional[Credentials]:
        """Get or refresh Google Calendar credentials"""
        creds = None
        token_path = f'tokens/calendar_token_{user_id}.pickle'

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.GOOGLE_CALENDAR_CREDENTIALS,
                    CalendarIntegration.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        return creds

    @staticmethod
    def add_to_calendar(wishlist: WishList, user_id: int) -> bool:
        """Add wishlist occasion to Google Calendar"""
        try:
            creds = CalendarIntegration.get_credentials(user_id)
            if not creds:
                return False

            service = build('calendar', 'v3', credentials=creds)

            # Set event details
            occasion_type = wishlist.occasion_type.lower()
            color_id = CalendarIntegration.CALENDAR_COLORS.get(
                occasion_type,
                CalendarIntegration.CALENDAR_COLORS['other']
            )

            event = {
                'summary': wishlist.title,
                'description': (
                    f"{wishlist.description}\n\n"
                    f"Wishlist Link: {settings.SITE_URL}/wishlists/{wishlist.id}"
                ),
                'start': {
                    'date': wishlist.occasion_date.isoformat()
                },
                'end': {
                    'date': wishlist.occasion_date.isoformat()
                },
                'colorId': color_id,
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 24 * 60}
                    ]
                }
            }

            # Add recurring event if needed
            if wishlist.is_recurring:
                event['recurrence'] = ['RRULE:FREQ=YEARLY']

            event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            # Store event ID for future reference
            wishlist.calendar_event_id = event['id']
            wishlist.save(update_fields=['calendar_event_id'])

            return True

        except Exception as e:
            print(f"Error adding event to calendar: {str(e)}")
            return False

    @staticmethod
    def update_calendar_event(wishlist: WishList, user_id: int) -> bool:
        """Update existing calendar event"""
        if not wishlist.calendar_event_id:
            return CalendarIntegration.add_to_calendar(wishlist, user_id)

        try:
            creds = CalendarIntegration.get_credentials(user_id)
            if not creds:
                return False

            service = build('calendar', 'v3', credentials=creds)

            # Get existing event
            event = service.events().get(
                calendarId='primary',
                eventId=wishlist.calendar_event_id
            ).execute()

            # Update event details
            event['summary'] = wishlist.title
            event['description'] = (
                f"{wishlist.description}\n\n"
                f"Wishlist Link: {settings.SITE_URL}/wishlists/{wishlist.id}"
            )
            event['start']['date'] = wishlist.occasion_date.isoformat()
            event['end']['date'] = wishlist.occasion_date.isoformat()

            updated_event = service.events().update(
                calendarId='primary',
                eventId=wishlist.calendar_event_id,
                body=event
            ).execute()

            return bool(updated_event)

        except Exception as e:
            print(f"Error updating calendar event: {str(e)}")
            return False

    @staticmethod
    def remove_from_calendar(wishlist: WishList, user_id: int) -> bool:
        """Remove wishlist occasion from calendar"""
        if not wishlist.calendar_event_id:
            return True

        try:
            creds = CalendarIntegration.get_credentials(user_id)
            if not creds:
                return False

            service = build('calendar', 'v3', credentials=creds)

            service.events().delete(
                calendarId='primary',
                eventId=wishlist.calendar_event_id
            ).execute()

            wishlist.calendar_event_id = None
            wishlist.save(update_fields=['calendar_event_id'])

            return True

        except Exception as e:
            print(f"Error removing calendar event: {str(e)}")
            return False
