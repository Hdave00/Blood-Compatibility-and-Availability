from rest_framework import serializers
from .models import Donor, DonationRequest, User, BloodMatchHistory


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # exclude sensitive field
        exclude = ('password',)


# Without city and country in the serializer, these fields won’t be included in the JSON response when we save or fetch
# donor data, leading to partial updates and inconsistencies when reloading.

class DonorSerializer(serializers.ModelSerializer):
    # nested user serializer (to avoid exposing sensitive data)
    user = serializers.SerializerMethodField()

    class Meta:
        model = Donor
        fields = ["id", "blood_type", "availability", "user", "location", "city", "country"]

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email,
        }

    # ensuring location is optionally displayed for privacy
    def get_location(self, obj):
        return obj.location if obj.location else "Location not shared by user"


class DonationRequestSerializer(serializers.ModelSerializer):
    
    donor_contact_info = serializers.SerializerMethodField()
    
    # added this later, check json packets for errors related to usernames in donation requests
    requester_username = serializers.CharField(source='requester.username', read_only=True)
    country = serializers.CharField(read_only=True)

    def get_donor_contact_info(self, obj):
        return [obj.donor_contact_info(donor) for donor in obj.accepted_donors.all()]

    class Meta:
        model = DonationRequest
        fields = [
            'recipient', 'requester_username',
            'blood_type_needed', 'location', 'status', 'country',
            'created_at', 'donor_contact_info', 'id'
        ]


class BloodMatchHistorySerializer(serializers.ModelSerializer):

    donor = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)

    class Meta:
        model = BloodMatchHistory
        fields = '__all__'
