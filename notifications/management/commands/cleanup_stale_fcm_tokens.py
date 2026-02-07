from django.core.management.base import BaseCommand
from notifications.services import NotificationService


class Command(BaseCommand):
    help = "Remove FCM device tokens not used in the last N days"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", type=int, default=30,
            help="Remove tokens not used in this many days (default: 30)"
        )

    def handle(self, *args, **options):
        days = options["days"]
        count = NotificationService.cleanup_stale_tokens(days=days)
        self.stdout.write(
            self.style.SUCCESS(
                f"Cleaned up {count} stale FCM tokens (older than {days} days)"
            )
        )
