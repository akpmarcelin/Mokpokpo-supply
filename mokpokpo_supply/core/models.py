# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


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
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    localisation = models.CharField(max_length=255)  # UNE SEULE INFO
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    actif = models.BooleanField(default=True)
    date_inscription = models.DateTimeField(auto_now_add=True)


    # Métadonnées
    class Meta:
        verbose_name = 'utilisateur'
        verbose_name_plural = 'utilisateurs'
        ordering = ['nom', 'prenom']

    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur."""
        full_name = f"{self.prenom} {self.nom}".strip()
        return full_name if full_name else self.username

    def get_short_name(self):
        """Retourne le prénom de l'utilisateur."""
        return self.prenom if self.prenom else self.username

    def __str__(self):
        return self.get_full_name()


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
    """
    Modèle pour tracer tous les mouvements de stock dans l'entrepôt.
    Permet de suivre l'historique des entrées, sorties et transferts de lots.
    """
    TYPE_CHOICES = [
        ('ENTREE', 'Entrée en stock'),
        ('SORTIE', 'Sortie de stock'),
        ('TRANSFERT', 'Transfert entre emplacements'),
    ]
    
    lot = models.ForeignKey(
        Lot, 
        on_delete=models.CASCADE,
        verbose_name='lot concerné',
        related_name='mouvements'
    )
    type_mouvement = models.CharField(
        'type de mouvement',
        max_length=20, 
        choices=TYPE_CHOICES,
        help_text='Type d\'opération effectuée sur le stock'
    )
    quantite = models.FloatField(
        'quantité',
        help_text='Quantité déplacée (en kg)'
    )
    source_emplacement = models.ForeignKey(
        Emplacement, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='mouvements_sortants',
        verbose_name='emplacement source',
        help_text='Emplacement de départ du produit (vide pour les entrées)'
    )
    destination_emplacement = models.ForeignKey(
        Emplacement, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='mouvements_entrants',
        verbose_name='emplacement de destination',
        help_text='Emplacement d\'arrivée du produit (vide pour les sorties)'
    )
    utilisateur = models.ForeignKey(
        Utilisateur, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='operations_stock',
        verbose_name='responsable',
        help_text='Utilisateur ayant effectué l\'opération'
    )
    date = models.DateTimeField(
        'date et heure',
        auto_now_add=True,
        help_text='Date et heure du mouvement'
    )
    commentaire = models.TextField(
        'commentaire',
        blank=True,
        null=True,
        help_text='Informations complémentaires sur le mouvement'
    )
    
    class Meta:
        verbose_name = 'mouvement de stock'
        verbose_name_plural = 'mouvements de stock'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date'], name='idx_mouvement_date'),
            models.Index(fields=['type_mouvement'], name='idx_mouvement_type'),
        ]
    
    def __str__(self):
        return (f"{self.get_type_mouvement_display()} - "
                f"{self.quantite} kg de {self.lot} le {self.date.strftime('%d/%m/%Y %H:%M')}")
    
    def save(self, *args, **kwargs):
        # Vérification de la cohérence des emplacements selon le type de mouvement
        if self.type_mouvement == 'ENTREE' and self.source_emplacement:
            raise ValidationError("Une entrée ne peut pas avoir d'emplacement source")
        elif self.type_mouvement == 'SORTIE' and self.destination_emplacement:
            raise ValidationError("Une sortie ne peut pas avoir d'emplacement de destination")
        elif self.type_mouvement == 'TRANSFERT' and not (self.source_emplacement and self.destination_emplacement):
            raise ValidationError("Un transfert nécessite un emplacement source et un emplacement de destination")
            
        super().save(*args, **kwargs)


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

