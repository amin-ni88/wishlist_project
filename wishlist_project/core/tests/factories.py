import factory
from django.contrib.auth.models import User
from core.models import WishList, WishListItem, Plan, Subscription, Contribution, Notification
from faker import Faker

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

class WishListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WishList

    owner = factory.SubFactory(UserFactory)
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=3))
    description = factory.LazyFunction(lambda: fake.paragraph())
    is_public = factory.Faker('boolean')
    created_at = factory.LazyFunction(lambda: fake.date_time_this_year())

class WishListItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WishListItem

    wishlist = factory.SubFactory(WishListFactory)
    name = factory.LazyFunction(lambda: fake.product_name())
    description = factory.LazyFunction(lambda: fake.paragraph())
    price = factory.LazyFunction(lambda: fake.pydecimal(left_digits=3, right_digits=2))
    priority = factory.Iterator(['LOW', 'MEDIUM', 'HIGH'])
    url = factory.LazyFunction(lambda: fake.url())

class PlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Plan

    name = factory.Iterator(['Basic', 'Premium', 'Pro'])
    price = factory.Iterator([0.00, 9.99, 19.99])
    features = factory.LazyFunction(
        lambda: [fake.word() for _ in range(3)]
    )

class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription

    user = factory.SubFactory(UserFactory)
    plan = factory.SubFactory(PlanFactory)
    start_date = factory.LazyFunction(lambda: fake.date_this_year())
    end_date = factory.LazyFunction(lambda: fake.date_this_year(after_today=True))
    is_active = True

class ContributionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contribution

    item = factory.SubFactory(WishListItemFactory)
    contributor = factory.SubFactory(UserFactory)
    amount = factory.LazyFunction(lambda: fake.pydecimal(left_digits=2, right_digits=2))
    created_at = factory.LazyFunction(lambda: fake.date_time_this_year())

class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)
    message = factory.LazyFunction(lambda: fake.sentence())
    notification_type = factory.Iterator(['CONTRIBUTION', 'WISHLIST_SHARED', 'ITEM_PRICE_DROP'])
    is_read = factory.Faker('boolean')
    created_at = factory.LazyFunction(lambda: fake.date_time_this_year())
