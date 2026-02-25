from django.test import TestCase
from django.contrib.auth import get_user_model


User = get_user_model()

class HomeRoutingTests(TestCase):
    def test_home_requires_authentication(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/api-auth/login/", response["Location"])

    def test_home_redirects_authenticated_users_to_projects(self):
        user = User.objects.create_user(username="home-user", password="12345")
        self.client.force_login(user)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/ui/projects/")
