import json
import rasterio
import numpy as np

from pathlib import Path
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .ml.model import predict
from .serializers import ClassificationRequestSerializer
from .models import Classification
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from PIL import Image

def _resolve_image_path(image_path: str) -> Path:
    """
    Resolve caminhos de imagem vindos do frontend/geojson.

    Aceita:
    - caminhos absolutos (Windows/Linux)
    - relativos como "backend/app/data/img/arquivo.tif"
    - relativos como "app/data/img/arquivo.tif"
    - relativos como "img/arquivo.tif" (se existir)

    Retorna o primeiro path existente; caso nenhum exista, retorna o candidato mais provável.
    """
    p = Path(image_path)
    if p.is_absolute():
        return p

    # Tentativas comuns, considerando que settings.BASE_DIR = ".../backend"
    candidates = [
        p,  # relativo ao CWD (pode falhar)
        Path(settings.BASE_DIR) / p,
        Path(settings.BASE_DIR).parent / p,
    ]

    # Se vier prefixado com "backend/...", remove esse prefixo (evita backend/backend/...)
    parts = p.parts
    if len(parts) >= 2 and parts[0].lower() == "backend":
        p2 = Path(*parts[1:])
        candidates.extend(
            [
                Path(settings.BASE_DIR) / p2,
                Path(settings.BASE_DIR).parent / p2,
            ]
        )

    for c in candidates:
        if c.is_file():
            return c

    # fallback: tende a ser o local real onde estão seus arquivos
    return Path(settings.BASE_DIR) / "app" / "data" / "img" / p.name


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

def point_preview(request, id):
    
    geojson_path = Path(settings.BASE_DIR) / "app" / "data" / "point.geojson"

    with open(geojson_path) as f:
        data = json.load(f)

    feature = next(
        (f for f in data["features"] if f["properties"]["id"] == id),
        None
    )

    if not feature:
        return JsonResponse({"error": "Point not found"}, status = 404)

    image_path = feature["properties"]["image_path"]

    tif_path = _resolve_image_path(image_path)

    if not tif_path.is_file():
        return JsonResponse(
            {"error": f"arquivo não encontrado no servidor: {str(tif_path)}"},
            status=404,
        )

    with rasterio.open(tif_path) as src:
        if src.count < 3:
            return JsonResponse(
                {"error": f"imagem precisa ter pelo menos 3 bandas para preview, mas tem {src.count}"},
                status=400,
            )
        r = src.read(1).astype(np.float32)
        g = src.read(2).astype(np.float32)
        b = src.read(3).astype(np.float32)

    rgb = np.dstack((r,g,b))

    # Normalização robusta para 0-255 (evita divisão por zero)
    vmin = float(np.min(rgb))
    vmax = float(np.max(rgb))
    denom = vmax - vmin
    if denom <= 0:
        rgb8 = np.zeros_like(rgb, dtype=np.uint8)
    else:
        rgb8 = ((rgb - vmin) / denom * 255.0).clip(0, 255).astype(np.uint8)

    img = Image.fromarray(rgb8)

    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format = "PNG")

    return HttpResponse(buffer.getvalue(), content_type="image/png")

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
                path = _resolve_image_path(image_path)
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