from django.shortcuts import redirect, get_object_or_404

from .models import Recipe


def redirect_to_recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return redirect(f'/recipes/{recipe.pk}/')
