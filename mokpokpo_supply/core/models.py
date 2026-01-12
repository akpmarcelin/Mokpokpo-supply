# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


# --------------------
# ROLE
# --------------------
class Role(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nom


# --------------------
# UTILISATEUR
# --------------------
class Utilisateur(AbstractUser):
    prenoms = models.CharField(max_length=150)
    email = models.EmailField(null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    adresse = models.CharField(max_length=255, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    actif = models.BooleanField(default=True)


# --------------------
# PRODUIT
# --------------------
class Produit(models.Model):
    TYPE_CHOICES = [
        ('CAFE', 'Café'),
        ('CACAO', 'Cacao'),
    ]

    nom = models.CharField(max_length=100)
    type_produit = models.CharField(max_length=10, choices=TYPE_CHOICES)
    unite = models.CharField(max_length=20)  # kg, sac
    prix_reference = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nom


# --------------------
# HISTORIQUE DES PRIX (pour IA)
# --------------------
class HistoriquePrix(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()


# --------------------
# ENTREPOT
# --------------------
class Entrepot(models.Model):
    nom = models.CharField(max_length=100)
    localisation = models.CharField(max_length=150)

    def __str__(self):
        return self.nom


# --------------------
# EMPLACEMENT
# --------------------
class Emplacement(models.Model):
    entrepot = models.ForeignKey(Entrepot, on_delete=models.CASCADE)
    code_emplacement = models.CharField(max_length=50)  # ex: E1-R2-N3

    def __str__(self):
        return self.code_emplacement


# --------------------
# LOT
# --------------------
class Lot(models.Model):
    code_lot = models.CharField(max_length=100, unique=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite_initiale = models.FloatField()
    quantite_restante = models.FloatField()
    date_production = models.DateField()
    emplacement = models.ForeignKey(Emplacement, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.code_lot


# --------------------
# MOUVEMENT DE STOCK (traçabilité)
# --------------------
class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('ENTREE', 'Entrée'),
        ('SORTIE', 'Sortie'),
        ('TRANSFERT', 'Transfert'),
    ]

    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantite = models.FloatField()
    source_emplacement = models.ForeignKey(
        Emplacement, on_delete=models.SET_NULL, null=True, related_name='source'
    )
    destination_emplacement = models.ForeignKey(
        Emplacement, on_delete=models.SET_NULL, null=True, related_name='destination'
    )
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)


# --------------------
# LIVRAISON
# --------------------
class Livraison(models.Model):
    STATUT_CHOICES = [
        ('PREPARATION', 'En préparation'),
        ('EN_ROUTE', 'En route'),
        ('LIVREE', 'Livrée'),
    ]

    numero = models.CharField(max_length=50)
    grossiste = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='livraisons_grossiste')
    livreur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='livraisons_livreur')
    statut = models.CharField(max_length=20, default='PREPARATION')
    date_livraison = models.DateField()   # date demandée
    date_creation = models.DateTimeField(auto_now_add=True)  # timestamp


# --------------------
# DETAIL LIVRAISON
# --------------------
class LigneLivraison(models.Model):
    livraison = models.ForeignKey(Livraison, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    lot = models.ForeignKey(Lot, on_delete=models.SET_NULL, null=True, blank=True)
    quantite = models.FloatField()

# --------------------
# PREVISION DEMANDE (préparer l’IA)
# --------------------
class PrevisionDemande(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    periode = models.CharField(max_length=20)  # ex: 2026-03
    quantite_prevue = models.FloatField()
    date_calcul = models.DateTimeField(auto_now_add=True)

