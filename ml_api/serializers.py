# # Serializers allow complex data such as querysets and model instances 
# # to be converted to native Python datatypes that can then be easily 
# # rendered into JSON, XML or other content types. Serializers also 
# # provide deserialization, allowing parsed data to be converted back 
# # into complex types, after first validating the incoming data.
# #
# # https://www.django-rest-framework.org/api-guide/serializers/

# from rest_framework import serializers

# from ml_api.models import ABTest

# class ABTestSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = ABTest
#         read_only_fields = ("id", "ended_at", "created_at", "summary")
#         fields = ("id", "title", "created_at", "ended_at", "created_at", 
#                   "summary", "algorithm_A", "algorithm_B")