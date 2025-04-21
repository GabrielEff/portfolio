
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from dockNmine.models import WorkGroup

User = get_user_model()

class IntegrationAcceptanceTests(TestCase):
    def setUp(self):
        # Création d’un utilisateur pour simuler un usage réel
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.client.login(username='testuser', password='pass123')

    def test_user_can_create_workgroup(self):
        response = self.client.post(reverse('creategroup'), {
            'name': 'TestGroup',
            'password': 'secretpass',
            'description': 'Projet test pour intégration'
        })
        # Test d'intégration : on vérifie que toutes les couches (formulaire, base, redirection) fonctionnent
        self.assertEqual(response.status_code, 302)
        self.assertTrue(WorkGroup.objects.filter(name='TestGroup').exists())

    def test_user_can_login_and_access_group(self):
        # Acceptation : l’utilisateur doit pouvoir accéder à ses groupes après login
        group = WorkGroup.objects.create(name='AcceptedGroup', password='accept', admin=self.user)
        group.user_set.add(self.user)
        group.save()

        self.client.logout()
        login_success = self.client.login(username='testuser', password='pass123')
        self.assertTrue(login_success)

        response = self.client.get(reverse('onegroup') + f'?id={group.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AcceptedGroup')

    def test_access_protein_statistics_authenticated(self):
        # Intégration : utilisateur connecté doit pouvoir accéder aux statistiques protéines
        session = self.client.session
        group = WorkGroup.objects.create(name='ProteinGroup', password='group', admin=self.user)
        group.user_set.add(self.user)
        group.save()
        session['log_group'] = group.id
        session.save()

        response = self.client.get(reverse('protstats'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'protein_stats.html')
