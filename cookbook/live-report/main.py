"""This web application is displaying on a web page a live report for a selected period.
   This script requires dateutils and web.py (pip install web.py dateutils)
"""

import datetime
import web
from dateutil.relativedelta import relativedelta
from web import form
from slims.slims import Slims
from slims.criteria import between_inclusive

render = web.template.render('templates/')
slims = Slims("slims", "http://localhost:9999", "admin", "admin")

# Creation of the register from which will allow the user to choose a period of time
period = [('days', 'one day'), ('weeks', 'one week'), ('months', 'one month'), ('years', 'one year')]

register_form = form.Form(
    form.Radio("Period", period, description="Number of Time to Display"),
    form.Button("submit", type="submit", description="Register"),
)

urls = (
  '/', 'DisplayReport',
)


def calculate_previous_date(current, period):
    return current - relativedelta(**{period: 1})


def get_attribute_of_column(record, column, attribute):
    if record is None:
        return " - "
    if not hasattr(record, column):
        return " - "
    if not hasattr(record.column(column), attribute):
        return " - "

    return getattr(record.column(column), attribute)


class DisplayReport:

    def GET(self):
        f = register_form()
        return render.displaying_days(f)

    def POST(self):
        f = register_form()
        if not f.validates():
            return render.displaying_days(f)
        else:
            now = datetime.datetime.now()
            period = f.d.Period
            previous_date = calculate_previous_date(now, period)

            # Searching for the results in the selected period of time
            records = slims.fetch("Result",
                                  between_inclusive("rslt_createdOn", previous_date, now),
                                  sort=["rslt_fk_test", "rslt_fk_content"])

            table = []
            for record in records:
                # For each record we create a row in the table
                row = []
                row.append(get_attribute_of_column(record, "rslt_fk_content", "displayValue"))
                row.append(get_attribute_of_column(record, "rslt_fk_test", "displayValue"))
                row.append(get_attribute_of_column(record, "rslt_value", "value"))
                row.append(get_attribute_of_column(record, "rslt_value", "unit"))

                # ExperimentRun
                if record.rslt_fk_experimentRunStep.value is None:
                    row.append(" - ")
                else:
                    # ExperimentRun (first fetch the experimentrunstep, then get its name)
                    experimentRunStep = record.follow("rslt_fk_experimentRunStep")
                    row.append(experimentRunStep.xprs_fk_experimentRun.displayValue)

                table.append(row)

            return render.display_report(table, f.d.Period)


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
