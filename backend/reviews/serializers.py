"""
Review serializers.
"""

from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id", "user", "user_name", "product", "rating",
            "comment", "is_approved", "created_at",
        ]
        read_only_fields = ["id", "user", "is_approved", "created_at"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
