from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Listing, ListingRevision, Review


User = get_user_model()


class ListingTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username="seller",
            password="SellerPass2026!",
        )

        self.buyer = User.objects.create_user(
            username="buyer",
            password="BuyerPass2026!",
        )

        self.listing = Listing.objects.create(
            title="Носки",
            description="Красивые носки с уточками",
            price=Decimal("20.00"),
            location="Тула",
            category="accessories",
            owner=self.seller,
            status="approved",
        )

    def test_only_approved_listings_are_public(self):
        Listing.objects.create(
            title="Неодобренное объявление",
            description="Его не должно быть на главной",
            price=Decimal("100.00"),
            location="Москва",
            category="other",
            owner=self.seller,
            status="pending",
        )

        response = self.client.get(reverse("home"))

        self.assertContains(response, "Носки")
        self.assertNotContains(response, "Неодобренное объявление")

    def test_seller_creates_pending_listing(self):
        self.client.login(
            username="seller",
            password="SellerPass2026!",
        )

        response = self.client.post(
            reverse("create_listing"),
            {
                "title": "Куртка",
                "description": "Тестовая куртка",
                "price": "1500.00",
                "location": "Москва",
                "category": "outerwear",
            },
        )

        self.assertEqual(response.status_code, 302)

        listing = Listing.objects.get(title="Куртка")

        self.assertEqual(listing.owner, self.seller)
        self.assertEqual(listing.status, "pending")

    def test_contacts_hidden_from_anonymous_user(self):
        self.seller.profile.phone = "+79991234567"
        self.seller.profile.save()

        response = self.client.get(
            reverse("listing_detail", args=[self.listing.pk])
        )

        self.assertNotContains(response, "+79991234567")
        self.assertContains(
            response,
            "Контактная информация доступна только зарегистрированным пользователям",
        )

    def test_contacts_visible_to_authenticated_user(self):
        self.seller.profile.phone = "+79991234567"
        self.seller.profile.telegram = "seller_test"
        self.seller.profile.save()

        self.client.login(
            username="buyer",
            password="BuyerPass2026!",
        )

        response = self.client.get(
            reverse("listing_detail", args=[self.listing.pk])
        )

        self.assertContains(response, "+79991234567")
        self.assertContains(response, "seller_test")

    def test_staff_cannot_create_listing(self):
        moderator = User.objects.create_user(
            username="moderator",
            password="ModeratorPass2026!",
            is_staff=True,
        )

        self.client.login(
            username="moderator",
            password="ModeratorPass2026!",
        )

        response = self.client.get(reverse("create_listing"))

        self.assertEqual(response.status_code, 403)

    def test_user_cannot_edit_another_users_listing(self):
        self.client.login(
            username="buyer",
            password="BuyerPass2026!",
        )

        response = self.client.get(
            reverse("edit_listing", args=[self.listing.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_editing_approved_listing_creates_revision(self):
        self.client.login(
            username="seller",
            password="SellerPass2026!",
        )

        response = self.client.post(
            reverse("edit_listing", args=[self.listing.pk]),
            {
                "title": "Носки",
                "description": "Красивые носки с уточками",
                "price": "25.00",
                "location": "Тула",
                "category": "accessories",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.listing.refresh_from_db()

        self.assertEqual(
            self.listing.price,
            Decimal("20.00"),
        )

        revision = ListingRevision.objects.get(
            listing=self.listing,
            status="pending",
        )

        self.assertEqual(
            revision.price,
            Decimal("25.00"),
        )

    def test_review_is_created_and_updated(self):
        self.client.login(
            username="buyer",
            password="BuyerPass2026!",
        )

        url = reverse(
            "add_review",
            args=[self.listing.pk],
        )

        self.client.post(
            url,
            {
                "rating": "5",
                "text": "Отличные носки",
            },
        )

        self.assertEqual(
            Review.objects.filter(
                listing=self.listing,
                author=self.buyer,
            ).count(),
            1,
        )

        self.client.post(
            url,
            {
                "rating": "4",
                "text": "Хорошие носки",
            },
        )

        review = Review.objects.get(
            listing=self.listing,
            author=self.buyer,
        )

        self.assertEqual(
            Review.objects.filter(
                listing=self.listing,
                author=self.buyer,
            ).count(),
            1,
        )
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.text, "Хорошие носки")

    def test_owner_cannot_review_own_listing(self):
        self.client.login(
            username="seller",
            password="SellerPass2026!",
        )

        response = self.client.post(
            reverse("add_review", args=[self.listing.pk]),
            {
                "rating": "5",
                "text": "Сам себе отзыв",
            },
        )

        self.assertEqual(response.status_code, 403)

        self.assertFalse(
            Review.objects.filter(
                listing=self.listing,
                author=self.seller,
            ).exists()
        )
