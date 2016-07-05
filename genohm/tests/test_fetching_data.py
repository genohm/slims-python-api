from genohm.slims.slims import Slims

slims = Slims("testSlims", "http://localhost:9999", "admin", "admin", repo_location="/Users/Ruben/RepoRepo/deplancke38")

records = slims.fetch("Content", "cntn_barCode=00000004")
for record in records:
    print(record.follow("cntn_fk_contentType").cntp_name.value)

    for derivation in record.follow("-cntn_fk_originalContent"):
        print derivation.cntn_id.value
