from genohm.slims.slims import Slims
from genohm.slims.criteria import *

slims = Slims("testSlims", "http://localhost:9999", "admin", "admin", repo_location="/Users/Ruben/RepoRepo/deplancke38")

records = slims.fetch("Content", disjunction()
                      .add(equals("cntn_barCode", "00000004"))
                      .add(equals("cntn_barCode", "00000005")))

for record in records:
    print(record.follow("cntn_fk_contentType").cntp_name.value)

    for derivation in record.follow("-cntn_fk_originalContent"):
        print derivation.cntn_id.value
