import os
import tempfile

import numpy as np
import rasterio
import tensorflow as tf


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "CNN_MARE_model.h5")

model = tf.keras.models.load_model(MODEL_PATH)

CLASSES = ["maré baixa", "maré média", "maré alta", "indeterminada"]


def _open_raster_from_django_file(django_file):
    """
    Aceita um UploadedFile do Django, grava em um arquivo temporário
    e abre com o rasterio.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".tif")
    try:
        # Para InMemoryUploadedFile / TemporaryUploadedFile
        if hasattr(django_file, "chunks"):
            for chunk in django_file.chunks():
                tmp.write(chunk)
        else:
            # Qualquer outro file-like com .read()
            data = django_file.read()
            tmp.write(data)

        tmp.flush()
        tmp.close()

        # Lê todas as bandas da imagem (bands, H, W)
        with rasterio.open(tmp.name) as src:
            img = src.read()

        return img

    finally:
        try:
            os.remove(tmp.name)
        except Exception:
            # Se não conseguir apagar, não quebra a predição.
            pass

    # Em caso de erro na abertura/leitura, quem chamou lida com isso
    return None


def preprocess_image(file):
    """
    `file` pode ser:
    - caminho da imagem (string / Path);
    - arquivo enviado via Django (request.FILES["image"]). 
    """
    # Caso seja caminho de arquivo (string / PathLike)
    if isinstance(file, (str, os.PathLike)):
        with rasterio.open(file) as src:
            # Lê todas as bandas disponíveis (bands, H, W)
            img = src.read()
    else:
        # UploadedFile ou file-like vindo da API
        img = _open_raster_from_django_file(file)

    if img is None:
        raise ValueError("Não foi possível ler a imagem enviada.")

    # Se a imagem tiver apenas 3 bandas (RGB), cria uma 4ª banda
    # duplicando a primeira, para casar com o modelo treinado (4 canais).
    if img.shape[0] == 3:
        extra_band = img[0:1, :, :]
        img = np.concatenate([img, extra_band], axis=0)

    # (bands, H, W) -> (H, W, bands)
    img = np.moveaxis(img, 0, -1).astype("float32") / 255.0

    # Garante que a imagem tenha a mesma dimensão espacial usada no treino.
    # O modelo foi treinado com um tamanho fixo (por ex. 384x384);
    # se a imagem tiver outro tamanho (como 200x202), redimensionamos.
    target_h, target_w = model.input_shape[1], model.input_shape[2]
    if img.shape[0] != target_h or img.shape[1] != target_w:
        img = tf.image.resize(img, (target_h, target_w)).numpy()

    # adicionar batch
    img = np.expand_dims(img, axis=0)

    return img


def predict(file):
    img = preprocess_image(file)
    preds = model.predict(img)

    class_index = np.argmax(preds)
    confidence = float(np.max(preds))

    return CLASSES[class_index], confidence