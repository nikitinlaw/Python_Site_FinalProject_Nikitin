from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Profile


User = get_user_model()


class AccountTests(TestCase):
    def test_registration_creates_user_and_profile(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": "StrongPass2026!",
                "password2": "StrongPass2026!",
            },
        )

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username="newuser")

        self.assertEqual(user.email, "new@example.com")
        self.assertTrue(
            Profile.objects.filter(user=user).exists()
        )
