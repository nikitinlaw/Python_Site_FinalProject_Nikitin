from django import forms

from .models import Listing, ListingRevision, Review


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = (
            "title",
            "description",
            "price",
            "location",
            "category",
            "image",
        )

        labels = {
            "title": "Заголовок",
            "description": "Описание",
            "price": "Стоимость аренды",
            "location": "Местоположение",
            "category": "Категория",
            "image": "Фотография",
        }


class ListingRevisionForm(forms.ModelForm):
    class Meta:
        model = ListingRevision
        fields = (
            "title",
            "description",
            "price",
            "location",
            "category",
            "image",
        )

        labels = {
            "title": "Заголовок",
            "description": "Описание",
            "price": "Стоимость аренды",
            "location": "Местоположение",
            "category": "Категория",
            "image": "Новая фотография",
        }


class ListingSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="Что ищем",
        widget=forms.TextInput(
            attrs={"placeholder": "Например: носки"}
        ),
    )

    location = forms.CharField(
        required=False,
        label="Город",
        widget=forms.TextInput(
            attrs={"placeholder": "Например: Москва"}
        ),
    )

    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        label="Цена от",
    )

    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        label="Цена до",
    )


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = (
            "rating",
            "text",
        )

        labels = {
            "rating": "Оценка",
            "text": "Отзыв",
        }
