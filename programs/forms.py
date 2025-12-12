from django import forms
from .models import Program

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = [
            "name",
            "description",
            "price",
            "registration_deadline",
            "location",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input"}),
            "description": forms.Textarea(attrs={"class": "textarea", "rows": 4}),
            "price": forms.NumberInput(attrs={"class": "input", "step": "0.01"}),
            "registration_deadline": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "location": forms.TextInput(attrs={"class": "input"}),
        }
