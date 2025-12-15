from django import forms
from .models import Program

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = [
            "title",
            "description",
            "price",
            "start_time",
            "reg_deadline",
            "location",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "input"}
            ),
            "description": forms.Textarea(
                attrs={"class": "textarea", "rows": 4}
            ),
            "price": forms.NumberInput(
                attrs={"class": "input", "step": "0.01"}
            ),
            "start_time": forms.DateTimeInput(
                attrs={"class": "input", "type": "datetime-local"}
            ),
            "reg_deadline": forms.DateTimeInput(
                attrs={"class": "input", "type": "datetime-local"}
            ),
            "location": forms.TextInput(
                attrs={"class": "input"}
            ),
        }
