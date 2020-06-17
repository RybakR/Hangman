#Serwer
import socket
from _thread import *
import uuid
import ssl
import logging
logger = logging.getLogger("SERWER")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


#table for users
users_table = []
#table for rooms
room_table = []
#table for games
game_table = []


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
s.bind(("localhost", 1773))
s.listen(5)

def mask_key(key):
    masked_key = ''

    for x in key:
        if x == ' ':
            #saving spaces in case of they appear in key word
            masked_key = masked_key + '  '
        else:
            #adding spaces after every '_' for clarity
            masked_key = masked_key + '_ '

    return masked_key

def unmask_key(key, masked_key, letter):
    count = 0
    masked_key = list(masked_key)
    correct_letter = False
    for x in key:
        if x == letter:
            # flag for checking if right letter was guessed
            correct_letter = True
            # revealing true letter in masked key
            masked_key[count] = letter

        count = count + 1

    masked_key = ''.join(masked_key)
    result = (masked_key, correct_letter)
    return result

class Game:
    game_key = ''
    game_key_ = '' #masked game key word
    id_guesser = ''
    id_game_master = ''
    game_over = False
    lives = 0

    def __init__(self, id_guesser, id_game_master):
        self.id_guesser = id_guesser
        self.id_game_master = id_game_master
        self.lives = 10
        self.game_over = True

    #setting key for game
    def set_key(self, game_key):
        key = ''
        for x in game_key:
            key = key + x + ' '

        self.game_key = key
        self.game_key_ = mask_key(game_key)
        self.game_over = False

    #checking for guessed letter
    def check_letter(self, letter):
        if self.game_over:
            return "GAME IS NOT ON"

        #result[0] is key with revealed letters, result[1] is flag if letter was guessed
        result = unmask_key(self.game_key, self.game_key_, letter)
        self.game_key_ = result[0]

        #deleting spaces from keys for proper comparision
        key_ = self.game_key_.replace(' ', '')
        key = self.game_key.replace(' ', '')

        if not result[1]:
            #unguessed letter -> guesser loses his life
            self.lives = self.lives - 1

            if self.lives == 0:
                self.game_over = True
                return 'GAMEOVER: LOSE'
            else:
                return 'MISS'
        else:
            if key == key_:
                self.game_over = True
                return 'GAMEOVER: WIN'
            else:
                return 'NEXTLETTER'

class Room:
     host = ''
     other_player = ''
     room_name = ''
     room_password = ''
     game_is_not_on = False #information if there is game going in the room
     continue_game = ('','') #information if players ([0],[1]) want to continue game

     def __init__(self, host, room_name, room_password):
         self.host = host
         self.room_name = room_name
         self.room_password = room_password

     def player_joined(self, other_player):
         self.other_player = other_player

#getting user socket: users_table => (socket, id)
def get_connection(usr_id):
    for x in users_table:
        if x[1] == usr_id:
            return x[0]
    return None

def get_usrID_by_client(client):
    for x in users_table:
        if x[0] == client:
            return x[1]
    return None

def get_message(client, size):
    data = b''

    while b'\r\n\r\n' not in data:
        data = client.recv(size)

    return data.decode('utf-8')

def start_communication(client):
    #getting user ID
    usr_id = str(uuid.uuid4())

    users_table.append((client, usr_id))
    message = get_message(client, 1024)
    message = str(message)
    logging.info('Client ' + str(client) + ' ' + repr(message));

    if message == 'WISIELEC\r\nHELLO\r\n\r\n':
        response =  'WISIELEC\r\nHELLO\r\n SESSIONID: ' + usr_id + '\r\n\r\n'
        logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
        client.send(response.encode('utf-8'))
    else:
        response = 'WISIELEC\r\n400 Bad request\r\n\r\n'
        logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
        client.send(response.encode('utf-8'))

    return usr_id

def create_room(client, message, host):
    room_name = message.split('NAME: ')[1].split('\r\n')[0]
    if room_name == '':
        response = 'WISIELEC\r\n400 Bad request\r\n\r\n'
        logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
        client.send(response.encode('utf-8'))
        return
    room_password = message.split('PASSWORD: ')[1].split('\r\n\r\n')[0]
    if room_password == '':
        response = 'WISIELEC\r\n400 Bad request\r\n\r\n'
        logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
        client.send(response.encode('utf-8'))
        return
    room = Room(host, room_name, room_password)
    for x in room_table:
        if x.room_name == room_name:
            response = 'WISIELEC\r\n409 Conflict\r\n\r\n'
            logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
            client.send(response.encode('utf-8'))
            return

    room_table.append(room)
    response = 'WISIELEC\r\n200 OK\r\n\r\n'
    logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
    client.send(response.encode('utf-8'))

def send_room_list(client):
    list_of_rooms = ''
    for x in room_table:
        if x.other_player == '':
            list_of_rooms = list_of_rooms + x.room_name + ","

    response = ('WISIELEC\r\nLISTOFROOMS: ' + list_of_rooms + '\r\n\r\n')
    logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
    client.send(response.encode('utf-8'))

def start_game_thread(client, host_id):
    response = 'WISIELEC\r\nSTARTGAME\r\n\r\n'
    logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
    client.send(response.encode('utf-8'))
    response = 'WISIELEC\r\n200 OK\r\nSESSIONID: ' + host_id + '\r\n\r\n'
    logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
    client.send(response.encode('utf-8'))

def start_game(client, host, usr_id, host_id):
    response = 'WISIELEC\r\n200 OK\r\n\r\n'
    logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
    client.send(response.encode('utf-8'))
    response = 'WISIELEC\r\n223 NEWPLAYER\r\nSESSIONID: ' + usr_id + '\r\n\r\n'
    logger.info('Sending message to Client: ' + str(host) + ' ' + 'Message: ' + repr(response));
    host.send(response.encode('utf-8'))

    game = Game(usr_id, host_id)
    game_table.append(game)

    start_new_thread(start_game_thread, (host, host_id,))
    start_new_thread(start_game_thread, (client, host_id,))

def find_room(usrID):
    for x in room_table:
        if x.other_player == usrID or x.host == usrID:
            return x
    return None

def join_room(client, message, usr_id):
    room_name = message.split('NAME: ')[1].split('\r\n')[0]
    room_password = message.split('PASSWORD: ')[1].split('\r\n\r\n')[0]
    for x in room_table:
        if x.room_name == room_name:
            if x.room_password == room_password and x.other_player == '':
                x.player_joined(usr_id)
                host = get_connection(x.host)
                start_game(client, host, usr_id, x.host)
                return
            elif x.room_password == room_password and x.other_player != '':
                response = 'WISIELEC\r\n408 Room is full\r\n\r\n'
                logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
                client.send(response.encode('utf-8'))
                return
            else:
                response = 'WISIELEC\r\n401 UNAUTHORIZED\r\n\r\n'
                logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
                client.send(response.encode('utf-8'))
                return
    response = 'WISIELEC\r\n400 Bad Request\r\n\r\n'
    logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
    client.send(response.encode('utf-8'))
    return

def start_game_for_guesser(game):
    guesser = get_connection(game.id_guesser)
    response = 'WISIELEC\r\n200 OK\r\nSESSIONID: ' + game.id_game_master + '\r\nPLAY\r\nLIFES: ' + str(game.lives) + '\r\nGAMEKEY: ' + str(game.game_key_) + '\r\n\r\n'
    logger.info('Sending message to Client: ' + str(guesser) + ' ' + 'Message: ' + repr(response));
    guesser.send(response.encode('utf-8'))

def find_game(usrID):
    for game in game_table:
        if game.id_guesser == usrID or game.id_game_master == usrID:
            return game

def set_key_in_game(client, wiadomosc, usrID):
    game = find_game(usrID)
    game.set_key(wiadomosc.split('GAMEKEY: ')[1].split('\r\n\r\n')[0])
    room = find_room(usrID)
    room.game_is_not_on = True
    response = 'WISIELEC\r\n200 OK\r\nGAMEKEY: ' + str(game.game_key_) + '\r\n\r\n'
    logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
    client.send(response.encode('utf-8'))
    start_new_thread(start_game_for_guesser, (game,))

def send_to_master(game, letter, type):
    master = get_connection(game.id_game_master)
    if type == 'goon':
        response = 'WISIELEC\r\n201 OK\r\nGAMEKEY: ' + str(game.game_key_) + '\r\nLETTER: ' + str(letter) + '\r\nLIFES: ' + str(game.lives) +'\r\n\r\n'
        logger.info('Sending message to Client: ' + str(master) + ' ' + 'Message: ' + repr(response));
        master.send(response.encode('utf-8'))
    elif type == 'gameover':
        response = 'WISIELEC\r\nGAMEOVER\r\nLIFES: ' + str(game.lives) + '\r\n\r\n'
        logger.info('Sending message to Client: ' + str(master) + ' ' + 'Message: ' + repr(response));
        master.send(response.encode('utf-8'))
    elif type == 'win':
        response = 'WISIELEC\r\nWIN\r\nGAMEKEY: ' + str(game.game_key_) + '\r\n\r\n'
        logger.info('Sending message to Client: ' + str(master) + ' ' + 'Message: ' + repr(response));
        master.send(response.encode('utf-8'))
    elif type == 'nextgame':
        response = 'WISIELEC\r\nNEXTGAME' + '\r\n\r\n'
        logger.info('Sending message to Client: ' + str(master) + ' ' + 'Message: ' + repr(response));
        master.send(response.encode('utf-8'))

def check_letter_from_guesser(client, message, usr_id):
    game = find_game(usr_id)
    letter = message.split('LETTER: ')[1].split('\r\n\r\n')[0]
    if letter == ' ' or len(letter) > 1:
        response = 'WISIELEC\r\n400 Bad Request\r\n\r\n'
        logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
        client.send(response.encode('utf-8'))

    result = game.check_letter(letter)

    if result == 'GAME IS NOT ON':
        response = 'WISIELEC\r\n409 NOT ON\r\n\r\n'
        logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
        client.send(response.encode('utf-8'))
    elif result == 'MISS':
        send_to_master(game, letter,'goon')
        response = 'WISIELEC\r\nSESSIONID: ' + usr_id + '\r\nPLAY\r\nLIFES: ' + str(game.lives) + '\r\nGAMEKEY: ' + str(game.game_key_) +  '\r\n\r\n'
        logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
        client.send(response.encode('utf-8'))
    elif result == 'NEXTLETTER':
        send_to_master(game, letter, 'goon')
        response = 'WISIELEC\r\nSESSIONID: ' + usr_id + '\r\nPLAY\r\nLIFES: ' + str(game.lives) + '\r\nGAMEKEY: ' + str(game.game_key_) + '\r\n\r\n'
        logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
        client.send(response.encode('utf-8'))
    elif result == 'GAMEOVER: LOSE':
        room = find_room(usr_id)
        room.game_is_not_on = False
        send_to_master(game, letter, 'win')
        response = 'WISIELEC\r\nSESSIONID: ' + usr_id + '\r\nLOSE\r\nGAMEKEY: ' + str(game.game_key_) + '\r\nGAMEKEYTRUE: ' + str(game.game_key) +'\r\n\r\n'
        logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
        client.send(response.encode('utf-8'))
    elif result == 'GAMEOVER: WIN':
        room = find_room(usr_id)
        room.game_is_not_on = False
        send_to_master(game, letter, 'gameover')
        response = 'WISIELEC\r\nSESSIONID: ' + usr_id + '\r\nWIN\r\nLIFES: ' + str(game.lives) + '\r\nGAMEKEY: ' + str(game.game_key) + '\r\n\r\n'
        logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
        client.send(response.encode('utf-8'))
def delete_game_and_room(usr_id):
    game = find_game(usr_id)
    room = find_room(usr_id)
    if game != None:
        game_table.remove(game)
    if room != None:
        room_table.remove(room)

def send_end_game_communicate(client):
    response = 'WISIELEC\r\nEND GAME\r\n\r\n'
    logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
    client.send(response.encode('utf-8'))

def ask_for_game_continuation(client, message, usr_id):
    value = message.split('VALUE: ')[1].split('\r\n\r\n')[0]
    room = find_room(usr_id)

    if value == 'Y' or value == 'N':
        if room.host == usr_id:
            #changing value of "continuation" tuple for first player
            tmp = list(room.continue_game)
            tmp[0] = value
            room.continue_game = tuple(tmp)

        elif room.other_player == usr_id:
            # changing value of "continuation" tuple for second player
            tmp = list(room.continue_game)
            tmp[1] = value
            room.continue_game = tuple(tmp)

        else:
            response = 'WISIELEC\r\n401 Not Authoritated\r\n\r\n'
            logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
            client.send(response.encode('utf-8'))
    else:
        response = 'WISIELEC\r\n400 Bad Request\r\n\r\n'
        logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
        client.send(response.encode('utf-8'))

    #waiting for other player answer
    if room.continue_game[0] == '' or room.continue_game[1] == '':
        return

    #both players want to play again
    if room.continue_game[0] == 'Y' and room.continue_game[1] == 'Y':
        game = find_game(usr_id)

        #swaping game master with host after continuation
        tmp = game.id_game_master
        game.id_game_master = game.id_guesser
        game.id_guesser = tmp

        room.continue_game = ('', '')
        game.lives = 10

        guesser = get_connection(game.id_guesser)
        game_master = get_connection(game.id_game_master)

        start_new_thread(start_game_thread, (game_master, game.id_game_master))
        start_new_thread(start_game_thread, (guesser, game.id_game_master))

    #one of players do not want to continue - game is closed and room deleted
    elif room.continue_game[0] == 'N' or room.continue_game[1] == 'N':
        guesser_id = room.other_player
        host_id = room.host

        guesser = get_connection(guesser_id)
        host = get_connection(host_id)

        delete_game_and_room(usr_id)
        start_new_thread(send_end_game_communicate, (guesser,))
        start_new_thread(send_end_game_communicate, (host,))
    else:
        response = 'WISIELEC\r\n400 Bad Request\r\n\r\n'
        logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
        client.send(response.encode('utf-8'))

#"switch" dealing with communication messages
def recognize_communication(client, message):
    communicate = message.split('\r\n')[2]
    usr_id = message.split('SESSIONID: ')[1].split('\r\n')[0]
    logger.info('Client ' + str(client) + ' Message: ' + repr(message));
    if get_connection(usr_id) == None: # unknown session_id
        response = 'WISIELEC\r\n401 Unauthorized\r\n\r\n'
        logger.info('Unauthorized client: ' + str(client))
        client.send(response.encode('utf-8'))

    if communicate == 'CREATE': #create new room
        create_room(client, message, usr_id)
    elif communicate == "ROOMLIST": #send list of rooms to client
        send_room_list(client)
    elif communicate == 'JOIN': #join to the room
        join_room(client, message, usr_id)
    elif communicate == 'SETGAMEKEY':   #setting room key
        set_key_in_game(client, message, usr_id)
    elif communicate == 'PLAY': #starting game
        check_letter_from_guesser(client, message, usr_id)
    elif communicate == 'WANTNEXT': #asking for next game
        ask_for_game_continuation(client, message, usr_id)
    elif communicate == 'CLOSED':
        delete_game_and_room(usr_id)
        logger.info('Connection closed with Client: ' + str(client));

    else:
        print("unrecognized communicate")
        response = 'WISIELEC\r\n400 Bad Request\r\n\r\n'
        logger.info('Sending message to Client: ' + str(client) + ' ' + 'Message: ' + repr(response));
        client.send(response.encode('utf-8'))

#dealing with recognize_communication
def player_service(client):
    try:
        start_communication(client)

        while True:
            message = get_message(client, 1024)
            recognize_communication(client, message)
    except ConnectionResetError:
        id = get_usrID_by_client(client)
        if id != None:
            delete_game_and_room(id)
        logger.info('Connection closed: ' + str(client))
    except error:
            print(error.with_traceback())
    finally:
        client.close()

def main():
    try:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_cert_chain(certfile='server.crt', keyfile='server.key', password='andrzejkarwoski')
        context.load_verify_locations(cafile='client.crt')
        ss = context.wrap_socket(s, server_side=True)
        while True:
            c, addr = ss.accept()
            start_new_thread(player_service, (c, ))
    except error:
        print(error.with_traceback())
    finally:
        s.close()

main()
s.close()