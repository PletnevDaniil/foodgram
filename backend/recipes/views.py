# # from django.shortcuts import redirect, get_object_or_404

# # from .models import Recipe
# from django.http import HttpResponse
# from django.conf import settings
# import os


# def redirect_to_recipe_detail(request, pk):
#     """Редирект по короткой ссылке"""
#     # Можно проверить, существует ли рецепт
#     # Recipe.objects.get(pk=pk)

#     # Отдаём index.html — пусть React роутер обработает /recipes/9/
#     index_path = os.path.join(
#         settings.BASE_DIR,
#         '../frontend/build', 'index.html'
#     )
#     try:
#         with open(index_path, 'r', encoding='utf-8') as f:
#             content = f.read()
#         return HttpResponse(content, content_type='text/html')
#     except FileNotFoundError:
#         return HttpResponse('Frontend build not found', status=500)

# # def redirect_to_recipe_detail(request, pk):
# #     recipe = get_object_or_404(Recipe, pk=pk)
# #     return redirect(f'/recipes/{recipe.pk}/')
