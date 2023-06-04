from django import forms
from .models import Article, Author, Tag, Category


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = "title", "content", "pub_date", "author", "category", "tags"


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = "name", "bio"


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = "name",


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "name",

