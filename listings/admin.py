from django.contrib import admin

from .models import Listing, ListingRevision


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "price",
        "location",
        "category",
        "owner",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "category",
    )

    search_fields = (
        "title",
        "description",
        "location",
        "owner__username",
    )

    ordering = ("-created_at",)


@admin.register(ListingRevision)
class ListingRevisionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "listing",
        "price",
        "status",
        "created_at",
    )

    list_filter = ("status",)

    actions = (
        "approve_revisions",
        "reject_revisions",
    )

    @admin.action(description="Одобрить выбранные изменения")
    def approve_revisions(self, request, queryset):
        for revision in queryset:
            revision.status = "approved"
            revision.save(update_fields=["status"])
            revision.apply()

    @admin.action(description="Отклонить выбранные изменения")
    def reject_revisions(self, request, queryset):
        queryset.update(status="rejected")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.status == "approved":
            obj.apply()
