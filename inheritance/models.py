from django.db import models



# This application will be built along with the login functionality from compatibility application
# it wll only handle the display of the blood group inheritance visualization using the older blood inheritance algorithm
# and it will have some educational resources about blood groups and types and how they work.


# model not needed for visualization but maybe needed for application scaling in future
BLOOD_TYPES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
]

class BloodInheritance(models.Model):
    parent1_blood = models.CharField(max_length=3, choices=BLOOD_TYPES)
    parent2_blood = models.CharField(max_length=3, choices=BLOOD_TYPES)
    # stores possible blood types in json format
    predicted_blood = models.JSONField()

    def serialize(self):
        return {
            "id": self.id,
            "parent1_blood": self.parent1_blood,
            "parent2_blood": self.parent2_blood,
            "predicted_blood": self.predicted_blood,
        }
