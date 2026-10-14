# VR-viewer starter

Bekijk je bouwkundige constructie in VR op de Meta Quest, zonder terminal, commando's of account.

Kies je map met VR-modellen (HTML-pagina's), klik op **Start**, en scan de QR-code met je Quest.

## Downloaden

Ga naar **Releases** (rechts op deze pagina) en download `VR-viewer-starter-setup.exe`.

Windows toont bij de eerste keer misschien *"Windows heeft uw pc beveiligd"*. Klik dan op **Meer informatie → Toch uitvoeren**. Dat komt doordat de app niet digitaal ondertekend is. De Microsoft Store-versie heeft dat niet.

## Wat heb je nodig?

- Een Windows-computer
- Een Meta Quest 2, 3, 3S of Pro (met een QR-scanner-app, of je typt de link)
- Geen account: de app maakt een gratis Cloudflare-snellink

## Gebruik

1. Kies je hoofdmap met VR-modellen (bv. `C:\VR-modellen`). Modellen mogen elk in een eigen submap staan.
2. Klik op **Start**. De eerste keer downloadt de app eenmalig `cloudflared` (±55 MB).
3. Scan de QR-code met je Quest of typ de link, kies een model en druk op **Start VR**.

Een vaste link (voor een afgedrukte QR-code of bladwijzer) kan ook: kies in stap 2 **Vaste link via ngrok** (gratis ngrok-account nodig).

Om te testen klik je op **Voorbeeld proberen**.

Is er een nieuwe versie, dan meldt de app dat zelf.

---

Ontwikkeld in het kader van de masterproef *VR als leerhulpmiddel in bouwkundig onderwijs*.
