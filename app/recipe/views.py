from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base view set for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """return objects from current authenticated user only

           when the view is invoked, this method is used to get the objects,
           if this method is not override, whatever is specified in queryset
           field
        """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the DB"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in DB"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage view with`create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions
    for Recipes.
    """
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """retrieved the recipes for the authenticated user"""
        return self.queryset.filter(user=self.request.user)
