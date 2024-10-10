from django.urls import path
from apps.marketplace.views import (
    ProduitsListView,
    ProduitFilterView,
    ProduitProfileFindView,
    ProduitProfileView,
    ProduitNewView,
    ProduitAchatView,
)

urlpatterns = [
    path('produits/list/', ProduitsListView.as_view(), name='produits-list'), # GET
    path('produits/filter/', ProduitFilterView.as_view(), name='produit-filter'), # GET
    path('produit/profile/find/<int:id_produit>/', ProduitProfileFindView.as_view(), name='produit-profile-find'), # GET
    path('produits/profile/<int:id_produit>/edit/', ProduitProfileView.as_view(), name='produit-profile-edit'), # PUT, DELETE
    path('produits/new/', ProduitNewView.as_view(), name='produit-new'), # POST
    path('produits/achats/new/', ProduitAchatView.as_view(), name='achat_produit'), # POST
]
