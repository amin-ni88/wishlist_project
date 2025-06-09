import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from core.models import WishListItem
from datetime import datetime
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


@dataclass
class PricePoint:
    price: float
    timestamp: datetime
    source: str


class PriceTracker:
    """Service for tracking item prices across different platforms"""

    SUPPORTED_DOMAINS = {
        'digikala.com': 'extract_digikala_price',
        'amazon.com': 'extract_amazon_price',
        'divar.ir': 'extract_divar_price',
    }

    @staticmethod
    def update_price_history(item: WishListItem) -> bool:
        """Update price history for an item"""
        if not item.product_url:
            return False

        try:
            domain = urlparse(item.product_url).netloc
            method_name = PriceTracker.SUPPORTED_DOMAINS.get(domain)

            if not method_name:
                return False

            method = getattr(PriceTracker, method_name)
            current_price = method(item.product_url)

            if current_price:
                history = item.price_history or []
                history.append({
                    'price': float(current_price),
                    'timestamp': timezone.now().isoformat(),
                    'source': domain
                })

                item.price_history = history
                item.save(update_fields=['price_history'])
                return True

        except Exception as e:
            logger.error(f"Error updating price for item {item.id}: {str(e)}")
            return False

    @staticmethod
    def extract_digikala_price(url: str) -> Optional[float]:
        """Extract price from Digikala"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            price_elem = soup.find('div', {'class': 'product-price'})
            if price_elem:
                price_text = price_elem.text.strip()
                return float(price_text.replace(',', '').replace('تومان', ''))
            return None

        except Exception:
            return None

    @staticmethod
    def get_price_trends(item: WishListItem) -> Dict:
        """Get price trends for an item"""
        history = item.price_history or []
        if not history:
            return {}

        prices = [entry['price'] for entry in history]
        return {
            'current_price': prices[-1],
            'min_price': min(prices),
            'max_price': max(prices),
            'avg_price': sum(prices) / len(prices),
            'price_changes': len(history) - 1,
            'history': history
        }


class SimilarItemsFinder:
    """Service for finding similar items"""

    @staticmethod
    def find_similar_items(item: WishListItem, limit: int = 5) -> List[WishListItem]:
        """Find similar items based on various criteria"""
        queryset = WishListItem.objects.exclude(id=item.id)

        # Find items in same category
        if item.category:
            queryset = queryset.filter(category=item.category)

        # Find items with similar price range (±20%)
        if item.price:
            price_range = item.price * 0.2
            queryset = queryset.filter(
                price__gte=item.price - price_range,
                price__lte=item.price + price_range
            )

        # Find items with similar tags
        if item.tags.exists():
            queryset = queryset.filter(tags__in=item.tags.all())

        # Order by relevance (number of matching criteria)
        queryset = queryset.annotate(
            relevance=Count('tags', filter=Q(tags__in=item.tags.all()))
        ).order_by('-relevance')

        return queryset[:limit]
