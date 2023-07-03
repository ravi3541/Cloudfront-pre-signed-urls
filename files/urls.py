from django.urls import path
from .views import (
                    GetCloudfrontPresignedPutUrlAPIView,
                    SaveDocumentAPIView,
                    GetPresignedGetUrl,
                    DeleteDocumentAPIView
                   )

urlpatterns = [

    path('getPresignedPutUrl', GetCloudfrontPresignedPutUrlAPIView.as_view(), name='put-cloudfront-presigned-url'),
    path("getDocumentUrl/<int:pk>/", GetPresignedGetUrl.as_view(), name="get-doc-url"),
    path("saveDocument", SaveDocumentAPIView.as_view(), name="save-doc"),
    path("deleteDocument/<int:pk>/", DeleteDocumentAPIView.as_view(), name="delete-document")

]
