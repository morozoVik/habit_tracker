from django.core.management.base import BaseCommand
from habits.tasks import send_telegram_notification


class Command(BaseCommand):
    help = "Test Telegram notification"

    def add_arguments(self, parser):
        parser.add_argument("chat_id", type=str, help="Telegram Chat ID")
        parser.add_argument("message", type=str, help="Message to send")

    def handle(self, *args, **options):
        chat_id = options["chat_id"]
        message = options["message"]

        result = send_telegram_notification(chat_id, message)

        if result:
            self.stdout.write(
                self.style.SUCCESS(f"Message sent successfully: {result}")
            )
        else:
            self.stdout.write(self.style.ERROR("Failed to send message"))
