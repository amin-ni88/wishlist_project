import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .factories import (
    UserFactory, WishListFactory, WishListItemFactory,
    PlanFactory, SubscriptionFactory, ContributionFactory,
    NotificationFactory
)

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return UserFactory()

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def wishlist(user):
    return WishListFactory(owner=user)

@pytest.fixture
def wishlist_item(wishlist):
    return WishListItemFactory(wishlist=wishlist)

@pytest.fixture
def plan():
    return PlanFactory()

@pytest.fixture
def subscription(user, plan):
    return SubscriptionFactory(user=user, plan=plan)

@pytest.fixture
def contribution(wishlist_item, user):
    return ContributionFactory(item=wishlist_item, contributor=user)

@pytest.fixture
def notification(user):
    return NotificationFactory(user=user)

@pytest.fixture
def admin_user():
    return UserFactory(is_staff=True, is_superuser=True)
