from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Product
from .serializers import ProductSerializer
from .permissions import IsAuthenticatedReadCreateOnly, IsAdminUserForHighPriceDelete

class ProductViewSet(viewsets.ModelViewSet):
    """
    Ürünler için CRUD işlemlerini sağlayan ViewSet.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedReadCreateOnly, IsAdminUserForHighPriceDelete]

    def get_queryset(self):
        """
        Sorgu parametrelerine göre filtrelenmiş queryset döndürür.
        select_related ve prefetch_related kullanarak performansı artırır.
        """
        queryset = Product.objects.filter(is_active=True)
        
        # N+1 problemini çözmek için relations'ları önceden yükle
        queryset = queryset.select_related('category').prefetch_related('tags')
        
        # Kategori ve etiketlere göre filtreleme
        category_id = self.request.query_params.get('category')
        tag_id = self.request.query_params.get('tag')
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
            
        return queryset

    @swagger_auto_schema(
        operation_description="Tüm ürünleri listeler",
        responses={
            200: ProductSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        """
        Ürünleri listeler ve önbelleğe alır.
        """
        # Cache key belirleme
        cache_key = 'product_list'
        category_id = request.query_params.get('category')
        tag_id = request.query_params.get('tag')
        
        if category_id:
            cache_key = f'product_list_category_{category_id}'
        elif tag_id:
            cache_key = f'product_list_tag_{tag_id}'
        
        # Önbellekten veri almayı dene
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # Önbellekte yoksa, veritabanından al
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Önbelleğe kaydet (30 dakika süreyle)
        cache.set(cache_key, serializer.data, timeout=60*30)
        
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Yeni bir ürün oluşturur",
        request_body=ProductSerializer,
        responses={
            201: ProductSerializer,
            400: "Geçersiz veri"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Yeni bir ürün oluşturur.
        """
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Belirli bir ürünü getirir",
        responses={
            200: ProductSerializer,
            404: "Ürün bulunamadı"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Belirli bir ürünün detaylarını getirir.
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Belirli bir ürünü tamamen günceller",
        request_body=ProductSerializer,
        responses={
            200: ProductSerializer,
            400: "Geçersiz veri",
            404: "Ürün bulunamadı"
        }
    )
    def update(self, request, *args, **kwargs):
        """
        Belirli bir ürünü tamamen günceller (PUT).
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Belirli bir ürünü kısmen günceller",
        request_body=ProductSerializer,
        responses={
            200: ProductSerializer,
            400: "Geçersiz veri",
            404: "Ürün bulunamadı"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Belirli bir ürünü kısmen günceller (PATCH).
        """
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Belirli bir ürünü siler",
        responses={
            204: "İçerik yok",
            404: "Ürün bulunamadı"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """
        Belirli bir ürünü siler.
        """
        return super().destroy(request, *args, **kwargs)