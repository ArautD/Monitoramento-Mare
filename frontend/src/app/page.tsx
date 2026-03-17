"use client";

import { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || "";

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ class: string; confidence: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isMapOpen, setIsMapOpen] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [selectedArea, setSelectedArea] = useState<any>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  const mapContainerRef = useRef<HTMLDivElement | null>(null);

  

  useEffect(() => {
    if (!isMapOpen || !mapContainerRef.current || !mapboxgl.accessToken) return;
  
    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: "mapbox://styles/mapbox/satellite-streets-v12", // estilo de satélite
      center: [-48, -10], // ajuste para a área que você quer focar
      zoom: 4,
    });
    
    map.on("load", async() => {
      if (!apiUrl) return;

      // Carrega apenas os pontos (cada ponto representa uma imagem disponível)
      const pointsResponse = await fetch(`${apiUrl}/api/points-geojson/`);
      const pointsGeojson = await pointsResponse.json();

      map.addSource("points", {
        type: "geojson",
        data: pointsGeojson,
      });

      map.addLayer({
        id: "points-circle",
        type: "circle",
        source: "points",
        paint: {
          "circle-radius": 6,
          "circle-color": "#ef4444",
          "circle-stroke-width": 2,
          "circle-stroke-color": "#ffffff",
        },
      });

      map.on("click", "points-circle", (e) => {
        const feature = e.features?.[0];
        if (!feature) return;

        const props = feature.properties as any;
        setSelectedArea({
          nome: props.area_name ?? props.area_nome ?? props.nome ?? "Ponto",
          year: props.year,
          month: props.month,
          tile: props.tile,
          image_path: props.image_path,
        });

        alert(
          `Imagem selecionada: ${props.area_name ?? props.nome} - ${props.month}/${props.year} (tile ${props.tile})`
        );
      });

      // cursor bonito
      map.on("mouseenter", "points-circle", () => {
        map.getCanvas().style.cursor = "pointer";
      });

      map.on("mouseleave", "points-circle", () => {
        map.getCanvas().style.cursor = "";
      });
  });

    // opcional: desabilitar scroll zoom
    // map.scrollZoom.disable();
  
    return () => {
      map.remove();
    };
  }, [isMapOpen]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);

    if (!file) {
      setError("Selecione uma imagem antes de enviar.");
      return;
    }

    if (!apiUrl) {
      setError("Variável NEXT_PUBLIC_API_URL não está definida.");
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append("image", file);

      const response = await fetch(`${apiUrl}/api/classify/`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.error || "Erro ao chamar a API.");
      }

      const data = await response.json();
      setResult({
        class: data.class,
        confidence: data.confidence,
      });
    } catch (err: any) {
      setError(err.message || "Erro inesperado.");
    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-50">
      {/* Fundo com planeta terra girando + blur */}
      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        <div className="h-[120vmin] w-[120vmin] rounded-full bg-[url('/earth.jpg')] bg-cover bg-center opacity-40 blur-sm animate-[spin_60s_linear_infinite]" />
        <div className="absolute inset-0 bg-gradient-to-b from-slate-950/90 via-slate-950/80 to-slate-950" />
      </div>

      {/* Hero / Landing */}
      <section className="relative z-10 flex min-h-screen items-center justify-center px-4">
        <div className="max-w-3xl rounded-3xl border border-slate-800/60 bg-slate-950/40 p-8 shadow-2xl backdrop-blur-xl">
          <p className="mb-3 text-xs font-medium uppercase tracking-[0.25em] text-emerald-300/80">
            Monitoramento Costeiro Inteligente
          </p>
          <h1 className="mb-4 text-3xl md:text-4xl lg:text-5xl font-semibold leading-tight">
            Monitoramento de Maré a partir de imagens de satélite
          </h1>
          <p className="mb-8 text-sm md:text-base text-slate-300 max-w-2xl">
            Este projeto utiliza redes neurais convolucionais para classificar o estado da maré
            em regiões costeiras, a partir de imagens de satélite. Explore diferentes formas de
            interação com os dados: envie uma imagem ou selecione uma área de interesse.
          </p>

          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              onClick={() => setIsUploadOpen(true)}
              className="inline-flex items-center justify-center rounded-full bg-emerald-500 px-6 py-2.5 text-sm font-semibold text-slate-950 shadow-lg shadow-emerald-500/30 transition hover:bg-emerald-400"
            >
              Enviar imagem de satélite
            </button>
            <button
              onClick={() => setIsMapOpen(true)}
              className="inline-flex items-center justify-center rounded-full border border-slate-600 bg-slate-900/40 px-6 py-2.5 text-sm font-semibold text-slate-100 transition hover:border-emerald-400 hover:text-emerald-200"
            >
              Selecionar uma área
            </button>
          </div>
        </div>
      </section>

      {isUploadOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
        <div className="relative w-full max-w-xl rounded-2xl bg-slate-950 border border-slate-800 p-4 md:p-6">
          <button
            onClick={() => setIsUploadOpen(false)}
            className="absolute right-4 top-3 text-slate-400 hover:text-slate-100 text-sm"
          >
            Fechar
          </button>
          <h2 className="mb-2 text-xl font-semibold text-slate-100">
            Enviar imagem de satélite
          </h2>
          <p className="mb-4 text-sm text-slate-400">
            Faça o upload de um arquivo GeoTIFF ou imagem compatível para obter a classificação
            automática do estado da maré.
          </p>
    
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-200">
                Imagem (.tif, .jpg, .png)
              </label>
              <input
                type="file"
                accept=".tif,.tiff,image/*"
                onChange={(e) => {
                  const f = e.target.files?.[0] || null;
                  setFile(f);
                }}
                className="block w-full cursor-pointer text-sm text-slate-300 file:mr-4 file:cursor-pointer file:rounded-md file:border-0 file:bg-emerald-500 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-slate-950 hover:file:bg-emerald-400"
              />
            </div>
    
            <button
              type="submit"
              disabled={loading}
              className="inline-flex w-full items-center justify-center rounded-md bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 transition-colors hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Classificando..." : "Enviar para classificação"}
            </button>
          </form>
    
          {error && (
            <div className="mt-4 rounded-md border border-red-700 bg-red-900/40 px-3 py-2 text-sm text-red-200">
              {error}
            </div>
          )}
    
          {result && (
            <div className="mt-4 rounded-md border border-slate-700 bg-slate-800/80 px-3 py-3">
              <h3 className="mb-1 text-sm font-semibold text-slate-200">
                Resultado da classificação
              </h3>
              <p className="text-sm text-slate-300">
                <span className="font-medium">Classe:</span> {result.class}
              </p>
              <p className="text-sm text-slate-300">
                <span className="font-medium">Confiança:</span>{" "}
                {(result.confidence * 100).toFixed(2)}%
              </p>
            </div>
          )}
        </div>
      </div>
      )}

      {isMapOpen && (
        <div className = "fixed inset-0 z-50 flex items-center justify-center bg-black/70">
          <div className="relative w-full max-w-5x1 rounded-2x1 bg-slate-950 border border-slate-800 p-4 md:p-6">
            <button
            onClick={() => setIsMapOpen(false)}
            className="absolute right-4 top-3 text-slate-400 hover:text-slate-100 text-sm"
            >
              Fechar
            </button>
            <h2 className="mb-3 text-lg font-semibold text-slate-100">
            Selecione a área de interesse
            </h2>
            <div className="grid gap-4 md:grid-cols-[minmax(0,2fr)_minmax(0,1fr)] items-start">
              <div
              ref={mapContainerRef}
              className="h-80 w-full rounded-2x1 border border-slate-800 bg-slate-900"
              />
            <div className="text-sm text-slate-300 space-y-2">
              {!selectedArea &&(
                <p className="text-slate-400">
                  Clique em uma área do mapa para selecionar.
                </p>
              )}
              {selectedArea && (
                <>
                  <p><span className="font-semibold">Nome:</span> {selectedArea.nome}</p>
                  <p><span className="font-semibold">Classe:</span> {selectedArea.class}</p>
                  <p>
                    <span className="font-semibold">Confiança:</span>{" "}
                    {(selectedArea.confidence * 100).toFixed(2)}%
                  </p>

                  <button
                    className="mt-3 w-full rounded-md bg-emerald-500 px-3 py-2 text-sm font-semibold text-slate-950 hover:bg-emerald-400"
                    onClick={() => {
                      console.log("Área confirmada:", selectedArea);
                      setIsMapOpen(false);
                    }}
                  >
                    Usar esta área
                  </button>
                </>
              )}
              <p className="mb-2">
                Interaja com o mapa para selecionar a área de linha de costa
              </p>
              <p className="text-xs text-slate-500">
                Nesta primeira versão do mapa é apenas visual, depois lembrar de adicionar get
              </p>
            </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}