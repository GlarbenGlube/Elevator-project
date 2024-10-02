import socket

def getUserInputInt(start,end):
    validInput = False
    value = -1
    print(f"Enter a number to choose a menu option: ")
    while validInput != True:
        try:
            value = int(input())
        except:
            print("Please choose one of the menu options")
        if (start<=value and value<=end):
            return int(value)
            validInput = True
        else:
            print("Invalid Input, please try again: ")

def menu():
    print("0:  Stueetagen")
    print("1:  1. sal")
    print("2:  2. sal\n")
    print("9:  Luk program")
    match(getUserInputInt(0,9)):
        case 9:
            print("See you later!")
            quit()

        case 0:
            print("Afsted mod stueetagen")
            return '1'
        case 1:
            print("Afsted mod 1. sal")
            return '2'
        case 2:
            print("Afsted mod 2. sal")
            return '3'
        case _:
            print("Nah mate, choose an actual floor... No cheating this time")
            return 'eyo'

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
while True:
    command = menu()

    sock.sendto(bytes(command, "utf-8"), ('10.110.0.188' , 5001))

