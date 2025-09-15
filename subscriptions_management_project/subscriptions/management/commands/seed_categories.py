from django.core.management.base import BaseCommand
from subscriptions.models import Category

class Command(BaseCommand):
    help = 'Seed the database with default categories'

    def handle(self, *args, **options):
        # Define categories data
        categories_data = [
            # Main categories
            {
                'name': 'Entertainment',
                'description': 'Streaming services, gaming, and entertainment subscriptions',
                'parent': None
            },
            {
                'name': 'Productivity',
                'description': 'Software and tools for work and productivity',
                'parent': None
            },
            {
                'name': 'Cloud Services',
                'description': 'Cloud storage, hosting, and infrastructure services',
                'parent': None
            },
            {
                'name': 'Education',
                'description': 'Online courses, learning platforms, and educational content',
                'parent': None
            },
            {
                'name': 'Health & Fitness',
                'description': 'Health tracking, fitness apps, and wellness services',
                'parent': None
            },
            {
                'name': 'News & Media',
                'description': 'News subscriptions, magazines, and media content',
                'parent': None
            },
            {
                'name': 'Shopping',
                'description': 'E-commerce memberships and shopping services',
                'parent': None
            },
            {
                'name': 'Finance',
                'description': 'Financial services, banking, and investment tools',
                'parent': None
            },
            {
                'name': 'Other',
                'description': 'Anything else',
                'parent': None
            },
        ]

        # Subcategories
        subcategories_data = [
            # Entertainment subcategories
            {'name': 'Video Streaming', 'description': 'Netflix, Hulu, Disney+, etc.', 'parent_name': 'Entertainment'},
            {'name': 'Music Streaming', 'description': 'Spotify, Apple Music, etc.', 'parent_name': 'Entertainment'},
            {'name': 'Gaming', 'description': 'Xbox Game Pass, PlayStation Plus, etc.', 'parent_name': 'Entertainment'},
            
            # Productivity subcategories
            {'name': 'Office Software', 'description': 'Microsoft 365, Google Workspace, etc.', 'parent_name': 'Productivity'},
            {'name': 'Design Tools', 'description': 'Adobe Creative Suite, Figma, etc.', 'parent_name': 'Productivity'},
            {'name': 'Project Management', 'description': 'Asana, Trello, Monday.com, etc.', 'parent_name': 'Productivity'},
            
            # Cloud Services subcategories
            {'name': 'Storage', 'description': 'Dropbox, Google Drive, OneDrive, etc.', 'parent_name': 'Cloud Services'},
            {'name': 'Hosting', 'description': 'AWS, DigitalOcean, Heroku, etc.', 'parent_name': 'Cloud Services'},
            {'name': 'Backup', 'description': 'Backblaze, Carbonite, etc.', 'parent_name': 'Cloud Services'},
        ]

        # Create main categories
        created_count = 0
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'parent': cat_data['parent']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )

        # Create subcategories
        for subcat_data in subcategories_data:
            try:
                parent = Category.objects.get(name=subcat_data['parent_name'])
                subcategory, created = Category.objects.get_or_create(
                    name=subcat_data['name'],
                    defaults={
                        'description': subcat_data['description'],
                        'parent': parent
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created subcategory: {subcategory.name} under {parent.name}')
                    )
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Parent category "{subcat_data["parent_name"]}" not found for subcategory "{subcat_data["name"]}"')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} categories')
        )