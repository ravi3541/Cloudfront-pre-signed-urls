import os
import uuid
import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
GenericAPIView,
RetrieveAPIView,
CreateAPIView,DestroyAPIView
)


from .models import Documents
from utilities import messages
from utilities.utils import (
    ResponseInfo,
    generate_signed_url
)
from .serializers import (
    DocumentSerializer,
    GetPresignedUrlSerializer,
)


class GetCloudfrontPresignedPutUrlAPIView(GenericAPIView):
    """
    Class to create API to for getting cloudfront presigned url to upload document.
    """
    serializer_class = GetPresignedUrlSerializer

    def __init__(self, *args, **kwargs):
        self.response = ResponseInfo().response_format
        super(GetCloudfrontPresignedPutUrlAPIView).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        POST method to get Cloudfront  Presigned urls.
        """

        doc_serializer = self.get_serializer(data=request.data)
        if doc_serializer.is_valid(raise_exception=True):

            # generating unique file name for every document
            resource_id = uuid.uuid1()
            resource_id = str(resource_id.hex)
            file_name, file_extension = os.path.splitext(str(request.data["file"]))
            file_key = request.data["upload_path"] + resource_id + file_extension

            resource = os.getenv("CLOUDFRONT_URL") + file_key

            data = generate_signed_url(resource, 300)
            data["file_key"] = file_key

            self.response["error"] = None
            self.response["data"] = data
            self.response["status_code"] = status.HTTP_200_OK
            self.response["message"] = [messages.SUCCESS]

        return Response(self.response)


class GetPresignedGetUrl(RetrieveAPIView):
    """
    Class to create API to return signed url to download document.
    """
    def __init__(self, *args, **kwargs):
        self.response = ResponseInfo().response_format
        super(GetPresignedGetUrl).__init__(*args, **kwargs)

    def get_queryset(self):
        """
        Method to return the document queryset.
        """
        file_id = self.kwargs["pk"]
        return Documents.objects.get(id=file_id)

    def get(self, request, *args, **kwargs):
        """
        GET method to get Cloudfront  Presigned urls.
        """
        try:
            file = self.get_queryset()
            resource = os.getenv("CLOUDFRONT_URL")+str(file.file_key)

            data = generate_signed_url(resource, 120)

            self.response["error"] = None
            self.response["data"] = data
            self.response["message"] = [messages.SUCCESS]
            self.response["status_code"] = status.HTTP_200_OK

        except Documents.DoesNotExist:
            self.response["error"] = "Document"
            self.response["data"] = None
            self.response["message"] = [messages.DOES_NOT_EXIST.format("Document")]
            self.response["status_code"] = status.HTTP_400_BAD_REQUEST

        return Response(self.response)


class SaveDocumentAPIView(CreateAPIView):
    """
    Class to save document details.
    """
    serializer_class = DocumentSerializer

    def __init__(self, *args, **kwargs):
        self.response = ResponseInfo().response_format
        super(SaveDocumentAPIView).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Post method to save document data.
        """
        document_serializer = self.get_serializer(data=request.data)

        if document_serializer.is_valid(raise_exception=True):
            document_serializer.save()

            self.response["status_code"] = status.HTTP_201_CREATED
            self.response["data"] = document_serializer.data
            self.response["error"] = None
            self.response["message"] = [messages.SUCCESS]

        return Response(self.response)


class DeleteDocumentAPIView(DestroyAPIView):
    """
    Class to create API to delete document.
    """
    def __init__(self, *args, **kwargs):
        self.response = ResponseInfo().response_format
        super(DeleteDocumentAPIView).__init__(*args, **kwargs)

    def get_queryset(self):
        """
        Queryset method to return document queryset
        """
        doc_id = self.kwargs["pk"]
        return Documents.objects.get(id=doc_id)

    def delete(self, request, *args, **kwargs):
        """
        Delete method to delete document.
        """
        try:
            document = self.get_queryset()
            resource = os.getenv("CLOUDFRONT_URL")+document.file_key
            data = generate_signed_url(resource, 300)

            if requests.delete(data["signed_url"]):
                document.delete()
                self.response["status_code"] = status.HTTP_204_NO_CONTENT
                self.response["data"] = None
                self.response["error"] = None
                self.response["message"] = [messages.DELETED.format("Document")]

        except Documents.DoesNotExist:
            self.response["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response["data"] = None
            self.response["error"] = "Document"
            self.response["message"] = [messages.DOES_NOT_EXIST.format("Document")]

        return Response(self.response)
