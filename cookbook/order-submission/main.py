import web
from web import form

render = web.template.render('genohm/cookbook/order-submission/templates/')

register_form = form.Form(
    form.Textbox("Project", description="Project"),
    form.Button("submit", type="submit", description="Register"),
)

urls = (
  '/', 'CreateOrder',
)


class CreateOrder:

    def GET(self):
        f = register_form()
        return render.add_order(f)

    def POST(self):
        f = register_form()
        if not f.validates():
            return render.add_order(f)
        else:
            # Put Slims code here
            return render.add_order_success()


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
