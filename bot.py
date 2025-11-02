import pandas as pd

# Load the medicine database
data = pd.read_csv("data/medicines.csv")

def search_medicine(name):
    """Search for a medicine name and return its info."""
    result = data[data['Drug Name'].str.lower() == name.lower()]
    if result.empty:
        return "Medicine not found in database."
    
    info = result.iloc[0]
    return f"""
💊 **{info['Drug Name']}**
Class: {info['Class']}
Indication: {info['Indication']}
Dosage: {info['Dosage']}
Side Effects: {info['Side Effects']}
Special Instructions: {info['Special Instructions']}
"""

# Test run
if __name__ == "__main__":
    med = input("Enter medicine name: ")
    print(search_medicine(med))
