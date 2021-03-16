from config import db_path
from db_manager import Database

if __name__ == '__main__':

    db = Database(db_path)

    print('Welcome to ADMIN PROMT!')


    while True:
        enter_command = input('> ')
        
        command, *args = enter_command.split()
        print(command)
        print(args)
        if command == 'admin':
            if len(args) > 0:
                db.to_admin(args[0])
        elif command == 'unadmin':
            if len(args) > 0:
                print()
                db.from_admin(args[0])
