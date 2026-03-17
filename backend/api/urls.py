from django.urls import path
from .views import ClassifyView, AreaGeoJSONView, areas_geojson, points_geojson

urlpatterns = [
    path("classify/" , ClassifyView.as_view()),
    path("areas-geojson/", AreaGeoJSONView.as_view()),
    path("api/areas_geojson/", areas_geojson),
    path("points-geojson/", points_geojson),
]