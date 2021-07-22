from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from blog.models import BlogPost
from blog.utils import validate_uuid4
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


class ApiBlogListView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = BlogPostSerializer
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'author__username')

    def get_queryset(self, *args, **kwargs):
        queryset = BlogPost.objects.filter(is_draft=False).order_by('-date_published')

        return queryset


class ApiUserBlogListView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = BlogPostSerializer
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'author__username')
    lookup_url_kwarg = "uid"

    def get_queryset(self, *args, **kwargs):
        uid = self.kwargs.get(self.lookup_url_kwarg)
        queryset = BlogPost.objects.filter(is_draft=False, author=uid).order_by('-date_published')

        return queryset


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
def api_detail_blog_view(request, post_id):
    data = {}

    is_uuid = validate_uuid4(post_id)
    if not is_uuid:
        data['response'] = "error"
        data["message"] = "Post ID is invalid."
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    try:
        blog_post = BlogPost.objects.get(id=post_id, is_draft=False)
    except BlogPost.DoesNotExist:
        data['response'] = "error"
        data["message"] = "Post doesn't found."
        return Response(data=data, status=status.HTTP_404_NOT_FOUND)

    serializer = BlogPostSerializer(blog_post, context={'request': request})

    if request.method == "GET":
        return Response(serializer.data, status=status.HTTP_200_OK)
    data["response"] = "error"
    data["message"] = serializer.errors
    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes((IsAuthenticated,))
def api_update_blog_view(request, post_id):
    data = {}

    is_uuid = validate_uuid4(post_id)
    if not is_uuid:
        data['response'] = "error"
        data["message"] = "Post ID is invalid."
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    try:
        blog_post = BlogPost.objects.get(id=post_id, is_draft=False)
    except BlogPost.DoesNotExist:
        data['response'] = "error"
        data["message"] = "Post doesn't found."
        return Response(data=data, status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if blog_post.author != user:
        data['response'] = "error"
        data["message"] = "You don't have permission to delete this post."
        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "PUT":
        serializer = BlogPostUpdateSerializer(
            blog_post,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            data['response'] = "success"
            data['message'] = "Post updated successfully"
            data['id'] = blog_post.id
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def api_delete_blog_view(request, post_id):
    data = {}

    is_uuid = validate_uuid4(post_id)
    if not is_uuid:
        data['response'] = "error"
        data["message"] = "Post ID is invalid."
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    try:
        blog_post = BlogPost.objects.get(id=post_id, is_draft=False)
    except BlogPost.DoesNotExist:
        data['response'] = "error"
        data["message"] = "Post doesn't found."
        return Response(data=data, status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if blog_post.author != user:
        data['response'] = "error"
        data["message"] = "You don't have permission to delete this post."
        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'DELETE':
        operation = blog_post.delete()
        if operation:
            data['response'] = "success"
            data["message"] = "Post deleted successfully."
            return Response(data=data, status=status.HTTP_200_OK)

        data["response"] = "error"
        data["message"] = "Post deletion failed."
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def api_like_toggle_view(request, post_id):
    data = {}

    is_uuid = validate_uuid4(post_id)
    if not is_uuid:
        data['response'] = "error"
        data["message"] = "Post ID is invalid."
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    try:
        blog_post = BlogPost.objects.get(id=post_id, is_draft=False)
    except BlogPost.DoesNotExist:
        data['response'] = "error"
        data["message"] = "Post doesn't found."
        return Response(data=data, status=status.HTTP_404_NOT_FOUND)

    if request.user.is_authenticated:
        if request.user in blog_post.likes.all():
            blog_post.likes.remove(request.user)
            liked = False
            message = "Like removed."
        else:
            blog_post.likes.add(request.user)
            liked = True
            message = "Post liked."

        updated = True

        data["updated"] = updated
        data["liked"] = liked
        data["message"] = message
        return Response(data, status=status.HTTP_200_OK)
    else:
        data["response"] = "error"
        data["message"] = "An error occurred"
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def api_create_blog_view(request):
    if request.method == "POST":

        req_data = request.data
        req_data['author'] = request.user.id
        serializer = BlogPostCreateSerializer(data=req_data)

        data = {}
        if serializer.is_valid():
            blog_post = serializer.save()
            data['response'] = "success"
            data['message'] = "Post created successfully."
            data['id'] = blog_post.id
            return Response(data=data, status=status.HTTP_201_CREATED)
        data["response"] = "error"
        data["message"] = serializer.errors
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def api_is_author_of_blogpost(request, post_id):
    try:
        blog_post = BlogPost.objects.get(id=post_id, is_draft=False)
    except BlogPost.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = {}
    user = request.user
    if blog_post.author != user:
        data['response'] = "error"
        data["message"] = "You don't have any permission to this post."
        return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
    data["response"] = "success"
    data['message'] = "You have permission to edit this post."
    return Response(data=data, status=status.HTTP_200_OK)
