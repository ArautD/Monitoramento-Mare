"use client";

import { useState } from "react";

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ class: string; confidence: number } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

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
    <main className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 md:p-8">
        <h1 className="text-2xl md:text-3xl font-semibold mb-2">
          Monitoramento de Maré
        </h1>
        <p className="text-slate-400 mb-6 text-sm md:text-base">
          Envie uma imagem de satélite para classificar o tipo de uso/cobertura.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-200 mb-2">
              Imagem (.tif, .jpg, .png)
            </label>
            <input
              type="file"
              accept=".tif,.tiff,image/*"
              onChange={(e) => {
                const f = e.target.files?.[0] || null;
                setFile(f);
              }}
              className="block w-full text-sm text-slate-300
                         file:mr-4 file:py-2 file:px-4
                         file:rounded-md file:border-0
                         file:text-sm file:font-semibold
                         file:bg-emerald-500 file:text-slate-950
                         hover:file:bg-emerald-400
                         cursor-pointer"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full inline-flex items-center justify-center rounded-md
                       bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950
                       hover:bg-emerald-400 disabled:opacity-60 disabled:cursor-not-allowed
                       transition-colors"
          >
            {loading ? "Classificando..." : "Enviar para classificação"}
          </button>
        </form>

        {error && (
          <div className="mt-4 rounded-md bg-red-900/40 border border-red-700 px-3 py-2 text-sm text-red-200">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-4 rounded-md bg-slate-800 border border-slate-700 px-3 py-3">
            <h2 className="text-sm font-semibold text-slate-200 mb-1">
              Resultado da classificação
            </h2>
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
    </main>
  );
}