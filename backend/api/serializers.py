from rest_framework import serializers

class ClassificationRequestSerializer(serializers.Serializer):
    image = serializers.ImageField(required=False)
    image_path = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        image = attrs.get('image')
        image_path = attrs.get('image_path')

        #Nenhum dos dois preenchidos
        if not image and not image_path:
            raise serializers.ValidationError(
                "nenhuma imagem enviada. Use o campo 'image' (arquivo) ou 'image_path' (caminho)."
            )
        #ambos preenchidos
        if image and image_path:
            raise serializers.ValidationError(
                "ambos os campos 'image' e 'image_path' não podem ser preenchidos simultaneamente."
            )
        
        return attrs