from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose

VERSION = "0.0.1"

BANNER = """Protected Shelf v%s""" % VERSION


# define any hook functions here
def my_cleanup_hook(app):
    pass


class BaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = "Application does amazing things!"
        arguments = [
            (['-v', '--version'], dict(action='version', version=BANNER)),
            (['-u', '--create-user'],
                dict(action='store', help='the notorious foo option')),
            (['-c'],
                dict(action='store_true', help='the big C option')),
            ]

    @expose(hide=True)
    def default(self):
        self.app.log.info('Inside BaseController.default()')
        print("Welcome to " + BANNER)
        print("Type 'shelf --help' to see available commands.")

    # New user sign up
    @expose(help="Create new user")
    def create(self):
        self.app.log.info("Inside BaseController.create()")

    # Activate prompt
    @expose(help="Open session")
    def open(self):
        self.app.log.info("Inside BaseController.open()")


class App(CementApp):
    class Meta:
        label = 'shelf'
        extensions = ['json']
        hooks = [
            ('pre_close', my_cleanup_hook),
        ]
        base_controller = 'base'
        handlers = [BaseController]


with App() as app:
    # log stuff
    app.log.debug("About to run " + BANNER)

    # run the application
    app.run()
