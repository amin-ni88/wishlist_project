from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
from core.services.analytics import SubscriptionAnalytics

class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def subscription_metrics(self, request):
        """Get subscription metrics"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
        metrics = SubscriptionAnalytics.get_subscription_metrics(
            start_date,
            end_date
        )
        return Response(metrics)
    
    @action(detail=False, methods=['get'])
    def subscription_trends(self, request):
        """Get subscription trends"""
        trends = SubscriptionAnalytics.get_subscription_trends()
        return Response(trends)
