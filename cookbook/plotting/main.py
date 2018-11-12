""" In this example, results are fetched from slims and plotted

    Contents of type "Patient" and results associated to them for tests
    "length Test" and "weight test" (labels). A patient HAS TO HAVE one
    and only one result for each test.

    A BMI Calculation is done based on both.

    The plotting requires matplotlib (pip install matplotlib)

    run this script using the underneath command in the folder plotting
    python main.py
"""
from __future__ import division
from slims.slims import Slims
from slims.criteria import equals, is_one_of
import matplotlib.pyplot as plt

slims = Slims("slims", "http://localhost:9999", "admin", "admin")

# Data fetch -> selection of patients and their results
patients = slims.fetch("Content", equals("cntp_name", "Patient"))
patient_pks = map(lambda patient: patient.pk(), patients)

results = slims.fetch("Result", is_one_of("rslt_fk_content", patient_pks))

lengths = []
weights = []
BMI = []
x_axis_values = []

# Identification of the result per test
print ("Fetching necessary data...")
for result in results:
    # first identification the length Test results
    if result.rslt_fk_test.displayValue in "length Test":
        lengths.append(result.rslt_value.value)
        # Storage of content ID to display them on x axis
        x_axis_values.append(result.rslt_fk_content.displayValue)
    # first identification the weight Test results
    if result.rslt_fk_test.displayValue in "weight test":
        weights.append(result.rslt_value.value)

# Calculation and creation of the new BMI result
print ("Calculating BMI")
for i in range(len(weights)):
    BMI.append(weights[i] / (lengths[i] * lengths[i]))

x_axis = [i for i in range(len(x_axis_values))]

# Plots
print("Drawing graphs")
plt.figure(figsize=(20, 12))

# Plot of the length of the selected content
plt.subplot(311)
plt.xticks(x_axis, x_axis_values, rotation='vertical')
plt.title('Length')
plt.plot(x_axis, lengths, 'ro')
plt.xlabel('Barcode')
plt.ylabel('Length [m]')

# Plot of the weight of the selected content
plt.subplot(312)
plt.xticks(x_axis, x_axis_values, rotation='vertical')
plt.title('Weight')
plt.plot(x_axis, weights, 'bo')
plt.xlabel('Barcode')
plt.ylabel('Weigth [kg]')

# Plot of the BMI of the selected content
plt.subplot(313)
plt.xticks(x_axis, x_axis_values, rotation='vertical')
plt.title('BMI')
plt.plot(x_axis, BMI, 'ro')
plt.xlabel('Barcode')
plt.ylabel('BMI [kg/m^2]')

plt.subplots_adjust(hspace=1.25)

plt.show()
