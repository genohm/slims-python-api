""" In this script, many examples of operators for fetching are illustrated as well
    as the function to display the results. Operators can be conjunctive, disjunctive
    or inversive.

    The name of the operator functions are in most of the case self explanatory. They
    are defined and explained in python file criteria.
    For these demonstrations to work, once needs to have contents in SLims.
    The value of the fields can be addapted depending on the database present in SLims.
"""
from slims.slims import Slims
from slims.criteria import is_not_null
from slims.criteria import equals
from slims.criteria import contains
from slims.criteria import starts_with
from slims.criteria import ends_with
from slims.criteria import between_inclusive_match_case
from slims.criteria import conjunction
from slims.criteria import disjunction
from slims.criteria import is_not
from slims.util import display_results

slims = Slims("testSlims", "http://localhost:9999", "admin", "admin", repo_location="/Users/Ruben/RepoRepo/deplancke38")


# EXAMPLE OF OPERATOR COMBINATIONS

# Example N_1:
# We fetch Content records without criteria
# This means that all the contents present in the database will match
# By giving start and end parameters we can limit only the 10th to the 30th
# record to be returned
print("Example 1")
records = slims.fetch("Content", None, start=10, end=30)
# The fields ID and Barcode of the records will be displayed
display_results(records, ["cntn_id", "cntn_barCode"])

# Example N_2:
# Fetching content records with the criteria equals which takes two parameters;
# The field on which to filter and the value. This way we will filter for
# Content whose cntn_id is equal to "fish"
print("\n\nExample 2")
records = slims.fetch("Content", equals("cntn_id", "fish"))
display_results(records, ["cntn_id", "cntn_createdOn"])

# Example N_3:
# Fetching content records with a conjunction (and). This filters
# on content records for which the cntn_id is not null and the cntn_id starts with
# fish
print("\n\nExample 3")
records = slims.fetch("Content", conjunction().add(is_not_null("cntn_id"))
                                              .add(starts_with("cntn_id", "fish")))
# The third parameter of display_results allows to choose the x first results to display
display_results(records, ["cntn_id"], 10)

# Example N_4:
# Fetching content records with a disjunction (or). This filters for content
# records for which the cntn_id either contains "fish" or ends with a "9"
print("\n\nExample 4")
records = slims.fetch("Content", disjunction().add(contains("cntn_id", "fish"))
                                              .add(ends_with("cntn_id", "9")))
display_results(records, ["cntn_id"])

# Example N_5:
# Fetching in Content with a negation of the operator between
# The sorting is done by cntn_barcode and then cntn_id
print("\n\nExample 5")
records = slims.fetch("Content",
                      is_not(between_inclusive_match_case("cntn_id", "00000002", "00000166")),
                      sort=["cntn_barCode", "cntn_id"])
display_results(records, ["cntn_id"])
