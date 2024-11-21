from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from projects import (
    models as projects_models,
    constants as projects_constants
)
from users import models as users_models


class ProjectMemberApiViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = users_models.CustomUser.objects.create(first_name="user1" ,last_name ="gfgh", email="user1@example.com")
        self.user2 = users_models.CustomUser.objects.create(first_name="user2" ,last_name ="gfgh", email="user2@example.com")
        self.user3 = users_models.CustomUser.objects.create(first_name="user3" ,last_name ="gfgh", email="user3@example.com")

        self.project1 = projects_models.Project.objects.create(name="Project 1", max_members=2)
        self.project2 = projects_models.Project.objects.create(name="Project 2", max_members=2)
        self.project3 = projects_models.Project.objects.create(name="Project 3", max_members=2)

        projects_models.ProjectMember.objects.create(project=self.project1, member=self.user1)

        self.add_url = reverse('add_project_members', args=[self.project1.id])
        self.remove_url = reverse('remove_project_members', args=[self.project1.id])

        admin_user = users_models.CustomUser.objects.create_superuser(
            first_name="admin", last_name="test", email="admin@example.com", password="adminpass"
        )
        self.client.force_authenticate(user=admin_user)

    def test_add_member_success(self):
        """Test adding a new member to a project successfully."""
        response = self.client.post(self.add_url, data={'user_ids': [self.user2.id]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(str(self.user2.id), response.data['logs'])
        self.assertEqual(response.data['logs'][str(self.user2.id)], projects_constants.MEMBER_ADDED)

    def test_add_member_already_in_project(self):
        """Test adding a user who is already a member of the project."""
        response = self.client.post(self.add_url, data={'user_ids': [self.user1.id]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(str(self.user1.id), response.data['logs'])
        self.assertEqual(response.data['logs'][str(self.user1.id)], projects_constants.ALREADY_MEMBER)

    def test_add_member_exceeds_project_limit(self):
        """Test adding members beyond the project member limit."""
        self.client.post(self.add_url, data={'user_ids': [self.user2.id]}) 
        response = self.client.post(self.add_url, data={'user_ids': [self.user3.id]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(str(self.user3.id), response.data['logs'])
        self.assertEqual(response.data['logs'][str(self.user3.id)], projects_constants.MEMBER_LIMIT_REACHED)

    def test_remove_member_success(self):
        """Test removing an existing member from the project."""
        response = self.client.post(self.remove_url, data={'user_ids': [self.user1.id]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(str(self.user1.id), response.data['logs'])
        self.assertEqual(response.data['logs'][str(self.user1.id)], projects_constants.MEMBER_REMOVED)

    def test_remove_non_member(self):
        """Test attempting to remove a user who is not a member of the project."""
        response = self.client.post(self.remove_url, data={'user_ids': [self.user2.id]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(str(self.user2.id), response.data['logs'])
        self.assertEqual(response.data['logs'][str(self.user2.id)], projects_constants.NOT_A_MEMBER)

    def test_add_member_user_in_two_projects(self):
        """Test adding a user who is already a member of two projects."""
        projects_models.ProjectMember.objects.create(project=self.project3, member=self.user3)
        projects_models.ProjectMember.objects.create(project=self.project2, member=self.user3)

        response = self.client.post(self.add_url, data={'user_ids': [self.user3.id]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(str(self.user3.id), response.data['logs'])
        self.assertEqual(response.data['logs'][str(self.user3.id)], projects_constants.ALREADY_IN_TWO_PROJECTS)

    def test_invalid_user_id(self):
        """Test providing an invalid user ID."""
        response = self.client.post(self.add_url, data={'user_ids': [999]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("999", response.data['logs'])
        self.assertEqual(response.data['logs']["999"], projects_constants.USER_DOES_NOT_EXIST)

    def test_non_integer_user_ids(self):
        """Test providing non-integer user IDs."""
        response = self.client.post(self.add_url, data={'user_ids': ['abc']})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], projects_constants.USER_IDS_ERROR)

    def test_empty_user_ids(self):
        """Test providing empty user IDs."""
        response = self.client.post(self.add_url, data={'user_ids': []})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], projects_constants.USER_IDS_EMPTY)

