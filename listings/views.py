from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ListingForm, ListingRevisionForm, ListingSearchForm, ReviewForm
from .models import Listing, Review


def home(request):
    listings = Listing.objects.filter(
        status="approved"
    ).order_by("-created_at")

    search_form = ListingSearchForm(request.GET or None)

    if search_form.is_valid():
        q = search_form.cleaned_data.get("q")
        location = search_form.cleaned_data.get("location")
        min_price = search_form.cleaned_data.get("min_price")
        max_price = search_form.cleaned_data.get("max_price")

        if q:
            listings = listings.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q)
            )

        if location:
            listings = listings.filter(
                location__icontains=location
            )

        if min_price is not None:
            listings = listings.filter(
                price__gte=min_price
            )

        if max_price is not None:
            listings = listings.filter(
                price__lte=max_price
            )

    return render(
        request,
        "listings/home.html",
        {
            "listings": listings,
            "search_form": search_form,
        },
    )


def listing_detail(request, pk):
    listing = get_object_or_404(
        Listing,
        pk=pk,
        status="approved",
    )

    user_review = None

    if request.user.is_authenticated:
        user_review = listing.reviews.filter(
            author=request.user
        ).first()

    return render(
        request,
        "listings/detail.html",
        {
            "listing": listing,
            "user_review": user_review,
        },
    )


def seller_only(user):
    if user.is_staff:
        raise PermissionDenied(
            "Эта функция предназначена для обычных пользователей."
        )


@login_required
def create_listing(request):
    seller_only(request.user)

    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)

        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.status = "pending"
            listing.save()
            return redirect("my_listings")
    else:
        form = ListingForm()

    return render(
        request,
        "listings/create.html",
        {"form": form},
    )


@login_required
def my_listings(request):
    seller_only(request.user)

    listings = Listing.objects.filter(
        owner=request.user
    ).order_by("-created_at")

    return render(
        request,
        "listings/my_listings.html",
        {"listings": listings},
    )


@login_required
def edit_listing(request, pk):
    seller_only(request.user)

    listing = get_object_or_404(
        Listing,
        pk=pk,
        owner=request.user,
    )

    if listing.status == "approved":
        revision = listing.pending_revision

        if request.method == "POST":
            form = ListingRevisionForm(
                request.POST,
                request.FILES,
                instance=revision,
            )

            if form.is_valid():
                revision = form.save(commit=False)
                revision.listing = listing
                revision.status = "pending"
                revision.save()
                return redirect("my_listings")

        else:
            if revision:
                form = ListingRevisionForm(instance=revision)
            else:
                form = ListingRevisionForm(
                    initial={
                        "title": listing.title,
                        "description": listing.description,
                        "price": listing.price,
                        "location": listing.location,
                        "category": listing.category,
                    }
                )

        return render(
            request,
            "listings/edit.html",
            {
                "form": form,
                "listing": listing,
                "revision_mode": True,
            },
        )

    if request.method == "POST":
        form = ListingForm(
            request.POST,
            request.FILES,
            instance=listing,
        )

        if form.is_valid():
            listing = form.save(commit=False)
            listing.status = "pending"
            listing.save()
            return redirect("my_listings")
    else:
        form = ListingForm(instance=listing)

    return render(
        request,
        "listings/edit.html",
        {
            "form": form,
            "listing": listing,
            "revision_mode": False,
        },
    )


@login_required
def delete_listing(request, pk):
    seller_only(request.user)

    listing = get_object_or_404(
        Listing,
        pk=pk,
        owner=request.user,
    )

    if request.method == "POST":
        listing.delete()
        return redirect("my_listings")

    return render(
        request,
        "listings/delete.html",
        {"listing": listing},
    )


@login_required
def add_review(request, pk):
    listing = get_object_or_404(
        Listing,
        pk=pk,
        status="approved",
    )

    if listing.owner == request.user:
        raise PermissionDenied(
            "Нельзя оставлять отзыв на собственное объявление."
        )

    if request.method == "POST":
        review, created = Review.objects.get_or_create(
            listing=listing,
            author=request.user,
            defaults={
                "rating": request.POST.get("rating"),
                "text": request.POST.get("text"),
            },
        )

        if not created:
            form = ReviewForm(
                request.POST,
                instance=review,
            )

            if form.is_valid():
                form.save()
        return redirect(
            "listing_detail",
            pk=listing.pk,
        )

    return redirect(
        "listing_detail",
        pk=listing.pk,
    )
