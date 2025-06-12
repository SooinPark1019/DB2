from mysql.connector import connect

def initialize_database():
    # YOUR CODE GOES HERE
    # print msg
    print('Database successfully initialized')
    pass

def reset():
    # YOUR CODE GOES HERE
    pass

def print_DVDs():
    # YOUR CODE GOES HERE
    # print msg
    pass

def print_users():
    # YOUR CODE GOES HERE
    # print msg
    pass

def insert_DVD():
    title = input('DVD title: ')
    director = input('DVD director: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def remove_DVD():
    DVD_id = input('DVD ID: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def insert_user():
    name = input('User name: ')
    age = input('User age: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def remove_user():
    user_id = input('User ID: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def checkout_DVD():
    DVD_id = input('DVD ID: ')
    user_id = input('User ID: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def return_and_rate_DVD():
    DVD_id = input('DVD ID: ')
    user_id = input('User ID: ')
    rating = input('Ratings (1~5): ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def print_borrowing_status_for_user():
    user_id = input('User ID: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def search():
    query = input('Query: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def recommend_popularity():
    # YOUR CODE GOES HERE
    user_id = input('User ID: ')
    # YOUR CODE GOES HERE
    # print msg
    pass

def recommend_user_based():
    user_id = input('User ID: ')
    # YOUR CODE GOES HERE
    # print msg
    pass


def main():
    while True:
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
        menu = int(input('Select your action: '))

        if menu == 1:
            initialize_database()
        elif menu == 2:
            print_DVDs()
        elif menu == 3:
            print_users()
        elif menu == 4:
            insert_DVD()
        elif menu == 5:
            remove_DVD()
        elif menu == 6:
            insert_user()
        elif menu == 7:
            remove_user()
        elif menu == 8:
            checkout_DVD()
        elif menu == 9:
            return_and_rate_DVD()
        elif menu == 10:
            print_borrowing_status_for_user()
        elif menu == 11:
            search()
        elif menu == 12:
            recommend_popularity()
        elif menu == 13:
            recommend_user_based()
        elif menu == 14:
            print('Bye!')
            break
        elif menu == 15:
            reset()
        else:
            print('Invalid action')


if __name__ == "__main__":
    main()
