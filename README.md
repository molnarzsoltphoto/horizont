# Horizont — személyes hírszemle

Statikus, mobilbarát híroldal GitHub Pages-re. Nyolc téma: MÁV, magyar közlekedés, nemzetközi vasút, jégkorong, csillagászat, belpolitika, külpolitika és gazdaság.

## Telepítés

1. Hozz létre egy **nyilvános** GitHub repositoryt (például `horizont-hirek`), majd töltsd fel **a ZIP tartalmát** a repository gyökerébe. Fontos: a rejtett `.github` mappa is kerüljön fel. A GitHub webes feltöltőjén a `.github/workflows/update-news.yml` fájl feltöltését külön ellenőrizd; ha a mappafeltöltés nem működik, ezt a fájlt a GitHub `Add file → Create new file` menüjével is létrehozhatod, a fenti útvonalat megadva.
2. A repositoryban `Settings → Actions → General → Workflow permissions` alatt állítsd be a **Read and write permissions** értéket, és mentsd el. A workflowban is szerepel `contents: write`; a repository beállításának is engednie kell az írást.
3. Az `Actions` lapon válaszd a **Hírek frissítése** folyamatot, és kattints a **Run workflow** gombra. Ellenőrizd, hogy a `data/news.json` feltöltődött hírekkel.
4. `Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: main → / (root) → Save`. Ha a default branch neve más, azt válaszd. A megjelenő Pages URL-en elérhető az oldal.
5. A hírek ezután elvileg óránként frissülnek (az ütemezés UTC szerinti 17. percben indul, nem garantáltan pontos). Frissíthetsz kézzel is az Actions felületen.

## Szerkesztés

A témák keresőkifejezéseit a `scripts/fetch_news.py` fájl `QUERIES` részében módosíthatod. Az oldalon látható kategórianeveket az `app.js` `topics` listája tartalmazza. Egy új téma felvételéhez mindkét helyen módosítani kell, és érdemes hozzá színkódot is beállítani a CSS-ben.

## Tudnivalók

- A gyűjtő jelenleg Google Hírek keresési RSS-csatornákból dolgozik. A külső szolgáltató elérhetősége, a találatok minősége és a képek megléte változó. Első feltöltésig üres állapot látszik; a csomag nem tartalmaz kitalált híreket.
- Csak ha az RSS elem ténylegesen tartalmaz HTTPS-es kép-URL-t, jelenik meg külső kép; máskülönben saját grafikus helyettesítő látszik. Egyes külső képek forrólinkelése nem engedélyezett, azoknál a helyettesítő grafika marad. A kód nem másol képeket a repositoryba.
- A rövid leírás az RSS leírása, **nem mesterséges intelligenciával írt, ellenőrzött összefoglaló**. A cikkek az eredeti oldalra mutatnak, és a tartalmukat nem másolják át.
- A hírek legfeljebb 7 napig maradnak, maximum 250 elem tárolódik; az azonos URL-eket a gyűjtő kiszűri. Egyes témák keresési találatai átfedhetnek. A találatok nem szerkesztőségi válogatások.
- Nyilvános GitHub Pages esetén az oldal és a `data/news.json` is nyilvános. Titkos adatot, személyes RSS-linket vagy API-kulcsot ne tölts fel.
- Inaktív nyilvános repositoryban a GitHub idővel letilthatja az ütemezett Actions-futtatást; ha nem frissül az oldal, nézd meg az Actions lapot.
- A kereső böngészőben, a már begyűjtött hírek között működik. Nem keres új cikkeket az interneten.
