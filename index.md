## Was ist piScreen?
Das Projekt um aus einem einfachen TV und einem Raspberry Pi eine große Anzeigetafel zu machen.
Verwende piScreen um Werbeanzeigen in Schaufenstern zu zeigen, Informationen für Mitarbeiter "auszuhängen" oder einen digitalen Stundenplan an Schulen zu verwirklichen.
Zu steuern ist das Ganze per Passwort geschützter Weboberfläche. Kleiner Einblick gefällig? v3.0.0 sieht aktuell wie folgt aus:
![piScreen](https://raw.githubusercontent.com/Jet0JLH/piScreen/gh-pages/img/piScreen_pageAdmin_v3.0.0.JPG)

## Was wird für das Projekt benötigt?
- Aktuell ist das Projekt sehr für Raspberrys mit einem Raspberry OS optimiert. Dies sollte daher momentan als Voraussetzung für das System selber gelten.
- Ebenso sollte ein HDMI-CEC fähiger TV oder ein DDC/CI fähiges Display eingesetzt werden. Das Projekt selber läuft auch ohne CEC und DDC/CI, aber dadurch sind Funktionen, die das Steuern des Displays anbelangt, nicht verfügbar. (Das Ansteuern von weitere Standards wird ggf. noch nachgereicht)
- Eine Website die den gewünschten darzustellenden Inhalt bereitstellt und ggf. selber scrollt oder sich aktualisiert. piScreen selber kann aktuell nicht scrollen. Diese Funktionen könnten aber noch in Zukunft entwickelt werden.

## Wohin geht der Weg des Projektes noch?
Hierzu ist es immer gut einen Blick auf die aktuelle [Roadmap](https://github.com/Jet0JLH/piScreen/wiki/Roadmap) zu werfen. Hier werden die Ideen und Pläne für das Projekt gesammelt.

## Wer steckt hinter dem Projekt?
piScreen ist ein kleines Bastelprojekt von zwei befreundeten Hobbyentwicklern. Dementsprechend ist der Code weit entfernt von perfekt und wird aktuell nicht ständig weiterentwickelt. Wir haben aber vor immer wieder Funktionen nachzureichen und das Projekt somit am Laufen zu halten.

## Wie wird piScreen installiert?
1. Setze einen Raspberry Pi mit Raspberry OS (**Desktop Variante**, am besten 64 Bit) auf.
2. Die install.zip aus dem aktuellsten [Release](https://github.com/Jet0JLH/piScreen/releases) herunterladen.
3. Die install.zip nun auspacken und die darin befindliche install.py ausführen und der Installation folgen.
