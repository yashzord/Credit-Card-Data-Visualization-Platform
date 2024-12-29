import sqlite3
import shutil

# Path to existing database
original_db_path = r"C:\Users\yashu\OneDrive\Desktop\Github_Projects\Credit_Card_Data_Visulization_Platform\Final_Databases\dashinstancescatter.db"

# Connect to the existing database
conn = sqlite3.connect(original_db_path)
cursor = conn.cursor()

# Perform the update operation for 'lclUnitedStates'
cursor.execute("""
    UPDATE transactions
    SET PrimaryCurrencyCode = 'USD'
    WHERE PrimaryCurrencyCode = 'lclUnitedStates'
""")
# Perform the update operation for 'lclIndia'
cursor.execute("""
    UPDATE transactions
    SET PrimaryCurrencyCode = 'INR'
    WHERE PrimaryCurrencyCode = 'lclIndia'
""")

# Commit the changes
conn.commit()
# Close the connection
conn.close()

# Copy the updated database to a new file
new_db_path = r'C:\Users\yashu\Downloads'
shutil.copyfile(original_db_path, new_db_path)

print(f"Updated database has been saved to {new_db_path}")
