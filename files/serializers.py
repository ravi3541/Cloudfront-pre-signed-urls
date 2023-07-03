from rest_framework import serializers
from .models import Documents


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer class for document.
    """

    class Meta:
        model = Documents
        fields = ("id", "file_key", "created_at", "updated_at")


class GetPresignedUrlSerializer(serializers.Serializer):
    """
    Serializer class for verifying required fields for getting presigned urls.
    """
    file = serializers.FileField(required=True, allow_empty_file=False)
    upload_path = serializers.CharField(max_length=100, required=True, allow_null=False, allow_blank=False)
