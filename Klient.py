#klient
import socket
import ssl
import sys

myID = ''
server_ip = sys.argv[1]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4
#s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0) #IPv6

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile='client.crt', keyfile='client.key', password='andrzejkarwoski')
context.load_verify_locations(cafile='server.crt')
ss = context.wrap_socket(s, server_hostname=server_ip)

def receive_message(s, size):
    data = b''

    while b'\r\n\r\n' not in data:
        data = s.recv(size)

    return data.decode('utf-8')

def start_communication(s):
    s.send('WISIELEC\r\nHELLO\r\n\r\n'.encode('utf-8'))
    response = receive_message(s, 1024)

    global myID
    myID = response.split('SESSIONID: ')[1]
    myID = myID.replace("\r\n\r\n", "")

def ask_for_room_list(s):
    roomlist = []

    s.send(('WISIELEC\r\nSESSIONID: ' + myID +'\r\nROOMLIST\r\n\r\n').encode('utf-8'))
    response = receive_message(s, 1024)
    roomlist = response.split('LISTOFROOMS: ')[1].split(',')[:-1]
    return roomlist

def if_next_game(s):
    nextgame = ''

    while True:
        nextgame = input("Czy chcesz kontynuowac gre? (Y/N): ")

        if nextgame == 'Y' or nextgame == 'N':
           break
        else:
            print("Podales zla odpowiedz, podaj jeszcze raz")

    s.send(('WISIELEC\r\nSESSIONID: ' + myID + '\r\nWANTNEXT\r\nVALUE: ' + nextgame + '\r\n\r\n').encode('utf-8'))
    waiting_for_game_start(s)


def master_game(s):
    game_key = input("Podaj haslo gry do odgadniecia: ")
    s.send(('WISIELEC\r\nSESSIONID: ' + myID + '\r\nSETGAMEKEY\r\nGAMEKEY: ' + game_key + '\r\n\r\n').encode('utf-8'))

    game_state = ''
    while True:
        response = receive_message(s, 1024)
        if '200 OK' in response:
            game_state = response.split("GAMEKEY: ")[1].split('\r\n\r\n')[0]
            print("Aktualny stan gry: ", game_state)

        elif '201 OK' in response:
            game_state = response.split("GAMEKEY: ")[1].split('\r\n')[0]
            lifes = response.split("LIFES: ")[1].split('\r\n\r\n')[0]
            letter = response.split("LETTER: ")[1].split('\r\n')[0]
            print("Zgadujacy podal litere: ", letter)
            print("Pozostale zycia zgadujacego: ", lifes)
            print("Aktualny stan gry: ", game_state)

        elif 'GAMEOVER' in response:
            lifes = response.split("LIFES: ")[1].split('\r\n')[0]
            print("Przeciwnik odgadl haslo przy: " + str(lifes) + " zyciach, przegrales.")
            if_next_game(s)
            return

        elif 'WIN' in response:
            game_state = response.split("GAMEKEY: ")[1].split('\r\n')[0]
            print("Przeciwnik nie odgadl hasla, wygrales.")
            print("Udalo mu sie odslonic haslo do etapu: " + str(game_state))
            if_next_game(s)
            return

def guesser_game(s):
    print("Oczekiwanie na haslo do odgadniecia...")

    while True:
        response = receive_message(s, 1024)
        if 'PLAY' in response:
            lifes = response.split('LIFES: ')[1].split('\r\n')[0]
            print("Pozostala liczba zyc: ", lifes)
            game_state = response.split('GAMEKEY: ')[1].split('\r\n')[0]
            print("Haslo do odgadniecia: ", game_state)
            while True:
                letter = input("Podaj litere do odgadniecia: ")

                if len(letter) == 1 and letter.isalpha():
                    break

                print("Podano bledna litere, podaj jeszcze raz.")

            s.send(('WISIELEC\r\nSESSIONID: ' + myID + '\r\nPLAY\r\nLETTER: ' + letter.lower() + '\r\n\r\n').encode('utf-8'))

        if 'WIN' in response:
            print("WYGRANKO")
            lifes = response.split('LIFES: ')[1].split('\r\n')[0]
            game_key = response.split('GAMEKEY: ')[1].split('\r\n')[0]
            print("Haslo to: " + str(game_key))
            print("Pozostalo Ci: " + str(lifes) + " zyc. Gratulacje.")
            if_next_game(s)
            return

        if 'LOSE' in response:
            print("PREGRANKO")
            unmask_key = response.split('GAMEKEYTRUE: ')[1].split('\r\n\r\n')[0]
            mask_key = response.split('GAMEKEY: ')[1].split('\r\n')[0]
            print("Haslem bylo: " + str(unmask_key) + ", udalo Ci sie odgadnac: " + str(mask_key))
            if_next_game(s)
            return

def waiting_for_game_start(s):
    response = receive_message(s, 1024)
    if "STARTGAME" in response:
        print("Rozpoczynanie gry")
        response = receive_message(s, 1024)
        recivedID = response.split('SESSIONID: ')[1].split('\r\n')[0]

        if recivedID == myID:
            print("Podajesz haslo.")
            master_game(s)
        else:
            print("Odgadujesz haslo.")
            guesser_game(s)
    elif "END GAME" in response:
        print("Jeden z graczy nie wyrazil checi kontynuacji gry, pokoj zostaje usuniety.")
        ask_room(s)

def waiting_for_another_player(s):
    print("Oczekiwanie na dolaczenie innego gracza")
    response = receive_message(s, 1024)
    if "223 NEWPLAYER" in response:
        otherID = response.split('SESSIONID: ')[1].split('\r\n')[0]

        print("Dolaczyl gracz: " + otherID)
        waiting_for_game_start(s)

def ask_room(s):
    room_name = ''
    room_password = ''
    choice = ''

    while True:
        print("czy chcesz dolaczyc do pokoju (wpisz 1) czy stworzyc nowy (wpisz 2), by wyjść z gry(wpisz 0):")
        choice = input()
        if choice == "0":
            ss.send(('WISIELEC\r\nSESSIONID: ' + myID + '\r\nCLOSED\r\n\r\n').encode('utf-8'));
            quit()
        elif choice == "1":
            room_list = ask_for_room_list(s)
            print("Wybierz pokoj z listy (wypisz 0 aby wrocic do wyboru opcji)")

            i = 1
            for x in room_list:
                print(str(i) + ') ' + x)
                i += 1

            room_choice = input("Wybierz numer pokoju: ")

            try:
                val = int(room_choice)
            except ValueError:
                try:
                    val = float(room_choice)
                    print("Nie ma takiego pokoju")
                    continue
                except ValueError:
                    print("Nie ma takiego pokoju")
                    continue
            if int(room_choice) > len(room_list) or int(room_choice) < 0:
                print("Nie ma takiego pokoju")
                continue
            elif int(room_choice) == 0:
                continue

            room_choice = int(room_choice) - 1
            if int(room_choice) == -1:
                continue

            room_password = input("Podaj haslo do pokoju: ")
            s.send(('WISIELEC\r\nSESSIONID: ' + myID + '\r\nJOIN\r\nNAME: ' + room_list[room_choice] +'\r\nPASSWORD: ' + room_password + "\r\n\r\n").encode('utf-8'))
            response = receive_message(s, 1024)

            if '401 UNAUTHORIZED' in response:
                print("Zle haslo auau")
                continue
            elif '408 Room is full' in response:
                print("Wybrany pokój jest pełny, wybierz inny")
                continue
            elif '200 OK' in response:
                print("Dolaczono do pokoju")
                waiting_for_game_start(s)
                break

        elif choice == "2":
            while True:
                print("Podaj nazwe pokoju:")
                room_name = input()
                if room_name != '':
                    break

            while True:
                print("Podaj haslo do pokoju:")
                room_password = input()
                if room_password != '':
                    break

            s.send(('WISIELEC\r\nSESSIONID: ' + myID +'\r\nCREATE\r\nNAME: '+ room_name +'\r\nPASSWORD: ' + room_password + "\r\n\r\n").encode('utf-8'))
            response = receive_message(s,1024)

            if '409 Conflict' in response:
                print("Taki pokoj juz istnieje, sproboj ponowonie")
                continue
            elif '200 OK' in response:
                print("Utworzono pokoj")
                waiting_for_another_player(s)
                break

def main():
    try:
        ss.connect((server_ip, 1773)) #FOR IPv4
        #ss.connect((server_ip, 1773, 0, 0)) #FOR IPv6
        start_communication(ss)
        ask_room(ss)

    except socket.error:
        print(socket.error.with_traceback())
    except KeyboardInterrupt:
        ss.send(('WISIELEC\r\nSESSIONID: ' + myID + '\r\nCLOSED\r\n\r\n').encode('utf-8'));
        print('Client closed')

main()