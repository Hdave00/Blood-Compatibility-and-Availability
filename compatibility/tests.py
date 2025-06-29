from django.test import TestCase, Client
from .models import User, Donor, DonationRequest


# unittest class that will define a few function that fit in the class, each of which is something we would like to test

# define a subclass of TestCase, which behaves similar to Unittest
# todo this, we need to setup some initial data to test this, because django creates an entirely separate dbase for us, just for testing purposes

class DonorTestCase(TestCase):

    def setUp(self):


        # ---create data for User object---

        # since User model extends AbstractUser we need to provide at least a username and password.
        # we can also set other fields like location if we want to test specific scenarios.
        user1 = User.objects.create_user(username="testuser", password="testpass")
        user2 = User.objects.create_user(username="testuser2", password="testpass")
        user3 = User.objects.create_user(username="testuser3", password="testpass")
        user4 = User.objects.create_user(username="testuser4", password="testpass")
        user6 = User.objects.create_user(username="testuser6", password="testpass")
        user7 = User.objects.create_user(username="testuser7", password="testpass")

        # ---create data for Donor object---

        # we don’t need to create separate objects for blood types, locations, or availability if they are just attributes of the Donor model.
        # we can set these attributes directly when creating a Donor object.
        # we can set the city, state_or_county, country, and availability attributes when creating a Donor object

        Donor.objects.create(user=user1, blood_type="A+", city="Paris", country="France")
        Donor.objects.create(user=user2, blood_type="A-", city="Mumbai", state_or_county="Maharashtra", country="India")
        Donor.objects.create(user=user3, blood_type="O-", availability=False, city="London", country="United Kingdom")
        Donor.objects.create(user=user4, blood_type="B+", availability=True, city="Tokyo", country="Japan")
        Donor.objects.create(user=user6, blood_type="O+", city="Berlin", country="Germany")
        Donor.objects.create(user=user7, blood_type="B-", city="Sydney", state_or_county="Queensland", country="Australia")


    # then define the tests themselves after creating mock data

    # test valid country, city and state
    def test_valid_country_city_state(self):
        d1 = Donor.objects.get(city="Paris")
        self.assertEqual(d1.country, "France")
        self.assertEqual(d1.city, "Paris")

        d2 = Donor.objects.get(state_or_county="Maharashtra")
        self.assertEqual(d2.state_or_county, "Maharashtra")
        self.assertEqual(d2.country, "India")

    # test invalid country/city/state
    def test_invalid_country_city_state(self):
        d3 = Donor.objects.get(city="London")
        self.assertNotEqual(d3.country, "France")


    # test availability
    def test_availability(self):
        d4 = Donor.objects.get(city="Tokyo")
        self.assertTrue(d4.availability)

        d3 = Donor.objects.get(city="London")
        self.assertFalse(d3.availability)

    # test valid donor
    def test_valid_donor(self):
        d4 = Donor.objects.get(city="Tokyo")
        self.assertIsNotNone(d4.blood_type)
        self.assertIsNotNone(d4.city)
        self.assertIsNotNone(d4.country)

    # test invalid donor (no location, no blood type provided)
    def test_invalid_donor(self):
        user_invalid = User.objects.create_user(username="invaliduser", password="testpass")

        # no city country or blood type
        donor_invalid = Donor.objects.create(user=user_invalid)
        self.assertIsNone(donor_invalid.city)
        self.assertIsNone(donor_invalid.country)
        self.assertIsNone(donor_invalid.blood_type or None)

    # test valid blood type
    def test_valid_blood_type(self):
        d6 = Donor.objects.get(city="Berlin")
        self.assertIn(d6.blood_type, ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

    # test invalid blood types
    def test_invalid_blood_type(self):
        user_invalid_blood = User.objects.create_user(username="invalidblood", password="testpass")
        donor_invalid = Donor.objects.create(user=user_invalid_blood, blood_type="X")
        self.assertNotIn(donor_invalid.blood_type, ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

    # test update location
    def test_update_location(self):
        d7 = Donor.objects.get(city="Sydney")

        # manually reset location to trigger update
        d7.location = "Unknown"
        d7.update_location("New South Wales")
        d7.save()

        print(f"new location is: {d7.location}")
        self.assertEqual(d7.state_or_county, "New South Wales")
        self.assertEqual(d7.location, "Sydney, New South Wales, Australia")

    # test saving location
    def test_save_location(self):
        donor_new = Donor.objects.create(user=User.objects.create_user(username="savelocation", password="testpass"), blood_type="A+", city="Amsterdam", country="Netherlands")
        donor_new.save()
        self.assertEqual(donor_new.location, "Amsterdam, Netherlands")


    # test with similar assert statement for flights as in lecture, but for the donor count and all the other data we are showing on the
    # index page, use the context we pass in to the template, to check count of each, if its dynamic, change logic accordingly
    # testing the actual pages themselves and not just the data, for this we start with testing the default index page, using the Client import
    def test_index(self):
        c = Client()
        total_donors = Donor.objects.count()
        total_countries = Donor.objects.values("country").distinct().count()
        total_cities = Donor.objects.values("city").distinct().count()
        total_states_or_counties = Donor.objects.values("state_or_county").distinct().count()
        total_blood_types = Donor.objects.values("blood_type").distinct().count()

        response = c.get("/")
        self.assertEqual(response.status_code, 200)

        # test context
        self.assertEqual(response.context["total_donors"], total_donors)
        self.assertEqual(response.context["total_countries"], total_countries)
        self.assertEqual(response.context["total_cities"], total_cities)
        self.assertEqual(response.context["total_states_or_counties"], total_states_or_counties)
        self.assertEqual(response.context["total_blood_types"], total_blood_types)

    # test valid donor profile page, like in lecture, pass in the needed context
    def test_valid_donor_profile_page(self):
        d1 = Donor.objects.get(city="Paris")

        c = Client()

        # log in as the donor, for testing the login required while we're at it
        c.force_login(d1.user)

        response = c.get(f"/user/{d1.user.id}/profile/")
        self.assertEqual(response.status_code, 200)

        # test context
        self.assertEqual(response.context["viewed_user"], d1.user)
        self.assertEqual(response.context["donor_profile"], d1)
        self.assertTrue("received_requests" in response.context)
        self.assertTrue("is_own_profile" in response.context)
        self.assertTrue("has_requested" in response.context)
        self.assertTrue("donor_contact_info" in response.context)
        self.assertEqual(response.context["date_registered"], d1.date_registered)

    # test invalid donor profile page (non existent user ID, 999)
    def test_invalid_donor_profile_page(self):

        d6 = Donor.objects.get(city="Berlin")
        c = Client()

        c.force_login(d6.user)
        response = c.get("/user/999/profile/")
        self.assertEqual(response.status_code, 404)

