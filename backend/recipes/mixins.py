from rest_framework import serializers


class ImageMixin(serializers.Serializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
