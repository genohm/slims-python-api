============
Introduction
============

The slims-python-api is a project that allows users to interact easily with SLims
using python scripting. All communication is done via SLims' REST API so similar
approaches could work for other programming languages.

Installing slims-python-api
---------------------------

The required Python version is 3.9

You install slims-python-api with pip. Make sure to install the version corresponding to your installed slims version.

If you run SLIMS 6.3 you run

.. code-block:: bash
   
   pip install 'slims-python-api>=6.3.0,<6.4.0'

If you run SLIMS 6.2 you run

.. code-block:: bash
   
   pip install 'slims-python-api>=6.2.0,<6.3.0'


Some simple examples
--------------------

.. code-block:: python

   from slims.slims import Slims
   from slims.criteria import equals

   slims = Slims("test", "https://testserver.com/slimsrest/", "admin", "admin")
   content_records = slims.fetch("Content", equals("cntn_id", "test"))
   for content_record in content_records:
      print(content_record.cntn_barCode.value + " " +
            content_record.cntn_fk_location.displayValue)


Here we fetch all the content record with "test" as their id. Then we loop over them
and print their barcode and the name of the location they are in.

.. code-block:: python

   slims = Slims("test", "https://testserver.com/slimsrest/", "admin", "admin")
   content_records = slims.fetch("Content", equals("cntn_id", "test"))

   for content_record in content_records:
      content_record.update({"cntn_id", "foo"})

We fetch all the content records with "test" as their id and then update it to "foo"

These operations are combined in two of our cookbook examples.

- Fetching and displaying data on the command line
  https://github.com/genohm/slims-python-api/blob/master/cookbook/data-manipulation/fetching_data.py
- Updating, adding and removing records
  https://github.com/genohm/slims-python-api/blob/master/cookbook/data-manipulation/data_modification.py
- Sample web application (in web.py) that allows users to submit orders in a simple fashion
  https://github.com/genohm/slims-python-api/blob/master/cookbook/order-submission/main.py
- Sample web application that shows a table of the latest results in slims
  https://github.com/genohm/slims-python-api/blob/master/cookbook/live-report/main.py
- Fetching data and then plogging them 
  https://github.com/genohm/slims-python-api/blob/master/cookbook/plotting/main.py
