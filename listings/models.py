from django.conf import settings
from django.db import models


class Listing(models.Model):
    STATUS_CHOICES = [
        ("pending", "На модерации"),
        ("approved", "Одобрено"),
        ("rejected", "Отклонено"),
    ]

    CATEGORY_CHOICES = [
        ("outerwear", "Верхняя одежда"),
        ("suits", "Костюмы"),
        ("dresses", "Платья"),
        ("shoes", "Обувь"),
        ("accessories", "Аксессуары"),
        ("other", "Другое"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    location = models.CharField(max_length=200)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="other",
    )

    image = models.ImageField(
        upload_to="listings/",
        blank=True,
        null=True,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    @property
    def pending_revision(self):
        return (
            self.revisions
            .filter(status="pending")
            .order_by("-created_at")
            .first()
        )

    def __str__(self):
        return self.title


class ListingRevision(models.Model):
    STATUS_CHOICES = [
        ("pending", "На модерации"),
        ("approved", "Одобрено"),
        ("rejected", "Отклонено"),
    ]

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="revisions",
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    location = models.CharField(max_length=200)

    category = models.CharField(
        max_length=50,
        choices=Listing.CATEGORY_CHOICES,
    )

    image = models.ImageField(
        upload_to="listing_revisions/",
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def apply(self):
        listing = self.listing

        listing.title = self.title
        listing.description = self.description
        listing.price = self.price
        listing.location = self.location
        listing.category = self.category

        if self.image:
            listing.image = self.image

        listing.status = "approved"
        listing.save()

    def __str__(self):
        return f"Изменения для {self.listing.title}"


class Review(models.Model):
    RATING_CHOICES = [
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
    ]

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_written",
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
    )

    text = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("listing", "author"),
                name="one_review_per_user_per_listing",
            )
        ]

    def __str__(self):
        return f"{self.author} → {self.listing}: {self.rating}/5"
