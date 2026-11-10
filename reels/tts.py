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
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
API = "https://api.elevenlabs.io/v1"
MODEL = "eleven_multilingual_v2"
# Voz masculina padrão; pode ser trocada via env ELEVEN_VOICE_ID.
DEFAULT_VOICE = os.environ.get("ELEVEN_VOICE_ID", "TX3LPaxmHKxFdv7VOQHJ")  # "Liam": masculina, energética, estilo redes sociais
FALLBACK_VOICE = "pNInz6obpgDQGcFmaJgB"  # "Adam", masculina, funciona em pt-BR no multilingual_v2


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


def pick_voice():
    if DEFAULT_VOICE:
        return DEFAULT_VOICE
    try:
        voices = req("GET", "/voices")["voices"]
    except Exception:
        return FALLBACK_VOICE
    def score(v):
        lab = {k: str(x).lower() for k, x in (v.get("labels") or {}).items()}
        s = 0
        if lab.get("gender") == "male":
            s += 10
        if "brazil" in lab.get("accent", "") or "portug" in lab.get("language", "") or lab.get("language") == "pt":
            s += 5
        if any(k in lab.get("description", "") + lab.get("use_case", "") for k in ("narrat", "conversational", "social")):
            s += 2
        return s
    best = max(voices, key=score) if voices else None
    return best["voice_id"] if best and score(best) >= 10 else FALLBACK_VOICE


def synthesize(text):
    voice = pick_voice()
    body = {
        "text": text,
        "model_id": MODEL,
        "language_code": "pt",
        "voice_settings": {"stability": 0.38, "similarity_boost": 0.8, "style": 0.45, "use_speaker_boost": True, "speed": 1.08},
    }
    try:
        out = req("POST", f"/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128", body)
    except urllib.error.HTTPError as e:
        # language_code/speed não são aceitos por todos os modelos: tenta sem eles
        if e.code in (400, 422):
            body.pop("language_code", None)
            body["voice_settings"].pop("speed", None)
            out = req("POST", f"/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128", body)
        else:
            raise
    audio = base64.b64decode(out["audio_base64"])
    with open(os.path.join(BUILD, "voz.mp3"), "wb") as f:
        f.write(audio)
    al = out["alignment"]
    starts, ends = al["character_start_times_seconds"], al["character_end_times_seconds"]
    if "".join(al["characters"]) != text:
        raise RuntimeError("alinhamento não bate com o texto enviado")
    return voice, starts, ends


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
