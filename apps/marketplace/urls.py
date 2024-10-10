from django.urls import path
from apps.marketplace.views import (
    ProduitsListView,
    ProduitFilterView,
    ProduitProfileFindView,
    ProduitProfileView,
    ProduitNewView,
)

urlpatterns = [
    path('produits/list/', ProduitsListView.as_view(), name='produits-list'),
    path('produits/filter/', ProduitFilterView.as_view(), name='produit-filter'),
    path('produit/profile/find/<int:id_produit>/', ProduitProfileFindView.as_view(), name='produit-profile-find'),
    path('produits/profile/<int:id_produit>/edit/', ProduitProfileView.as_view(), name='produit-profile-edit'),
    path('produits/new/', ProduitNewView.as_view(), name='produit-new'),
]
