""" In this script, examples of operators for fetching are illustrated as well
    as the function to display the results. Operators can be conjunctive,
    disjunctive or inversive.

    The name of the operator functions are in most of the case self explanatory.
    They are defined and explained in python file criteria.
    For these demonstrations to work, contents need to be present in SLims.
    Ideally over 30 contents need to be present. Here is a list of content ids
    to include in your SLims instance to test correctly the following examples:
    - "fish"
    - "fish_12"
    - "fish_9"
    - "buble_9"
    - "blood_0009"
    - "DNA_012019"
    - "00000002"
    - "00000100"
    - "00000166"
    The value of the fields can be adapted depending on the database present
    in SLims.


    run this script using the underneath command in the folder containing it.
    python data_modification.py
"""
from slims.slims import Slims
from slims.criteria import is_not_null
from slims.criteria import equals
from slims.criteria import contains
from slims.criteria import starts_with
from slims.criteria import ends_with
from slims.criteria import between_inclusive
from slims.criteria import conjunction
from slims.criteria import disjunction
from slims.criteria import is_not
from slims.util import display_results

slims = Slims("slims", "http://localhost:9999", "admin", "admin")


# EXAMPLE OF OPERATOR COMBINATIONS

# Example N_1:
# We fetch Content records without criteria
# This means that the fetch includes all the contents in the database
# By giving start and end parameters the output is limited to the 10th to the
# 30th record to be returned
print("Example 1")
records = slims.fetch("Content", None, start=10, end=30)
# The fields cntn_id and cntn_barCode of the content records will be displayed
display_results(records, ["cntn_id", "cntn_barCode"])

# Example N_2:
# Fetching content records with the equals criteria;
# The parameters are the field on which to filter and the value. This way the
# filter only returns contents whose cntn_id is equal to "fish"
print("\n\nExample 2")
records = slims.fetch("Content", equals("cntn_id", "fish"))
display_results(records, ["cntn_id", "cntn_createdOn"])

# Example N_3:
# Fetching content records with a conjunction (and). This filters
# on content records for which the cntn_id is not null and the cntn_id starts
# with fish
print("\n\nExample 3")
records = slims.fetch("Content", conjunction().add(is_not_null("cntn_id"))
                                              .add(starts_with("cntn_id", "fish")))
# display_results has three arguments, the list of records, the list of fields
# to display and finally the number of results to display
display_results(records, ["cntn_id"], 10)

# Example N_4:
# Fetching content records with a disjunction (or). This filters content
# records for which the cntn_id either contains "fish" or ends with "9"
print("\n\nExample 4")
records = slims.fetch("Content", disjunction().add(contains("cntn_id", "fish"))
                                              .add(ends_with("cntn_id", "9")))
display_results(records, ["cntn_id"])

# Example N_5:
# Fetching in Content with a negation of the operator between.
# This filters all the contents whose id is not between "00000002" and "00000166"
# The sort is by cntn_barcode and then by cntn_id
print("\n\nExample 5")
records = slims.fetch("Content",
                      is_not(between_inclusive("cntn_id", "00000002", "00000166")),
                      sort=["cntn_barCode", "cntn_id"])
display_results(records, ["cntn_id"])
