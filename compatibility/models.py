from django.contrib.auth.models import AbstractUser
from django.db import models


# importing the is_compatible function which returns true if the donor blood is compatible with recipient blood.
from compatibility.utils import is_compatible


# Global lists for better reuse, too much to keep track of when there are individual blood type
BLOOD_TYPES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
]


COMPATIBILITY_CHART = {
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "AB-": ["A-", "B-", "AB-", "O-"],
    "O+": ["O+", "O-"],
    "O-": ["O-"],
}


# extending AbstractUser to include extra fields (and fixing reverse access error as sugegsted by ddb)
class User(AbstractUser):

    location = models.CharField(max_length=255, blank=True, null=True)

    groups = models.ManyToManyField("auth.Group", related_name="compatibility_users", blank=True)
    user_permissions = models.ManyToManyField("auth.Permission", related_name="compatibility_users_permissions", blank=True)

    def __str__(self):
        return f"{self.username}"


# donor model for having a registered donor and being able to represent the donor on the MAP using API
class Donor(models.Model):
    """ model representing a registered blood donor """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="donor_profile")
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)

    # proper locaiton feilds (for HERE Maps)
    city = models.CharField(max_length=100, blank=True, null=True)  # handles older test users
    state_or_county = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # is required for geolocation storage and usage in the map
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    # backward bompatibility, but also for information obfuscation as stored location is not the displayed location
    # and latitude/longitudes arent ever displayed (Stores combined address, default "Unknown")
    location = models.CharField(max_length=255, blank=True, null=True, default="Unknown")

    availability = models.BooleanField(default=True)
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donor: {self.user.username} ({self.blood_type}) - {self.city or 'Unknown'}, {self.country or 'Unknown'}"


    # from django docs for auto updating functionality (not entirely but mixed with their "sync/update")
    def update_location(self, state_or_county=None):
        """ Syncs the location field for backward compatibility. Stores location in the format: 'City, State/County, Country' """

        if state_or_county:
            self.state_or_county = state_or_county

        # if the location was manually set (from HERE API), dont override it
        if self.location and self.location != "Unknown":
            return

        # making sure city and country exist before updating location
        if self.city and self.country:
            address_parts = [self.city, self.state_or_county, self.country]
            self.location = ", ".join(filter(None, address_parts))
        else:
            self.location = "Unknown"

    # class objects methods can call themselves and update other functions within the class (remember this from cs50p)
    def save(self, *args, **kwargs):

        # for backward compatibility
        self.update_location()
        super().save(*args, **kwargs)



# donation request model, tracks donation requests and updates the status based on matched, completed, cancelled or pending
# it will also be responsible for tracking the requests made from a donor, to a donor ie, requester and recipient
class DonationRequest(models.Model):

    # status variables
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    ]

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    blood_type_needed = models.CharField(max_length=3, choices=BLOOD_TYPES)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    # location fields for better search filtering and compartmentalising of data for better storage
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    donors = models.ManyToManyField(Donor, related_name="donations", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # changing functionality for hiding emails and location until a request is accepted.
    accepted_donors = models.ManyToManyField(Donor, related_name="accepted_requests", blank=True)
    is_accepted = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        """ Autofill city, state, and country from location if available """

        if self.location:
            parts = self.location.split(", ")
            self.city = parts[0] if len(parts) > 0 else ""
            self.state = parts[1] if len(parts) > 1 else ""
            self.country = parts[2] if len(parts) > 2 else ""
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Request by {self.recipient.username} for {self.blood_type_needed} blood"

    def is_matched(self):
        """ returns True if at least one donor is assigned to this request """
        return self.donors.exists()

    def find_potential_donors(self):
        """ finds donors whose blood type is compatible with the requested blood type """
        return Donor.objects.filter(blood_type__in=COMPATIBILITY_CHART.get(self.blood_type_needed, []))

    def accept_request(self, donor):
        """ allows a donor to accept the request and reveals contact info """
        
        if donor in self.donors.all():
            self.accepted_donors.add(donor)
            self.is_accepted = True
            self.status = 'Matched'
            self.save()

    def donor_contact_info(self, donor):
        """ returns donor contact info if the request is accepted """

        if donor in self.accepted_donors.all():
            return {"email": donor.user.email, "location": donor.location}
        return {"email": "Hidden until accepted", "location": "Hidden until accepted"}



# model for checking compatibility (for non registered visitors) and keeping track of donationn history
class BloodMatchHistory(models.Model):

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name="given_matches")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_matches")
    donation_request = models.ForeignKey(DonationRequest, on_delete=models.SET_NULL, null=True, blank=True)

    donor_blood = models.CharField(max_length=3, choices=BLOOD_TYPES)
    recipient_blood = models.CharField(max_length=3, choices=BLOOD_TYPES)
    is_compatible = models.BooleanField(default=False)
    match_date = models.DateTimeField(auto_now_add=True)

    def check_compatibility(self):
        """ determines if the donors blood is compatible with the recipients blood """
        
        self.is_compatible = is_compatible(self.donor_blood, self.recipient_blood)
        return self.is_compatible




