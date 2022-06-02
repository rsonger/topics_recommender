from django.contrib import admin
from ml_api.models import Endpoint
from ml_api.models import MLAlgorithm
from ml_api.models import MLTestingStatus
from ml_api.models import MLRequest
from ml_api.models import ABTest

admin.site.register(Endpoint)
admin.site.register(MLAlgorithm)
admin.site.register(MLTestingStatus)
admin.site.register(MLRequest)
admin.site.register(ABTest)
