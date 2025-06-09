from django.db.models import Count, Sum, Avg, F
from django.db.models.functions import TruncDate, ExtractMonth
from django.utils import timezone
from datetime import timedelta
from core.models import UserSubscription, Transaction, Plan

class SubscriptionAnalytics:
    @staticmethod
    def get_subscription_metrics(start_date=None, end_date=None):
        """Get key subscription metrics"""
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()
            
        metrics = {
            'total_active_subscriptions': UserSubscription.objects.filter(
                is_active=True
            ).count(),
            
            'subscriptions_by_plan': UserSubscription.objects.filter(
                is_active=True
            ).values('plan__name').annotate(
                count=Count('id')
            ),
            
            'new_subscriptions': UserSubscription.objects.filter(
                created_at__range=(start_date, end_date)
            ).count(),
            
            'churn_rate': SubscriptionAnalytics._calculate_churn_rate(
                start_date,
                end_date
            ),
            
            'revenue_metrics': SubscriptionAnalytics._calculate_revenue_metrics(
                start_date,
                end_date
            ),
            
            'conversion_rate': SubscriptionAnalytics._calculate_conversion_rate(
                start_date,
                end_date
            )
        }
        
        return metrics
    
    @staticmethod
    def _calculate_churn_rate(start_date, end_date):
        """Calculate subscriber churn rate"""
        total_start = UserSubscription.objects.filter(
            created_at__lte=start_date,
            is_active=True
        ).count()
        
        churned = UserSubscription.objects.filter(
            end_date__range=(start_date, end_date),
            is_active=False,
            auto_renew=False
        ).count()
        
        return (churned / total_start * 100) if total_start > 0 else 0
    
    @staticmethod
    def _calculate_revenue_metrics(start_date, end_date):
        """Calculate revenue-related metrics"""
        transactions = Transaction.objects.filter(
            created_at__range=(start_date, end_date),
            transaction_type='PLAN_PURCHASE',
            status='SUCCESS'
        )
        
        return {
            'total_revenue': transactions.aggregate(
                total=Sum('amount')
            )['total'] or 0,
            
            'revenue_by_plan': transactions.values(
                'subscription__plan__name'
            ).annotate(
                total=Sum('amount')
            ),
            
            'average_revenue_per_user': transactions.values(
                'user'
            ).annotate(
                avg=Avg('amount')
            ).aggregate(
                total_avg=Avg('avg')
            )['total_avg'] or 0
        }
    
    @staticmethod
    def _calculate_conversion_rate(start_date, end_date):
        """Calculate free to paid conversion rate"""
        free_users = UserSubscription.objects.filter(
            created_at__range=(start_date, end_date),
            plan__type='FREE'
        ).values('user').distinct().count()
        
        converted = UserSubscription.objects.filter(
            created_at__range=(start_date, end_date),
            plan__type__in=['BASIC', 'PREMIUM', 'BUSINESS'],
            user__in=UserSubscription.objects.filter(
                plan__type='FREE'
            ).values('user')
        ).values('user').distinct().count()
        
        return (converted / free_users * 100) if free_users > 0 else 0
    
    @staticmethod
    def get_subscription_trends():
        """Get subscription trends over time"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=180)
        
        return {
            'daily_subscriptions': UserSubscription.objects.filter(
                created_at__range=(start_date, end_date)
            ).annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                count=Count('id')
            ).order_by('date'),
            
            'monthly_revenue': Transaction.objects.filter(
                created_at__range=(start_date, end_date),
                transaction_type='PLAN_PURCHASE',
                status='SUCCESS'
            ).annotate(
                month=ExtractMonth('created_at')
            ).values('month').annotate(
                total=Sum('amount')
            ).order_by('month'),
            
            'plan_distribution': UserSubscription.objects.filter(
                is_active=True
            ).values('plan__name').annotate(
                count=Count('id')
            ).order_by('-count')
        }
