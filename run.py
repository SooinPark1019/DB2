from service import (
    initialize_database, print_DVDs
)

def print_menu():
    print('============================================================')
    print('1. initialize database')
    print('2. print all DVDs')
    print('3. print all users')
    print('4. insert a new DVD')
    print('5. remove a DVD')
    print('6. insert a new user')
    print('7. remove a user')
    print('8. check out a DVD')
    print('9. return and rate a DVD')
    print('10. print borrowing status of a user')
    print('11. search DVDs')
    print('12. recommend a DVD for a user using popularity-based method')
    print('13. recommend a DVD for a user using user-based collaborative filtering')
    print('14. exit')
    print('15. reset database')
    print('============================================================')

menu_actions = {
    1: initialize_database,
    2: print_DVDs,
}

def main():
    while True:
        print_menu()

        menu = int(input('Select your action: '))

        if menu == 14:
            print('Bye!')
            break
        elif menu in menu_actions:
            menu_actions[menu]()
        else:
            print('Invalid action')

if __name__ == "__main__":
    main()
