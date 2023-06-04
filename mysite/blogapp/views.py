from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from .forms import AuthorForm
from .models import Article, Author, Category, Tag


class ArticlesListView(ListView):
    model = Article
    context_object_name = "articles"
    template_name = "blogapp/article_list.html"
    queryset = (
        Article.objects
        .select_related("author")
        .prefetch_related("tags")
        .defer("content")
    )


class ArticleCreateView(CreateView):
    model = Article
    template_name = 'blogapp/create_article.html'
    fields = "title", "content", "pub_date", "author", "category", "tags",
    success_url = reverse_lazy("blogapp:article-list")


class AuthorCreateView(CreateView):
    model = Author
    template_name = 'blogapp/create_author.html'
    fields = "name", "bio"
    success_url = reverse_lazy("blogapp:authors-list")


class AuthorsListView(ListView):
    model = Author
    context_object_name = "authors"
    template_name = "blogapp/authors_list.html"


class CategoryCreateView(CreateView):
    model = Category
    template_name = 'blogapp/create_category.html'
    fields = "name",
    success_url = reverse_lazy("blogapp:categories-list")


class CategoriesListView(ListView):
    model = Category
    context_object_name = "categories"
    template_name = "blogapp/categories_list.html"


class TagCreateView(CreateView):
    model = Tag
    template_name = 'blogapp/create_tag.html'
    fields = "name",
    success_url = reverse_lazy("blogapp:tags-list")


class TagsListView(ListView):
    model = Tag
    context_object_name = "tags"
    template_name = "blogapp/tags_list.html"
