# Reels de apresentação do FomentoRadar

Vídeo vertical (1080×1920, 30 fps, cerca de 45 s) para apresentar o conceito a startups e aceleradoras.
É um **protótipo ilustrativo**: o portal ainda não existe, e os editais, instituições e a empresa do vídeo são fictícios.

## Estrutura

| Arquivo | Função |
|---|---|
| `roteiro.json` | Roteiro em segmentos (narração, palavras de destaque e descrição visual). É a única fonte do texto. |
| `tts.py` | Gera a narração na ElevenLabs (voz masculina, `eleven_multilingual_v2`) com tempos por caractere. Sem acesso à API, estima os tempos. |
| `reel.html` | Telas do portal e animações, controladas por `render(t)` (determinístico). Abra com `?play` num navegador para assistir em tempo real (requer `build/timing.json` injetado como `window.TIMING`). |
| `render.cjs` | Captura quadro a quadro com Playwright e codifica com ffmpeg. |
| `audio.py` | Sintetiza a trilha (118 BPM) e os efeitos sonoros a partir das pistas da animação. Não usa samples de terceiros. |
| `build.sh` | Roda tudo e mixa: a música abaixa sob a voz e o áudio é normalizado para -14 LUFS. |

As cenas e as legendas palavra por palavra seguem os tempos reais da voz. Se você mudar o texto em `roteiro.json` e rodar `./build.sh`, tudo se ressincroniza.

## Roteiro (≈45 s)

| Cena | Narração | Visual |
|---|---|---|
| Gancho | Sua startup gastou três semanas num edital… pra descobrir que nem podia participar? | Páginas de edital caindo, contador "DIA 01 → 21" e o carimbo **INELEGÍVEL** |
| Dor | Oitenta páginas, anexos, retificação… e o prazo acabando. | PDF rolando, contadores e prazo piscando em vermelho |
| Revelação | Esse é o FomentoRadar. | Varredura de radar e a marca |
| Perfil | Você cadastra o perfil da empresa uma vez. | Celular: formulário se preenchendo sozinho |
| Chamadas | O radar encontra as chamadas compatíveis, com prazo. | Mini radar e três chamadas com prazo e requisitos atendidos |
| Requisitos | E cada requisito vem classificado: atendido, não atendido ou desconhecido, sempre com o trecho e a página do edital. | Selos sincronizados com a fala; zoom na citação (p. 12, item 4.2) |
| Confiança | Sem evidência, ele não chuta: diz desconhecido. | "SIM?" riscado e o selo **DESCONHECIDO** |
| Próximos passos | No fim, você vê o que falta, recebe o checklist e é avisado se o edital mudar. | Lacunas, checklist e notificação de retificação |
| CTA | Triagem de edital em minutos, não em semanas. Startup ou aceleradora? Entra no nosso piloto. | "Piloto aberto", botão "Comente PILOTO" e aviso de protótipo |

## Como gerar

Pré-requisitos: Python 3 com `numpy`, Node 22 com `playwright` (Chromium) e `ffmpeg`.

```bash
cd reels
./build.sh             # com narração, se api.elevenlabs.io estiver acessível com a chave
./build.sh --estimate  # versão sem voz, para revisar ritmo e visual
```

A chave da ElevenLabs **não** fica no código. Neste ambiente de nuvem, ela é cadastrada como *network secret* do ambiente (host `api.elevenlabs.io`, header `xi-api-key`) e o proxy a injeta nas requisições. Fora dele, exporte `ELEVEN_API_KEY`. Para escolher outra voz, use `ELEVEN_VOICE_ID`.

Saída: `out/fomentoradar_reels.mp4` (com voz) ou `out/fomentoradar_reels_sem_voz.mp4`.
