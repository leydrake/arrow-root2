from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pages.models import AdminProfile

class Command(BaseCommand):
    help = 'Create default admin user with credentials'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username for the admin user (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@example.com',
            help='Email for the admin user (default: admin@example.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Password for the admin user (default: admin123)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists!')
            )
            return

        # Create superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        # Create admin profile
        AdminProfile.objects.create(
            user=user,
            is_admin=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created admin user!\n'
                f'Username: {username}\n'
                f'Email: {email}\n'
                f'Password: {password}\n'
                f'You can now login at /admin/ or /login/'
            )
        )
