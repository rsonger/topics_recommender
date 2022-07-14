from django.forms import ModelForm

from survey_tasks.models import DATResponse

class GroupingForm(ModelForm):
    """Input form for the convergent thinking task."""
    class Meta:
        pass