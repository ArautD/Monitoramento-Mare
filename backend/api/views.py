from pathlib import Path
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .ml.model import predict
from .serializers import ClassificationRequestSerializer


@api_view(["POST"])
def classify2(request):
    """método para quando for selecionar no mapa"""
    lat = request.data.get("lat")
    lon = request.data.get("lon")

    return Response(
        {
            "message": "API ON",
            "lat": lat,
            "lon": lon,
        }
    )

class ClassifyView(APIView):
    def post(self, request):
        serializer = ClassificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image = serializer.validated_data.get("image")
        image_path = serializer.validated_data.get("image_path")

        try:
            if image is not None:
                clas, confidence = predict(image)
            else:
                path = Path(image_path)
                if not path.is_file():
                    return Response(
                        {"error": f"arquivo não encontrado no servidor: {image_path}"},
                        status = status.HTTP_400_BAD_REQUEST
                    )
                clas, confidence = predict(str(path))

            return Response(
                {"class": clas,"confidence": confidence},
                status = status.HTTP_200_OK,     
            )
        except Exception as exc:
            return Response(
                {"error": "falha ao classificar imagem", "detail": str(exc)},
                status = status.HTTP_500_INTERNAL_SERVER_ERROR,
            )