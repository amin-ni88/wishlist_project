from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Plan, UserSubscription
from core.serializers import PlanSerializer, UserSubscriptionSerializer
from core.services.payment import PaymentService
from django.utils import timezone
from decimal import Decimal

class SubscriptionManagementViewSet(viewsets.ModelViewSet):
    """ViewSet for managing subscription upgrades and downgrades"""
    
    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def upgrade(self, request, pk=None):
        """Upgrade to a higher tier plan"""
        current_subscription = self.get_object()
        new_plan_id = request.data.get('plan_id')
        
        try:
            new_plan = Plan.objects.get(id=new_plan_id)
            
            # Validate upgrade
            if new_plan.get_price(current_subscription.duration_type) <= \
               current_subscription.plan.get_price(current_subscription.duration_type):
                return Response(
                    {'error': 'New plan must be of higher tier'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate remaining value of current subscription
            days_left = (current_subscription.end_date - timezone.now()).days
            daily_rate = current_subscription.plan.get_price(
                current_subscription.duration_type
            ) / 30
            remaining_value = Decimal(days_left * daily_rate)
            
            # Calculate new plan cost
            new_plan_price = new_plan.get_price(current_subscription.duration_type)
            upgrade_cost = new_plan_price - remaining_value
            
            # Process payment
            if upgrade_cost > 0:
                transaction = PaymentService.process_plan_purchase(
                    user=request.user,
                    plan=new_plan,
                    duration_type=current_subscription.duration_type,
                    payment_method='WALLET',
                    gateway_id=None
                )[0]
                
                if transaction.status != 'SUCCESS':
                    return Response(
                        {'error': 'Insufficient funds'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Update subscription
            current_subscription.plan = new_plan
            current_subscription.save()
            
            return Response(
                UserSubscriptionSerializer(current_subscription).data
            )
            
        except Plan.DoesNotExist:
            return Response(
                {'error': 'Invalid plan ID'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def downgrade(self, request, pk=None):
        """Downgrade to a lower tier plan"""
        current_subscription = self.get_object()
        new_plan_id = request.data.get('plan_id')
        
        try:
            new_plan = Plan.objects.get(id=new_plan_id)
            
            # Validate downgrade
            if new_plan.get_price(current_subscription.duration_type) >= \
               current_subscription.plan.get_price(current_subscription.duration_type):
                return Response(
                    {'error': 'New plan must be of lower tier'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Schedule downgrade for end of current period
            current_subscription.next_plan = new_plan
            current_subscription.save()
            
            return Response({
                'message': 'Plan will be downgraded at the end of current period',
                'effective_date': current_subscription.end_date
            })
            
        except Plan.DoesNotExist:
            return Response(
                {'error': 'Invalid plan ID'},
                status=status.HTTP_404_NOT_FOUND
            )
