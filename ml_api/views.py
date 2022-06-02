# import datetime

# from django.db import transaction
# from django.db.models import F
# from rest_framework.response import Response
# from rest_framework.viewsets import GenericViewSet
# from rest_framework.views import APIView
# from rest_framework.mixins import (
#     RetrieveModelMixin, 
#     ListModelMixin, 
#     CreateModelMixin, 
#     UpdateModelMixin
# )

# from ml_api.models import MLAlgorithmStatus, MLRequest, ABTest
# from ml_api.serializers import ABTestSerializer


# def deactivate_other_statuses(instance):
#     old_statuses = MLAlgorithmStatus.objects.filter(
#         parent_mlalgorithm=instance.parent_mlalgorithm,
#         created_at__lt=instance.created_at,
#         active=True
#     )
#     for status in old_statuses:
#         status.active = False
#     MLAlgorithmStatus.objects.bulk_update(old_statuses, ["active"])


# class ABTestViewSet(
#     RetrieveModelMixin, 
#     ListModelMixin, 
#     GenericViewSet, 
#     CreateModelMixin, 
#     UpdateModelMixin
# ):
#     """
#     A view for creating new A/B Tests.
#     This view assigns "ab_testing" status to the two algorithms under test.
#     """
#     serializer_class = ABTestSerializer
#     queryset = ABTest.objects.all()

#     def perform_create(self, serializer):
#         # try:
#         with transaction.atomic():
#             instance = serializer.save()

#             # update the status for the first algorithm
#             status_A, _ = MLAlgorithmStatus.objects.get_or_create(
#                 status="ab_testing",
#                 created_by=instance.created_by,
#                 parent_mlalgorithm=instance.algorithm_A,
#                 active=True
#             )
#             # status_A.save()
#             deactivate_other_statuses(status_A)

#             # update the status for the second algorithm
#             status_B, _ = MLAlgorithmStatus.objects.get_or_create(
#                 status="ab_testing",
#                 created_by=instance.created_by,
#                 parent_mlalgorithm=instance.algorithm_B,
#                 active=True
#             )
#             # status_B.save()
#             deactivate_other_statuses(status_B)
            
#         # except Exception as e:
#         #   raise APIException(str(e))

# class ABTestStopView(APIView):
#     """
#     A view for stopping a running A/B Test.
#     This view computes the accuracy of each assocated algorithm.
#     The algorithm with higher accuracy is set to "production" status 
#     while the other is set to "testing".
#     """
#     def post(self, request, ab_test_id, format=None):
#         # try:
#         ab_test = ABTest.objects.get(pk=ab_test_id)

#         if ab_test.ended_at is not None:
#             return Response({
#                 "message": "The specified A/B Test is already finished."
#             })

#         date_now = datetime.datetime.now()
        
#         # calculate algorithm A accuracy
#         responses_A = MLRequest.objects.filter(
#             parent_mlalgorithm=ab_test.algorithm_A, 
#             created_at__gt=ab_test.created_at, 
#             created_at__lt=date_now
#         ).count()
#         correct_responses_A = MLRequest.objects.filter(
#             parent_mlalgorithm=ab_test.algorithm_A, 
#             created_at__gt=ab_test.created_at, 
#             created_at__lt=date_now, 
#             prediction=F('feedback')
#         ).count()
#         accuracy_A = correct_responses_A / float(responses_A)
#         print(responses_A, correct_responses_A, accuracy_A)

#         # calculate algorithm B accuracy
#         responses_B = MLRequest.objects.filter(
#             parent_mlalgorithm=ab_test.algorithm_B, 
#             created_at__gt=ab_test.created_at, 
#             created_at__lt=date_now
#         ).count()
#         correct_responses_B = MLRequest.objects.filter(
#             parent_mlalgorithm=ab_test.algorithm_B, 
#             created_at__gt=ab_test.created_at, 
#             created_at__lt=date_now, 
#             prediction=F('feedback')
#         ).count()
#         accuracy_B = correct_responses_B / float(responses_B)
#         print(responses_B, correct_responses_B, accuracy_B)

#         # select algorithm with higher accuracy
#         top_algorithm, other_algorithm = ab_test.algorithm_A, ab_test.algorithm_B
#         if accuracy_A < accuracy_B:
#             top_algorithm, other_algorithm = other_algorithm, top_algorithm

#         # assign the top algorithm to "production" status
#         production_status = MLAlgorithmStatus(
#             status="production",
#             created_by=ab_test.created_by,
#             parent_mlalgorithm=top_algorithm,
#             active=True
#         )
#         production_status.save()
#         deactivate_other_statuses(production_status)

#         # assign the other algorithm to "testing" status
#         testing_status = MLAlgorithmStatus(
#             status="testing",
#             created_by=ab_test.created_by,
#             parent_mlalgorithm=other_algorithm,
#             active=True
#         )
#         testing_status.save()
#         deactivate_other_statuses(testing_status)

#         summary = f"Algorithm A accuracy: {accuracy_A}, Algorithm B accuracy: {accuracy_B}"
#         ab_test.ended_at = date_now
#         ab_test.summary = summary
#         ab_test.save()

#         # except Exception as e:
#         #     return Response({
#         #         "status": "Error",
#         #         "message": str(e),
#         #         status=status.HTTP_400_BAD_REQUEST
#         #     })
#         return Response({
#             "message": "A/B Test completed.",
#             "summary": summary
#         })
