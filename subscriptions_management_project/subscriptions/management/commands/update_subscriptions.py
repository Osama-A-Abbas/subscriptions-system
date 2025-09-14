from django.core.management.base import BaseCommand
from django.utils import timezone
from subscriptions.models import Subscription
from dateutil.relativedelta import relativedelta

class Command(BaseCommand):
    help = 'Update subscription statuses and handle auto-renewals'
    
    def handle(self, *args, **options):
        today = timezone.now().date()
        updated_count = 0
        
        for subscription in Subscription.objects.filter(is_active=True):
            # Check if subscription has ended
            if subscription.ending_date and subscription.ending_date <= today:
                subscription.is_active = False
                subscription.save()
                updated_count += 1
                self.stdout.write(f'Ended subscription: {subscription.name}')
                continue
            
            # Check if renewal date has passed
            if subscription.renewal_date <= today:
                # Check if current period is paid
                if subscription.billing_cycle == 'monthly':
                    current_period_start = subscription.renewal_date - relativedelta(months=1)
                else:
                    current_period_start = subscription.renewal_date - relativedelta(years=1)

                has_payment = subscription.payments.filter(
                    billing_period_start=current_period_start,
                    is_paid=True
                ).exists()
                
                if has_payment and subscription.should_auto_renew():
                    # Auto-renew to next period
                    subscription.renewal_date = subscription.calculate_next_renewal()
                    subscription.save()
                    updated_count += 1
                    self.stdout.write(f'Auto-renewed: {subscription.name}')
                else:
                    self.stdout.write(f'No auto-renewal for: {subscription.name} (unpaid or disabled)')
        
        self.stdout.write(f'Updated {updated_count} subscriptions')