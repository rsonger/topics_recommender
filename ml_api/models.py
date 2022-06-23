from django.db import models
from django.utils import timezone

from topics_recommender.models import UserSession

class ABTest(models.Model):
    """
    An information record about an A/B test.

    Attributes:
        title: The title of this test.
        created_by: The name of the person who created this test.
        created_at: The date and time of the test's creation.
        ended_at: The date and time of the test's completion.
        summary: A description of the test.
        algorithm_A: The first algorithm referencing a MLAlgorithm object.
        algorithm_B: The second algorithm referencing a MLAlgorithm object.
    """
    title = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    summary = models.TextField(blank=True)
    
    def __str__(self):
        title = self.title if len(self.title) < 50 else f"{self.title[:50]}..."
        starttime = timezone.localtime(self.created_at)
        start = f"Started {starttime.isoformat('@', 'minutes')}"
        if self.ended_at:
            endtime = timezone.localtime(self.ended_at)
            end = f"Ended {endtime.isoformat('@', 'minutes')}"
        else:
            end = " <<ACTIVE>>" 
        return f"{title} -- {start} -- {end}"

    class Meta:
        verbose_name = "A/B Test"

class Endpoint(models.Model):
    '''
    Represents a route in the API.

    Attributes:
        name: the name of the endpoint as it will show in the URL
        owner: the name of the owner
        created_at: the date when this endpoint was created
    '''
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    ab_test = models.ForeignKey(
        ABTest, 
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Active A/B Test"
    )

    def __str__(self):
        return self.name

class MLAlgorithm(models.Model):
    '''
    Represents an algorithm provided by the API for use in inference.

    Attributes:
        name: the name of this algorithm
        description: a short description of how this algorithm works
        code: the algorithm source code
        version: the version number of this algorithm
        owner: the name of the owner
        created_at: the date when this algorithm was added to the database
        parent_endpoint: a reference to the endpoint where this algorithm is provided
    '''
    name = models.CharField(max_length=128)
    description = models.TextField()
    code = models.TextField()
    version = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    parent_endpoint = models.ForeignKey(
        Endpoint, 
        on_delete=models.CASCADE,
        related_name="algorithms",
        verbose_name="Assigned Endpoint")
    active = models.BooleanField(default=False)

    def __str__(self):
        str = f"{self.name} (v{self.version})"
        if self.active:
            return f"{str} <<ACTIVE>>"
        return str + self.description

    class Meta:
        verbose_name = "ML Algorithm"

class MLTestingStatus(models.Model):
    '''
    Represents the status of an endpoint which acts as a flag for whether it is in A/B testing.

    Attributes:
        status: the status of the parent endpoint
        active: a boolean flag indicating if the current status is active
        created_at: the date this status was created
        parent_endpoint: a reference to the associated Endpoint

    '''
    status = models.CharField(max_length=16)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_endpoint = models.ForeignKey(
        Endpoint, 
        on_delete=models.CASCADE, 
        related_name = "status", 
        verbose_name="Associated Endpoint"
    )

    def __str__(self):
        endpoint_name = self.parent_endpoint.name
        started = f"Started {timezone.localdate(self.created_at)}"
        active = "<<ACTIVE>>" if self.active else ""
        return f"{endpoint_name}.{self.status} {started} {active}"

    class Meta:
        verbose_name = "Endpoint Status"
        verbose_name_plural = "Endpoint Statuses"

    def save(self, *args, **kwargs) -> None:
        """Ensure the parent endpoint has only one active status."""
        if self.active:
            old_status = MLTestingStatus.objects.filter(
                parent_endpoint=self.parent_endpoint,
                active=True
            )
            if len(old_status) > 0:
                if len(old_status) > 1:
                    raise Exception(f"CONFIGURATION ERROR: Multiple active statuses for endpoint {self.parent_endpoint}")
                old_status[0].active = False
                old_status[0].save()
        return super().save(*args, **kwargs)
        
class MLRequest(models.Model):
    '''
    An object that holds information about a request to an associated MLAlgorithm.

    Attributes:
        input_data: input data sent to the algorithm in JSON format
        response: shorthand of the response status, e.g. "OK" or "ERROR
        full_response: the response returned to the request from the algorithmin JSON format
        ranking: recommended topic IDs and their scores listed in ranking order
        feedback: feedback for comparing actual result to prediction
        created_at: the date when this request was created
        parent_mlalgorithm: a reference to a MLAlgorithm objct used to create the ranking
    '''
    input_data = models.TextField()
    response = models.CharField(max_length=32)
    full_response = models.TextField()
    ranking = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    parent_mlalgorithm = models.ForeignKey(
        MLAlgorithm, 
        on_delete=models.CASCADE,
        related_name="request",
        verbose_name="ranking algorithm"
    )
    user_session = models.ForeignKey(
        UserSession, 
        on_delete=models.CASCADE,
        related_name="request",
        verbose_name="user session"
    )
    previous_request = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True
    )

    def __str__(self):
        endpoint = self.parent_mlalgorithm.parent_endpoint
        algorithm = self.parent_mlalgorithm.name
        time = timezone.localtime(self.created_at)
        
        return f"{endpoint} / {algorithm} ({time})"

    class Meta:
        verbose_name = "ML Request"
        get_latest_by = "created_at"
