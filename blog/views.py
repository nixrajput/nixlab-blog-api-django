from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from blog.models import BlogPost
from blog.serializers import (
    BlogPostSerializer,
    BlogPostUpdateSerializer,
    BlogPostCreateSerializer,
)

SUCCESS = "SUCCESS"
ERROR = "ERROR"
DELETE_SUCCESS = "DELETED"
UPDATE_SUCCESS = "UPDATED"
CREATE_SUCCESS = "CREATED"
PERMISSION_DENIED = "PERMISSION_DENIED"
DOES_NOT_EXIST = "DOES_NOT_EXIST"


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def api_detail_blog_view(request, slug):
    try:
        blog_post = BlogPost.objects.get(slug=slug, is_draft=False)
    except BlogPost.DoesNotExist:
        return Response({"response": DOES_NOT_EXIST},
                        status=status.HTTP_404_NOT_FOUND
                        )

    serializer = BlogPostSerializer(blog_post)

    if request.method == "GET":
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({'response': serializer.errors, },
                    status=status.HTTP_400_BAD_REQUEST, )


@api_view(["PUT"])
@permission_classes((IsAuthenticated,))
def api_update_blog_view(request, slug):
    try:
        blog_post = BlogPost.objects.get(slug=slug, is_draft=False)
    except BlogPost.DoesNotExist:
        return Response({"response": DOES_NOT_EXIST},
                        status=status.HTTP_404_NOT_FOUND
                        )

    user = request.user
    if blog_post.author != user:
        return Response({
            "response": "You don't have permission to edit this post."
        })

    if request.method == "PUT":
        serializer = BlogPostUpdateSerializer(
            blog_post,
            data=request.data,
            partial=True
        )
        data = {}

        if serializer.is_valid():
            serializer.save()
            data['response'] = UPDATE_SUCCESS
            data['id'] = blog_post.id
            data['title'] = blog_post.title
            data['body'] = blog_post.body
            data['slug'] = blog_post.slug
            data['image'] = blog_post.image.url
            data['author'] = blog_post.author.username
            data['author_id'] = blog_post.author.id
            data['timestamp'] = blog_post.timestamp
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def api_delete_blog_view(request, slug):
    try:
        blog_post = BlogPost.objects.get(slug=slug, is_draft=False)
    except BlogPost.DoesNotExist:
        return Response({"response": DOES_NOT_EXIST},
                        status=status.HTTP_404_NOT_FOUND
                        )

    user = request.user
    if blog_post.author != user:
        return Response(
            {'response': PERMISSION_DENIED},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if request.method == 'DELETE':
        operation = blog_post.delete()
        data = {}
        if operation:
            data['response'] = DELETE_SUCCESS
            return Response(data=data, status=status.HTTP_200_OK)
        return Response({"response": "DELETION_FAILED"},
                        status=status.HTTP_400_BAD_REQUEST
                        )


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def api_like_toggle_view(request, slug):
    try:
        blog_post = BlogPost.objects.get(slug=slug, is_draft=False)
    except BlogPost.DoesNotExist:
        return Response({"response": DOES_NOT_EXIST},
                        status=status.HTTP_404_NOT_FOUND
                        )

    if request.user.is_authenticated:
        if request.user in blog_post.likes.all():
            blog_post.likes.remove(request.user)
            liked = False
        else:
            blog_post.likes.add(request.user)
            liked = True

        updated = True

        data = {
            "updated": updated,
            "liked": liked
        }

        return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def api_create_blog_view(request):
    if request.method == "POST":

        data = request.data
        data['author'] = request.user.id
        serializer = BlogPostCreateSerializer(data=data)

        data = {}
        if serializer.is_valid():
            blog_post = serializer.save()
            data['response'] = CREATE_SUCCESS
            data['id'] = blog_post.id
            data['title'] = blog_post.title
            data['body'] = blog_post.body
            data['slug'] = blog_post.slug
            data['image'] = blog_post.image.url
            data['author'] = blog_post.author.username
            data['author_id'] = blog_post.author.id
            data['timestamp'] = blog_post.timestamp
            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApiBlogListView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = BlogPostSerializer
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'body', 'author__username')

    def get_queryset(self, *args, **kwargs):
        queryset = BlogPost.objects.filter(is_draft=False).order_by('-date_published')

        return queryset


class ApiUserBlogListView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = BlogPostSerializer
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'body', 'author__username')
    lookup_url_kwarg = "uid"

    def get_queryset(self, *args, **kwargs):
        uid = self.kwargs.get(self.lookup_url_kwarg)
        queryset = BlogPost.objects.filter(is_draft=False, author=uid).order_by('-date_published')

        return queryset


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def api_is_author_of_blogpost(request, slug):
    try:
        blog_post = BlogPost.objects.get(slug=slug, is_draft=False)
    except BlogPost.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = {}
    user = request.user
    if blog_post.author != user:
        data['response'] = "You don't have permission to edit that."
        return Response(data=data)
    data['response'] = "You have permission to edit that."
    return Response(data=data)
