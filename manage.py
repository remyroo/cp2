from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from bucketlist import app, db, views

'''
Create scripts that allow
db creation and migrations to run
from the shell using manage.py commands.
'''
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
