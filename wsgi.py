from App import create_app, db
import click
from flask.cli import with_appcontext
from App.models import Counter

app = create_app()


@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()


@click.command(name='drop_db')
@with_appcontext
def drop_db():
    """Cleans database"""
    db.drop_all()


@click.command(name='create_count')
@click.argument('value')
@with_appcontext
def create_count(value):
    counter = Counter(count=value)
    db.session.add(counter)
    db.session.commit()


app.cli.add_command(create_tables)
app.cli.add_command(drop_db)
app.cli.add_command(create_count)

# ctx = app.app_context()
# ctx.push()  # start working on database after that command
# # Database manipulations here
# db.create_all()
# counter = Counter(count=0)
# db.session.add(counter)
# db.session.commit()
# ctx.pop()  # exit from the app

if __name__ == '__main__':
    app.run(debug=True)
