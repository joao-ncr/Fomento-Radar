"""Gera a narração (ElevenLabs) e o arquivo de tempos que sincroniza cenas e legendas.

Uso:
  python3 tts.py            # tenta ElevenLabs; se não houver acesso, usa tempos estimados
  python3 tts.py --estimate # força tempos estimados (sem voz)

Saídas em build/: voz.mp3 (se houver voz) e timing.json.
A chave da ElevenLabs não fica no código: o proxy do ambiente injeta o header xi-api-key.
"""
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
API = "https://api.elevenlabs.io/v1"
# Predefinições de voz (env VOZ). Todas são vozes padrão da ElevenLabs, liberadas no plano gratuito
# (vozes da biblioteca, inclusive as nativas brasileiras, exigem plano pago via API).
#   tempo: aceleração aplicada depois (ffmpeg atempo, sem alterar o tom); os tempos são ajustados junto.
PRESETS = {
    "a": {"nome": "Chris (v3)", "voice": "iP95p4xoKVk53GoZ742B", "model": "eleven_v3",
          "settings": {"stability": 0.5}, "tempo": 1.10},
    "b": {"nome": "Brian (turbo v2.5, pt forçado)", "voice": "nPczCjzI2devNBz1zQrb", "model": "eleven_turbo_v2_5",
          "settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.3, "speed": 1.15}, "tempo": 1.0},
}
PRESET = PRESETS[os.environ.get("VOZ", "a")]
if os.environ.get("ELEVEN_VOICE_ID"):
    PRESET = {**PRESET, "voice": os.environ["ELEVEN_VOICE_ID"]}


def load_script():
    with open(os.path.join(HERE, "roteiro.json"), encoding="utf-8") as f:
        return json.load(f)


def build_text(segs):
    """Concatena os segmentos e devolve o texto e os offsets de cada segmento."""
    text, spans = "", []
    for s in segs:
        if text:
            text += " "
        start = len(text)
        text += s["texto"]
        spans.append((s["id"], start, len(text)))
    return text, spans


def words_with_offsets(text):
    return [(m.group(0), m.start(), m.end()) for m in re.finditer(r"\S+", text)]


def req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            # valor fictício: o proxy do ambiente substitui pela chave real
            "xi-api-key": os.environ.get("ELEVEN_API_KEY", "proxy-injected"),
        },
    )
    with urllib.request.urlopen(r, timeout=180) as resp:
        return json.loads(resp.read())


def synthesize(text):
    voice, model = PRESET["voice"], PRESET["model"]
    body = {"text": text, "model_id": model, "language_code": "pt", "voice_settings": PRESET["settings"]}
    out = req("POST", f"/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128", body)
    raw = os.path.join(BUILD, "voz_bruta.mp3")
    with open(raw, "wb") as f:
        f.write(base64.b64decode(out["audio_base64"]))
    tempo = PRESET["tempo"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", f"atempo={tempo}",
                    "-c:a", "libmp3lame", "-b:a", "192k", os.path.join(BUILD, "voz.mp3")], check=True)
    al = out["alignment"]
    starts = [x / tempo for x in al["character_start_times_seconds"]]
    ends = [x / tempo for x in al["character_end_times_seconds"]]
    if "".join(al["characters"]) != text:
        raise RuntimeError("alinhamento não bate com o texto enviado")
    return PRESET["nome"], starts, ends


def estimate(text):
    """Tempos aproximados (~14,5 caracteres/s com pausas na pontuação)."""
    rate, t = 1 / 14.5, 0.25
    starts, ends = [], []
    for ch in text:
        starts.append(t)
        t += rate
        if ch == "…":
            t += 0.38
        elif ch in ".?!":
            t += 0.30
        elif ch == ":":
            t += 0.22
        elif ch == ",":
            t += 0.12
        ends.append(t)
    return starts, ends


def main():
    os.makedirs(BUILD, exist_ok=True)
    script = load_script()
    segs = script["segmentos"]
    text, spans = build_text(segs)
    voice = None
    if "--estimate" not in sys.argv:
        try:
            voice, starts, ends = synthesize(text)
            print(f"voz gerada com a voz {voice}")
        except Exception as e:  # sem acesso à API: segue com estimativa
            print(f"ElevenLabs indisponível ({e}); usando tempos estimados", file=sys.stderr)
    if voice is None:
        starts, ends = estimate(text)
        vp = os.path.join(BUILD, "voz.mp3")
        if os.path.exists(vp):
            os.remove(vp)

    words = []
    for w, a, b in words_with_offsets(text):
        seg = next(sid for sid, s0, s1 in spans if s0 <= a < s1)
        words.append({"w": w, "start": round(starts[a], 3), "end": round(ends[b - 1], 3), "seg": seg})

    seg_times = []
    for i, (sid, a, b) in enumerate(spans):
        st = starts[a]
        seg_times.append({"id": sid, "start": round(st, 3), "speechEnd": round(ends[b - 1], 3)})
    for i, s in enumerate(seg_times):
        # cada cena começa um pouco antes da fala e vai até a próxima cena
        s["start"] = 0.0 if i == 0 else round(max(0.0, s["start"] - 0.12), 3)
    tail = 2.4  # respiro final para o CTA
    total = round(ends[-1] + tail, 3)
    for i, s in enumerate(seg_times):
        s["end"] = seg_times[i + 1]["start"] if i + 1 < len(seg_times) else total

    highlights = {s["id"]: s.get("destaque", []) for s in segs}
    timing = {"duration": total, "hasVoice": voice is not None, "voice": voice,
              "segments": seg_times, "words": words, "highlights": highlights,
              "disclaimer": script["aviso"]}
    with open(os.path.join(BUILD, "timing.json"), "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=1)
    print(f"duração: {total:.1f}s, voz: {'sim' if voice else 'não (estimada)'}")


if __name__ == "__main__":
    main()
