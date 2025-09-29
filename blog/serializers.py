from rest_framework import serializers
from .models import Reaction


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        # dejamos solo los campos que queremos exponer; post y user serán read-only
        fields = ["id", "type", "created_at", "post", "user"]
        read_only_fields = ["id", "user", "post", "created_at"]
        extra_kwargs = {
            # rating/opinion no están en fields, así que no serán requeridos
            "type": {"required": True},
            "rating": {"required": False, "allow_null": True},
            "opinion": {"required": False, "allow_blank": True},
        }

    def create(self, validated_data):
        request = self.context.get("request")
        post = self.context.get("post")
        user = request.user

        reaction, created = Reaction.objects.update_or_create(
            post=post,
            user=user,
            defaults={"type": validated_data.get("type")}
        )
        return reaction
