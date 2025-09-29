# blog/api_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Post, Comment
from .serializers import ReactionSerializer

class ReactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_id = request.data.get("post")
        if not post_id:
            return Response({"error": "Se requiere el ID del post"}, status=status.HTTP_400_BAD_REQUEST)

        post = get_object_or_404(Post, id=post_id)

        serializer = ReactionSerializer(
            data=request.data,
            context={"request": request, "post": post}
        )
        serializer.is_valid(raise_exception=True)
        reaction = serializer.save()

        # Ajusta los campos si tu modelo Comment usa 'author'/'text' u otros nombres
        Comment.objects.create(
            post=post,
            author=request.user,
            text=f"{request.user.username} reaccionó con {reaction.type}"
        )

        return Response(ReactionSerializer(reaction).data, status=status.HTTP_201_CREATED)
