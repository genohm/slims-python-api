from genohm.slims.slims import Slims
from genohm.slims.criteria import *
from genohm.slims.util import *

slims = Slims("testSlims", "http://localhost:9999", "admin", "admin", repo_location="/Users/Ruben/RepoRepo/deplancke38")


# To print the value of the value of operator, fieldname and value used by the function
# print is_na("cntn_cf_treatment").to_dict()
print is_not_null("cntn_cf_lenght").to_dict()

# EXAMPLE OF OPERATOR COMBINATIONS
# records = slims.fetch("Content", is_one_of("cntn_id", ["sample1", "sample2"]))
# records = slims.fetch("Content", is_not(starts_with("cntn_id", "chemical")))
# records = slims.fetch("Content", is_not(ends_with("cntn_id", "0")))
# records = slims.fetch("Content", disjunction()
#                      .add(starts_with("cntn_id", "chemical"))
#                      .add(starts_with("cntn_id", "sample")))
# records = slims.fetch("Content", between_inclusive_match_case("cntn_id", "0", "3"))
# records = slims.fetch("Content", is_not(conjunction()
#                                        .add(not_equals("cntn_id", "sample1"))
#                                        .add(starts_with("cntn_id", "sample"))))
# records = slims.fetch("Content", equalsIgnoreCase("cntn_id", "SAMPLE1"))
# records = slims.fetch("Content", is_na("cntn_cf_treatment"))
# records = slims.fetch("Content", is_not_null("cntn_cf_lenght"), ["cntn_cf_lenght", "cntn_id"])
records = slims.fetch("Content", is_not_null("cntn_createdOn"), ["cntn_createdOn", "cntn_id"], 15, 30)
# records = slims.fetch("Content", is_not_null("cntn_fk_disease"), ["cntn_pk", "cntn_id"])
# records = slims.fetch("Content", starts_with("cntn_id", "0"))
# records = slims.fetch("Content", is_na("cntn_cf_treatment"))
# Not equal or starts with - example
# records = slims.fetch("Content", disjunction()
#                      .add(not_equals("cntn_id", "chemical_0000"))
#                      .add(starts_with("cntn_id", "sample")))

# DISPLAY RESULTS
# display_results(records, ["cntn_id"])
# display_results(records, ["cntn_id", "cntn_cf_presence"])
# display_results(records, ["cntn_quantity", "cntn_id"])
display_results(records, ["cntn_createdOn", "cntn_id"])
# display_results(records, ["cntn_id", "cntn_createdOn"], 5)
