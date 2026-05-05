from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
)

from .permissions import (
    IsAdminOrSuperuser,
    IsAdminOrReadOnly,
    IsAuthorOrModeratorOrAdmin,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    UserSerializer,
    UserMeSerializer,
)
from reviews.models import Category, Comment, Genre, Review, Title


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):

    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')

    permission_classes = (
        permissions.IsAuthenticated,
        IsAdminOrSuperuser,
    )

    queryset = User.objects.all()
    serializer_class = UserSerializer

    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        methods=('get',),
        url_path='me',
        permission_classes=(
            permissions.IsAuthenticated,
        )
    )
    def me(self, request):
        user = self._get_user()
        serializer = UserSerializer(user)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @me.mapping.post
    @me.mapping.patch
    def me_patch(self, request):
        user = self._get_user()
        serializer = UserMeSerializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def _get_user(self):
        return self.request.user


class CategoryViewSet(
    viewsets.GenericViewSet,
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(
    viewsets.GenericViewSet,
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):

    http_method_names = ('get', 'post', 'patch', 'delete',)

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'description')
    ordering_fields = ('year', 'name')

    def get_queryset(self):
        queryset = Title.objects.select_related('category').prefetch_related(
            'genre'
        ).annotate(rating=Avg('reviews__score'))
        year = self.request.query_params.get('year')
        category_slug = self.request.query_params.get('category')
        genre_slug = self.request.query_params.get('genre')
        name = self.request.query_params.get('name')
        if year:
            queryset = queryset.filter(year=year)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        if name:
            queryset = queryset.filter(name=name)
        return queryset.order_by('-rating', '-year', 'name')

    def get_serializer_class(self):
        if self.action in {'list', 'retrieve'}:
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):

    http_method_names = ('get', 'post', 'patch', 'delete',)
    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin
    )

    def _get_title(self):
        title_id = self.kwargs.get('title_id')
        if not title_id:
            raise Http404('Параметр title_id не передан')
        return get_object_or_404(Title, id=title_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['title'] = self._get_title()
        return context

    def get_queryset(self):
        title = self._get_title()
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        title = self._get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):

    http_method_names = ('get', 'post', 'patch', 'delete',)

    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin
    )

    def _get_review(self):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        if not review_id:
            raise Http404('Параметр review_id не передан в URL')
        if not title_id:
            raise Http404('Параметр title_id не передан в URL')
        return get_object_or_404(
            Review,
            id=review_id,
            title_id=title_id
        )

    def get_queryset(self):
        review = self._get_review()
        return Comment.objects.filter(review=review)

    def perform_create(self, serializer):
        review = self._get_review()
        serializer.save(author=self.request.user, review=review)
