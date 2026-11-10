#!/usr/bin/env bash
# Pipeline completo do reels: voz -> tempos -> quadros -> trilha/efeitos -> mixagem final.
# Uso: ./build.sh            (tenta ElevenLabs; sem acesso, usa tempos estimados e sai sem narração)
#      ./build.sh --estimate (força versão sem voz)
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build out

python3 tts.py "$@"
node render.cjs
python3 audio.py

if [ -f build/voz.mp3 ]; then
  # música abaixa (sidechain) quando a voz entra; normaliza para -14 LUFS (padrão de redes sociais)
  ffmpeg -y -loglevel error -i build/video.mp4 -i build/voz.mp3 -i build/musica.wav -i build/sfx.wav -filter_complex "
    [1:a]aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=1.0,asplit=2[v][vsc];
    [2:a]volume=0.32[m];
    [m][vsc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=300[md];
    [3:a]volume=0.55[fx];
    [v][md][fx]amix=inputs=3:normalize=0:duration=longest,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.84:level=false[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "out/fomentoradar_reels_opcao_${VOZ:-a}.mp4"
  echo "vídeo final com narração: "out/fomentoradar_reels_opcao_${VOZ:-a}.mp4""
else
  ffmpeg -y -loglevel error -i build/video.mp4 -i build/musica.wav -i build/sfx.wav -filter_complex "
    [1:a]volume=0.5[m];[2:a]volume=0.6[fx];[m][fx]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.84:level=false[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/fomentoradar_reels_sem_voz.mp4
  echo "vídeo sem narração (prévia de ritmo): out/fomentoradar_reels_sem_voz.mp4"
fi
