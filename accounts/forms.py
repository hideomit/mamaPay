from django.contrib.auth.forms import UserCreationForm
from .models import Parent

class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Parent
        fields = ('username', 'email')