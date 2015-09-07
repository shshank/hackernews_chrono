import database
import models

def setup():
    print 'creating schema.. ',
    database.init_db()
    print 'Done'

    admin_exists = bool(models.User.query.filter(models.User.user_type==5).first())
    create_admin = None

    if admin_exists:
        print 'Admin user already exists.'

    while not create_admin:
        create_admin = raw_input('Want to create a new admin user? (y/n)')
        if create_admin.lower() not in ['y', 'n']:
            print 'Wrong input'

    if create_admin == 'y':
        user_exists = True
        while user_exists:
            username = raw_input("username (>= than 6 chars, Alphanumeric and _ only.): ")
            user_exists = models.User.query.filter(models.User.username==username).first()
            if user_exists:
                print 'username already exists, choose another.'

        password = raw_input("password (>= than 6 chars): ")
        models.User.add_new(username=username, password=password, user_type=5)

    print "Done."


if __name__ == '__main__':
    setup()
