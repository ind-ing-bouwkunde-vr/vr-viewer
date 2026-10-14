# Privacyverklaring – VR-viewer starter

*Laatst bijgewerkt: oktober 2026*

VR-viewer starter is een gratis hulpmiddel, ontwikkeld in het kader van de masterproef *VR als leerhulpmiddel in bouwkundig onderwijs* (UGent). Met de app kun je VR-pagina's van bouwkundige constructies bekijken op een Meta Quest.

## Welke gegevens verzamelt de app?

Geen. De app verzamelt, verstuurt of verkoopt geen persoonsgegevens en bevat geen advertenties of statistieken.

## Wat bewaart de app op je computer?

Enkel op je eigen computer, in je gebruikersmap (`AppData\Local\VRViewerStarter`):

- de map met VR-modellen die je koos en je instellingen (bv. welk soort link je gebruikt);
- het programma cloudflared (als je de snellink gebruikt);
- de plaats van ngrok.exe en je ngrok-authtoken (enkel als je ngrok gebruikt).

Deze gegevens verlaten je computer niet, behalve het authtoken dat ngrok gebruikt om met je eigen ngrok-account te verbinden. Als je de app verwijdert, worden ze ook verwijderd.

## Diensten van derden

Om je VR-pagina via een beveiligde https-link op de Quest te tonen, gebruikt de app een tunneldienst. Zolang je op **Start** hebt geklikt, zijn de bestanden in je gekozen map bereikbaar via die link. Klik op **Stop** of sluit de app om de link te stoppen.

- **Cloudflare (snellink, standaard).** De app gebruikt het gratis programma cloudflared van Cloudflare Inc. Er is geen account nodig. Het verkeer via de snellink valt onder de privacyverklaring van Cloudflare: <https://www.cloudflare.com/privacypolicy/>.
- **ngrok (vaste link, optioneel).** Kies je in de app voor een vaste link, dan gebruik je ngrok van ngrok Inc., met een eigen gratis account. Dat verkeer valt onder de privacyverklaring van ngrok: <https://ngrok.com/privacy>.

## Controle op nieuwe versies

De versie die je via GitHub downloadt, vraagt bij het opstarten aan GitHub wat het nieuwste versienummer van de app is. Daarbij wordt enkel het versienummer van je app meegestuurd, geen persoonsgegevens. De Microsoft Store-versie doet dit niet; die wordt door de Store zelf bijgewerkt.

## Contact

Vragen? Maak een melding (issue) aan op de GitHub-pagina van dit project.
