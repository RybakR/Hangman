# R. Rybak & A. Karwoski - Gra "Wisielec"

## Instrukcja obsługi:

###### Aby odbyć grę, należy:
- odpalić serwer: **py Serwer.py**
- odpalić pierwszego klienta **A**: **py Klient.py ip_serwera** *np. py Klient.py localhost*
- wybrać opcję stwórz nowy pokój: **input**: *“2”*
- podać nazwę pokoju: **input**: *np.  “nazwa”*
- podać hasło pokoju: **input**: *np. “haslo”*
- odpalić drugiego klienta **B**: **py Klient.py ip_serwera** *np. py Klient.py localhost*
- wybrać opcję dołącz do istniejącego pokoju: **input**: *“1”*
- wybrać pokój z listy: **input**: *np. “1”*
- podać hasło pokoju: **input**: *np. “haslo”*
- po stronie klienta **A** podać hasło gry do odgadnięcia: **input**: *np. “password”*
- po stronie klienta **B** podawać literę do odgadniecia” **input**: *np “a”*
- po wygranej / przegranej po stronie klienta **A** oraz **B** podać informację, czy chce się kontynuować grę: **input** *“Y”/”N”*.
- gdy klient **A** oraz klient **B** wprowadzi *“Y”* powtarzają się kroki od **9-12** z zamianą stron: klient **B** podaje hasło do odgadnięcia, klient **A** zgaduje litery. 
- Gdy jeden z graczy wprowadzi *“N”*  zarówno klient **A**, jak i klient **B** zostanie skierowany do menu wyboru opcji punkty **3, 7.**

 
## Mechanizm gry:
###### Początkowa komunikacja / tworzenie pokoju / dołączanie do istniejącego pokoju
- Klient wysyła *„Hello”.*
- Serwer zwraca *„Hello”* oraz *ID*.
- Klient wysyła informacje czy chce: stworzyć pokój, dołączyć do istniejącego lub wyjść z gry.

###### W wypadku stworzenia nowego pokoju:
- Gracz podaje nazwę pokoju oraz hasło.
- Serwer sprawdza czy taki pokój już istnieje:

a) Jeżeli istnieje to wysyła komunikat o braku możliwości stworzenia ze względu na konflikt.

b) Jeżeli nie istnieje serwer tworzy taki pokój i podaje komunikat o jego stworzeniu.

- Gracz tworzący pokój oczekuje na dołączenie się innego gracza.

Po dołączeniu drugiego gracza, założyciel pokoju dostaje informacje kto dołączył i rozpoczyna się gra.

###### W wypadku dołączenia do istniejącego pokoju:
- Gracz otrzymuje od serwera listę istniejących pokojów
- Gracz wybiera pokój do którego chce się dołączyć, następnie podaje do niego hasło
- Serwer sprawdza poprawność podanego hasła, w zależności od wyników weryfikacji zwraca komunikat oraz 
 dodaje / odrzuca klienta.

Po poprawnym dołączeniu się gracza, gra rozpoczyna się


###### Przebieg gry
- Gracz podaje klucz gry, który jest przechowywany przez serwer
- Serwer koduje klucz do postaci ciągu „_” oznaczającego nieodgadnione litery oraz podaje graczowi odgadującemu informacje, że może rozpocząć rozgrywkę
###### Powtarzane dopóki gracz wygra lub przegra:
 - Gracz zgadujący podaje literę
- Serwer sprawdza literę (czy jest jedna, czy już się pojawiła)
- Jeżeli gracz nie trafił litery traci życie oraz otrzymuje informację o liczbie żyć
- Jeżeli gracz trafił „_” na miejscu trafionej litery odrywa się, gracz otrzymuje informacje o   aktualnym stanie klucza gry oraz pozostałej liczbie żyć
- Gracz podający hasło gry otrzymuje informacje o ruchu gracza zgadującego
- Jeżeli liczba żyć spadnie do 0 gracz zgadujący otrzymuje komunikat o przegranej, odkryty klucz gry oraz zapytanie, czy chce kontynuować grę
- Gracz podający klucz gry otrzymuje komunikat o wygranej, literach które gracz zgadujący odgadł oraz informacje, czy chce kontynuować grę.
- Jeżeli wszystkie litery zostały odgadnięte prawidłowo, gracz zgadujący otrzymuje komunikat o wygranej oraz zapytanie czy chce kontynuować grę.
- Gracz podający klucz gry otrzymuje komunikat o przegranej, liczbie żyć które pozostały graczowi zgadującemu oraz zapytanie, czy chce kontynuować grę.
###### Po zakończonej rozgrywce:
- Jeżeli obaj gracze wyrażą chęć kontynuacji gry, gra rozpoczyna się na nowo z zamianą graczy: gracz zgadujący podaje hasło gry, gracz podający hasło gry teraz zgaduje.
- Jeżeli któryś z graczy nie chce kontynuować gry, gracze otrzymują o tym komunikat oraz pokój zostaje zamknięty.
 
# Protokół:
## Zasada działania:
Klient wysyła komunikat na zasadzie: `"WISIELEC\r\nWIADOMOSC\r\n\r\n"`

Serwer po rozpoznaniu komunikatu wysyła dane / kod błędu w zależności od jego weryfikacji.

## Wiadomości:
 
###### Początkowa komunikacja
*Request:*

`'WISIELEC\r\nHELLO\r\n\r\n'`

*Response:*

a)      `'WISIELEC\r\nHELLO\r\n SESSIONID: ' + usr_id + '\r\n\r\n'`

b)     `'WISIELEC\r\n400 Bad request\r\n\r\n'`
 
## GRA PODAJĄCEGO KLUCZ GRY:

###### Ustawianie klucza gry:

*Request:*

`'WISIELEC\r\nSESSIONID: ' + myID + '\r\nSETGAMEKEY\r\nGAMEKEY: ' + game_key + '\r\n\r\n'`

*Response:*

 `'WISIELEC\r\n200 OK\r\nGAMEKEY: ' + str(game.game_key_) + '\r\n\r\n'`
 
###### Komunikowanie ruchów zgadującego:

*Message:*

a)      Rozpoczęcie gry:

`'WISIELEC\r\n201 OK\r\nGAMEKEY: ' + str(game.game_key_) + '\r\nLETTER: ' + str(letter) + '\r\nLIFES: ' + str(game.lives) +'\r\n\r\n'`

b)     Przegrana:

`'WISIELEC\r\nGAMEOVER\r\nLIFES: ' + str(game.lives) + '\r\n\r\n'`

c)      Wygrana:

`'WISIELEC\r\nWIN\r\nGAMEKEY: ' + str(game.game_key_) + '\r\n\r\n'`

d)     Kontynuacja gry:

`'WISIELEC\r\nNEXTGAME' + '\r\n\r\n'`
 
## GRA ZGADUJĄCEGO:

###### Rozpoczynanie gry dla zgadującego:

*Response*:

`'WISIELEC\r\n200 OK\r\nSESSIONID: ' + game.id_game_master + '\r\nPLAY\r\nLIFES: ' + str(game.lives) + '\r\nGAMEKEY: ' + str(game.game_key_) + '\r\n\r\n'`
 
###### Zgadywanie litery:
*Request:*

`'WISIELEC\r\nSESSIONID: ' + myID + '\r\nPLAY\r\nLETTER: ' + letter.lower() + '\r\n\r\n'`

*Response:*

a)      Błędna litera:

`'WISIELEC\r\n400 Bad Request\r\n\r\n'`

b)     Nierozpoczęta gra:

`'WISIELEC\r\n409 NOT ON\r\n\r\n'`

c)      Nietrafiona litera:

`'WISIELEC\r\nSESSIONID: ' + usr_id + '\r\nPLAY\r\nLIFES: ' + str(game.lives) + '\r\nGAMEKEY: ' + str(game.game_key_) +  '\r\n\r\n'`

d)     Trafiona litera:

`'WISIELEC\r\nSESSIONID: ' + usr_id + '\r\nPLAY\r\nLIFES: ' + str(game.lives) + '\r\nGAMEKEY: ' + str(game.game_key_) + '\r\n\r\n'`

e)     Przegrana:

`'WISIELEC\r\nSESSIONID: ' + usr_id + '\r\nLOSE\r\nGAMEKEY: ' + str(game.game_key_) + '\r\nGAMEKEYTRUE: ' + str(game.game_key) +'\r\n\r\n'`

f)       Wygrana:

`'WISIELEC\r\nSESSIONID: ' + usr_id + '\r\nWIN\r\nLIFES: ' + str(game.lives) + '\r\nGAMEKEY: ' + str(game.game_key) + '\r\n\r\n'`
 
## Kontynuacja gry:
###### Zapytanie o kontynuacje gry:

*Request:*

 `'WISIELEC\r\nSESSIONID: ' + myID + '\r\nWANTNEXT\r\nVALUE: ' + nextgame + '\r\n\r\n'`
*Response:*

a)  `'WISIELEC\r\n401 Not Authoritated\r\n\r\n'`

b)  `'WISIELEC\r\n400 Bad Request\r\n\r\n'`

c)  `'WISIELEC\r\nSTARTGAME\r\n\r\n'`

d)  `'WISIELEC\r\nEND GAME\r\n\r\n'`

## Pokój gry:
###### Wyświetlanie listy pokojów po wyborze dołączenia do istniejącego pokoju:

*Request:*

 `'WISIELEC\r\nSESSIONID: ' + myID +'\r\nROOMLIST\r\n\r\n'`
 
*Response:*

 `'WISIELEC\r\nLISTOFROOMS: ' + list_of_rooms + '\r\n\r\n'`
 
###### Oczekiwanie na dołączenie się innego gracza:

*Response:*

`'WISIELEC\r\n223 NEWPLAYER\r\nSESSIONID: ' + usr_id + '\r\n\r\n'`
 
###### Dołączanie się do istniejącego pokoju:

*Request:*

`'WISIELEC\r\nSESSIONID: ' + myID + '\r\nJOIN\r\nNAME: ' + room_list[room_choice] +'\r\nPASSWORD: ' + room_password + "\r\n\r\n"`

*Response:*

a)      Pokój jest pełny:

`'WISIELEC\r\n408 Room is full\r\n\r\n'`

b)     Błędne hasło:

`'WISIELEC\r\n401 UNAUTHORIZED\r\n\r\n'`

c)      Błąd:

`'WISIELEC\r\n400 Bad Request\r\n\r\n'`

d)     Rozpoczęcie gry:

Client: `'WISIELEC\r\n200 OK\r\n\r\n'`

Host: `'WISIELEC\r\n223 NEWPLAYER\r\nSESSIONID: ' + usr_id + '\r\n\r\n'`
 
###### Tworzenie pokoju:

*Request:*

`'WISIELEC\r\nSESSIONID: ' + myID +'\r\nCREATE\r\nNAME: '+ room_name +'\r\nPASSWORD: ' + room_password + "\r\n\r\n"`

*Response:*

a)      Błąd nazwy / hasła:

`'WISIELEC\r\n400 Bad request\r\n\r\n'`

b)     Konflikt nazwy:

`'WISIELEC\r\n409 Conflict\r\n\r\n'`

c)      Stworzony pokój:

`'WISIELEC\r\n200 OK\r\n\r\n'`
 
 

