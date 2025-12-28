from django import forms
from django.contrib.auth.forms import UserCreationForm
from user.models import User, Role


class SignUpForm(UserCreationForm):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        empty_label=None,
        widget=forms.RadioSelect,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'role' and isinstance(field.widget, forms.widgets.TextInput):
                field.widget.attrs['class'] = 'form-control'
