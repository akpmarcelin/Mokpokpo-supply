# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur

class UtilisateurCreationForm(UserCreationForm):
    telephone = forms.CharField(max_length=20, required=True, label="Téléphone")
    adresse = forms.CharField(max_length=255, required=True, label="Adresse")

    class Meta:
        model = Utilisateur
        fields = ('username', 'prenoms', 'email', 'telephone', 'adresse', 'password1', 'password2')

    # optionnel : labels propres
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Nom d'utilisateur"
        self.fields['prenoms'].label = "Prénoms"
        self.fields['email'].label = "Email"
        self.fields['password1'].label = "Mot de passe"
        self.fields['password2'].label = "Confirmer le mot de passe"

