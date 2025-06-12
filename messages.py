# Success Messages
MSG_DB_INIT = "Database successfully initialized"
MSG_USER_INSERT = "One user successfully inserted"
MSG_DVD_INSERT = "DVD successfully inserted"
MSG_USER_REMOVE = "One user successfully removed"
MSG_DVD_REMOVE = "DVD successfully removed"
MSG_DVD_CHECKOUT = "DVD successfully checked out"
MSG_DVD_RETURNED_RATED = "DVD successfully returned and rated"
MSG_EXIT = "Bye!"

# Error Messages
ERR_TITLE_LENGTH = "Title length should range from 1 to 50 characters"
ERR_DIRECTOR_LENGTH = "Director length should range from 1 to 30 characters"
ERR_AGE_LIMIT = "Age limit should be an integer from 0 to 19"
ERR_DVD_EXISTS = "DVD ({}, {}) already exists"         # (title, director)
ERR_USERNAME_LENGTH = "Username length should range from 1 to 30 characters"
ERR_USER_AGE = "Age should be a positive integer"
ERR_DVD_NOT_EXIST = "DVD {} does not exist"           # (d_id)
ERR_DVD_BORROWED_CANNOT_DELETE = "Cannot delete a DVD that is currently borrowed"
ERR_USER_NOT_EXIST = "User {} does not exist"         # (u_id)
ERR_USER_BORROWED_CANNOT_DELETE = "Cannot delete a user with borrowed DVDs"
ERR_USER_BORROW_LIMIT = "User {} exceeded the maximum borrowing limit"  # (u_id)
ERR_USER_AGE_LIMIT = "User {} does not meet the age limit for this DVD" # (u_id)
ERR_DVD_OUT_OF_STOCK = "Cannot check out a DVD that is out of stock"
ERR_USER_RESTRICTED = "User {} is currently restricted from borrowing DVDs ({} attempts left)" # (u_id, remain)
ERR_RATING_RANGE = "Rating should be an integer from 1 to 5"
ERR_NOT_BORROWED = "Cannot return and rate a DVD that is not currently borrowed for this user"
ERR_SEARCH_FAIL = "Cannot find any matching results"
ERR_NO_RECOMMEND = "No DVD can be recommended"
