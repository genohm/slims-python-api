""" In this sample web application, a user can create a content record,  an
    order and select one requet

    This is written using web.py (pip install web.py) and demonstrates
    some fetching and inserting of data via the REST api. #be careful, web.py
    does not work with python 3.x

    Launch the script from within the order-submission folder with the command
    python main.py 7777
    this way the report can be accessed on http://localhost:7777
"""
from __future__ import print_function
import web
from web import form
from slims.slims import Slims
from slims.criteria import is_not
from slims.criteria import equals
from slims.content import Status


render = web.template.render('templates/')
slims = Slims("slims", "http://localhost:9999", "admin", "admin")

# Populate the comboboxes
# Searching for data by fetching
order_types = slims.fetch("OrderType", None)
content_types = slims.fetch("ContentType", equals("cntp_useBarcodeAsId", True))
locations = slims.fetch("Location", None)
requestables = slims.fetch("Requestable", is_not(equals("rqbl_type", "WORKFLOW")))

dic_order_type = {}
for order_type in order_types:
    dic_order_type.update({order_type.rdtp_name.value: order_type})

dic_content_type = {}
for content_type in content_types:
    dic_content_type.update({content_type.cntp_name.value: content_type})

dic_location = {}
for location in locations:
    dic_location.update({location.lctn_name.value: location})

dic_requestable = {}
for requestable in requestables:
    dic_requestable.update({requestable.rqbl_name.value: requestable})


# Web page inputs
first_form = form.Form(
    form.Dropdown("OrderType", dic_order_type, description="Order Type"),
    form.Dropdown("NewContentType", dic_content_type, description="New Content Type"),
    form.Dropdown("LocationNewContent", dic_location, description="Location of New Content"),
    form.Button("submit", type="submit", description="Continue to second stage"),
)

second_form = form.Form(
    form.Hidden("OrderType"),
    form.Hidden("NewContentType"),
    form.Hidden("LocationNewContent"),
    form.Dropdown("Requestable", dic_requestable, description="Requestable"),
    form.Button("submit", type="submit", description="Create order"),
)

urls = (
    '/', 'CreateOrder',
    '/CreateOrderFirst', 'CreateOrderFirst',
    '/CreateOrderSecond', 'CreateOrderSecond',
)


class CreateOrder:

    def GET(self):
        first = first_form()
        return render.add_order(first, "CreateOrderFirst")


class CreateOrderFirst:

    def POST(self):
        first = first_form()
        if not first.validates():
            return render.add_order(first, "CreateOrderFirst")
        else:
            second = second_form()
            # Pass values from first into second forms
            second.OrderType.value = first.d.OrderType
            second.NewContentType.value = first.d.NewContentType
            second.LocationNewContent.value = first.d.LocationNewContent

            return render.add_order(second, "CreateOrderSecond")


class CreateOrderSecond:

    def POST(self):
        second = second_form()
        if not second.validates():
            return render.add_order(second, "CreateOrderSecond")
        else:
            added_content = slims.add('Content', {
                'cntn_fk_contentType': dic_content_type[second.d.NewContentType].pk(),
                'cntn_status': Status.PENDING.value,
                'cntn_fk_location': dic_location[second.d.LocationNewContent].pk()
            })

            added_order = slims.add('Order', {
                'ordr_fk_orderType': dic_order_type[second.d.OrderType].pk()
            })

            slims.add('OrderContent', {
                'rdcn_fk_order': added_order.pk(),
                'rdcn_fk_content': added_content.pk()
            })

            slims.add('Request', {
                'rqst_fk_content': added_content.pk(),
                'rqst_fk_order': added_order.pk(),
                'rqst_fk_requestable': dic_requestable[second.d.Requestable].pk()
            })

            return render.add_order_success(added_order, added_content)


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
