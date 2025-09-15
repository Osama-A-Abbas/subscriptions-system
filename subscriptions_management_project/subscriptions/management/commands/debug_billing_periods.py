from django.core.management.base import BaseCommand
from django.utils import timezone
from subscriptions.models import Subscription
from datetime import date


class Command(BaseCommand):
    help = 'Debug billing periods and current period detection'
    
    def add_arguments(self, parser):
        parser.add_argument('subscription_id', type=int, help='Subscription ID to debug')
    
    def handle(self, *args, **options):
        subscription_id = options['subscription_id']
        
        try:
            subscription = Subscription.objects.get(pk=subscription_id)
        except Subscription.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Subscription {subscription_id} not found'))
            return
        
        self.stdout.write(f'\n=== Debugging Subscription: {subscription.name} ===')
        self.stdout.write(f'ID: {subscription.pk}')
        self.stdout.write(f'Start Date: {subscription.start_date}')
        self.stdout.write(f'Billing Cycle: {subscription.billing_cycle}')
        self.stdout.write(f'Duration Months: {subscription.duration_months}')
        self.stdout.write(f'Duration Years: {subscription.duration_years}')
        self.stdout.write(f'Total Payments: {subscription.get_total_payments()}')
        self.stdout.write(f'Today: {timezone.now().date()}')
        
        # Get billing periods
        periods = subscription.get_billing_periods()
        
        self.stdout.write(f'\n=== Billing Periods ({len(periods)} total) ===')
        for i, period in enumerate(periods, 1):
            status = []
            if period['is_current']:
                status.append('CURRENT')
            if period['is_past_due']:
                status.append('PAST DUE')
            if period['is_paid']:
                status.append('PAID')
            if not status:
                status.append('FUTURE')
            
            status_str = ' | '.join(status)
            
            self.stdout.write(
                f'Period {i}: {period["start"]} to {period["end"]} '
                f'[{status_str}] - ${period["amount"]}'
            )
        
        # Check existing payments
        payments = subscription.payments.all()
        self.stdout.write(f'\n=== Existing Payment Records ({payments.count()} total) ===')
        for payment in payments:
            self.stdout.write(
                f'Payment: {payment.billing_period_start} to {payment.billing_period_end} '
                f'- ${payment.amount} - {"PAID" if payment.is_paid else "UNPAID"}'
            )
        
        self.stdout.write('\n=== Summary ===')
        current_periods = [p for p in periods if p['is_current']]
        past_due_periods = [p for p in periods if p['is_past_due']]
        
        self.stdout.write(f'Current periods: {len(current_periods)}')
        self.stdout.write(f'Past due periods: {len(past_due_periods)}')
        
        if current_periods:
            self.stdout.write(f'Current period: {current_periods[0]["start"]} to {current_periods[0]["end"]}')
        else:
            self.stdout.write('No current period found!')
