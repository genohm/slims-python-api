""" In this script, we demonstrate creating, modifying and removing content.

    When creating a new record in SLims one needs to be careful about the
    mandatory fields to fill. For example creating a new content may require
    an ID or not depending on whereas the associate box in its related content
    type is checked or not.

    run this script using the underneath command in the folder containing it.
    python data_modification.py
"""
from slims.slims import Slims
from slims.criteria import equals, conjunction
import sys

slims = Slims("slims", "http://localhost:9999", "admin", "admin")

# Example N_1: Creating a content record; here a Content of content type DNA
#              in the location Building Test. Requires a location called
#              "Building test" (of location type Building) and a content type
#              "DNA" (with use barcode as id)

print("Example 1")
# Fetch DNA content type
dna_type = slims.fetch("ContentType", equals("cntp_name", "DNA"))

if not dna_type:
    sys.exit("No DNA Content type found, can not continue")

# Fetch Building Test location (ideally with location type Building,
# but this is not mandatory)
locations = slims.fetch("Location", equals("lctn_name", "Building Test"))

if not locations:
    sys.exit("No location called Building Test found, can not continue")

# Fetch the Pending status on Content
statuses = slims.fetch("Status", conjunction()
                       .add(equals("stts_name", "Pending"))
                       .add(equals("stts_fk_table", 2)))

if not statuses:
    sys.exit("Could not find an active Status called 'Pending' on Content, can not continue")

print("Creating DNA Record...")
created_dna = slims.add("Content",
                        {'cntn_fk_contentType': dna_type[0].pk(),
                         'cntn_fk_status': statuses[0].pk(),
                         'cntn_fk_location': locations[0].pk()})

print("Content with status", created_dna.cntn_fk_status.displayValue,
      ", location", created_dna.cntn_fk_location.displayValue,
      "and type", created_dna.cntn_fk_contentType.displayValue,
      "has been created.\n\n")

# Example N_2: Creating another content record. Requires a content type "fish"
#              for which "Use barcode as ID" is set to false.

# Fetch fish content type
print("Example 2")
fish_type = slims.fetch("ContentType", equals("cntp_name", "fish"))
if not fish_type:
    sys.exit("No fish Content type found, can not continue")

print("Creating fish record...")
created_fish = slims.add("Content",
                         {'cntn_fk_contentType': fish_type[0].pk(),
                          'cntn_fk_status': statuses[0].pk(),
                          'cntn_fk_location': locations[0].pk(),
                          'cntn_id': "Baby fish"
                          })

print("Content with status", created_fish.cntn_fk_status.displayValue,
      ", location", created_fish.cntn_fk_location.displayValue,
      "type", created_fish.cntn_fk_contentType.displayValue,
      "and id", created_fish.cntn_id.value,
      "has been created.\n\n")

# Example N_3: Creation of a result with test "weight" and link it to
#              The previously created fish record.
#              Requires a test with label "weight" and datatype quantity.
#              unit is kg.

# Fetch weight test
print("Example 3")
weight_test = slims.fetch("Test", equals("test_label", "weight"))

if not weight_test:
    sys.exit("No Weight test found, can not continue")

print("Creating the weight result...")
created_result = slims.add("Result",
                           {'rslt_fk_content': created_fish.pk(),
                            'rslt_fk_test': weight_test[0].pk(),
                            'rslt_value': {
                                'amount': 0.02,
                                'unit_display': weight_test[0].follow("test_fk_resultTablefield")
                                                              .follow("tbfl_fk_unit")
                                                              .unit_abbreviation.value,
                                'unit_pk': weight_test[0].follow("test_fk_resultTablefield")
                                                         .tbfl_fk_unit.value}})

print("A result of value", created_result.rslt_value.value, created_result.rslt_value.unit,
      ", linked to the content", created_fish.cntn_id.value,
      "was created\n\n")


# Example N_4: Modification of a result. The result created in Example
#              N_3 is modified. The fish has gained weight and the value
#              is updated to 0.5kg

print("Example 4")
print("Modifying result...")
modified_result = created_result.update({'rslt_value': {
                                         'amount': 0.5,
                                         'unit_display': weight_test[0].follow("test_fk_resultTablefield")
                                                                       .follow("tbfl_fk_unit")
                                                                       .unit_abbreviation.value,
                                         'unit_pk': weight_test[0].follow("test_fk_resultTablefield")
                                                                  .tbfl_fk_unit.value
                                         }})
print("Result linked to content", created_fish.cntn_id.value,
      "has been modified to", modified_result.rslt_value.value, modified_result.rslt_value.unit, "\n\n")

# Example N_5: Removing a content record created in Example 1
print("Example 5")
print("Removal of the content", created_dna.cntn_id.value, "...")
created_dna.remove()
print("The content", created_dna.cntn_id.value, "has been successfully removed")
