from django.forms import ModelForm
from .models import TaxReturn

class TaxReturnForm(ModelForm):
    class Meta:
        model = TaxReturn
        fields = ['title', 'memo', 'sin', 'year', 'full_name', 'important']
