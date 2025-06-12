from service import (
    initialize_database, print_DVDs, insert_DVD, remove_DVD, print_users, insert_user, remove_user, checkout_DVD, return_and_rate_DVD, print_borrowing_status_for_user, search,
    recommend_popularity, recommend_user_based,
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
    3: print_users,
    4: insert_DVD,
    5: remove_DVD,
    6: insert_user,
    7: remove_user,
    8: checkout_DVD,
    9: return_and_rate_DVD,
    10: print_borrowing_status_for_user,
    11: search,
    12: recommend_popularity,
    13: recommend_user_based,
    15: initialize_database
}

def main():
    print_menu()
    while True:
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
