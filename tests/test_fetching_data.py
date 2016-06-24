from genohm.slims import Slims

slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
records = slims.fetch("Content", "cntn_barCode=00000004")
for record in records:
    print(record.column("cntn_id").value())

locations = slims.fetch("Location", "lctn_barCode=00000001")
for record in locations:
    print(record.column("lctn_barCode").value())
