import json
from pathlib import Path
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .ml.model import predict
from .serializers import ClassificationRequestSerializer
from .models import Classification
from django.http import JsonResponse
from django.conf import settings
from pathlib import Path

@api_view(["GET"])
def areas_geojson(request):
    # Arquivos GeoJSON ficam em backend/app/data/
    file_path = Path(settings.BASE_DIR) / "app" / "data" / "areas.geojson"

    with open(file_path, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    return JsonResponse(geojson)


@api_view(["GET"])
def points_geojson(request):
    """
    Retorna os pontos pré-setados (cada ponto representa uma imagem disponível).
    """
    # Arquivos GeoJSON ficam em backend/app/data/
    file_path = Path(settings.BASE_DIR) / "app" / "data" / "point.geojson"

    with open(file_path, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    return JsonResponse(geojson)


class AreaGeoJSONView(APIView): #classe para deixar pontos no mapa (imagens de áreas já baixadas)
    def get(self, request):
        features = []

        qs = Classification.objects.exclude(extra_info=None)

        for obj in qs:
            coords = obj.extra_info.get("coordinates")
            if not coords:
                continue

            features.append({
                "type": "Feature",
                "properties": {
                    "id": obj.id,
                    "class": obj.prediction_class,
                    "confidence": obj.confidence,
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": coords,
                },
            })
        return Response({
            "type": "FeatureCollection",
            "features": features
        })


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
                Classification.objects.create(
                    image_name = getattr(image, "name", "") if image is not None else "",
                    image_path = str(path) if image is None else "",
                    prediction_class = clas,
                    confidence = confidence,
                    extra_info = {},
                )
                
            return Response(
                {"class": clas,"confidence": confidence},
                status = status.HTTP_200_OK,     
            )
        except Exception as exc:
            return Response(
                {"error": "falha ao classificar imagem", "detail": str(exc)},
                status = status.HTTP_500_INTERNAL_SERVER_ERROR,
            )