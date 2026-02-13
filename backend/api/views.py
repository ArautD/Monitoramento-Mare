from pathlib import Path

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .ml.model import predict


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


@api_view(["POST"])
def classify(request):
    """
    Endpoint de classificação.

    Aceita:
    - upload de arquivo (multipart/form-data) com o campo "image";
    - OU caminho de arquivo no servidor, via JSON: {"image_path": "img/minha_imagem.tif"}.
    """
    file = request.FILES.get("image")
    image_path = request.data.get("image_path")

    if not file and not image_path:
        return Response(
            {"error": "nenhuma imagem enviada. Use o campo 'image' (arquivo) ou 'image_path' (caminho)."},
            status=400,
        )

    try:
        if file is not None:
            # Caso 1: upload de arquivo
            clas, confidence = predict(file)
        else:
            # Caso 2: caminho de arquivo existente no servidor
            path = Path(image_path)
            if not path.is_file():
                return Response(
                    {"error": f"arquivo não encontrado no servidor: {image_path}"},
                    status=400,
                )
            clas, confidence = predict(str(path))

        return Response(
            {
                "class": clas,
                "confidence": confidence,
            }
        )
    except Exception as exc:
        # Facilita ver o erro exato durante desenvolvimento
        return Response(
            {"error": "falha ao classificar imagem", "detail": str(exc)},
            status=500,
        )