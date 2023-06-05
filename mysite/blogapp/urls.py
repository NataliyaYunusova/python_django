from django.urls import path

from .views import (
    ArticlesListView,
    ArticleCreateView,
    AuthorCreateView,
    AuthorsListView,
    CategoryCreateView,
    CategoriesListView,
    TagCreateView,
    TagsListView,
)

app_name = "blogapp"


urlpatterns = [
    path("articles/", ArticlesListView.as_view(), name="article-list"),
    path("articles/create/", ArticleCreateView.as_view(), name="create_article"),
    path("authors/create/", AuthorCreateView.as_view(), name="create_author"),
    path("authors/", AuthorsListView.as_view(), name="authors-list"),
    path("categories/", CategoriesListView.as_view(), name="categories-list"),
    path("categories/create/", CategoryCreateView.as_view(), name="create_category"),
    path("tags/", TagsListView.as_view(), name="tags-list"),
    path("tags/create/", TagCreateView.as_view(), name="create_tag"),
]
