#!/usr/bin/env python3
"""
Script to generate sample bill and receipt files for testing
Run this script to create all test files in your current directory
"""

import os

def create_files():
    """Create all sample bill and receipt files"""
    
    files_data = {
        'electricity_bill.txt': '''ELECTRIC COMPANY OF AMERICA
Customer Service: 1-800-ELECTRIC
www.electricamerica.com

ACCOUNT NUMBER: 123456789
SERVICE ADDRESS: 123 Main Street, Anytown, USA 12345
BILLING DATE: February 1, 2024
DUE DATE: February 28, 2024

BILLING PERIOD: January 1 - January 31, 2024

PREVIOUS BALANCE: $0.00
PAYMENTS RECEIVED: $0.00

CURRENT ELECTRIC CHARGES:
Electricity Usage: 850 kWh @ $0.12/kWh = $102.00
Basic Service Charge: $12.50
Environmental Recovery Fee: $3.25
State Tax (6%): $7.07

TOTAL AMOUNT DUE: $124.82

PAYMENT METHODS:
- Online: www.electricamerica.com
- Phone: 1-800-PAY-BILL
- Mail: PO Box 12345, Anytown, USA 12345

VENDOR: Electric Company of America
AMOUNT: $124.82
DATE: 2024-02-01
CATEGORY: Utilities''',

        'water_bill.txt': '''CITY OF ANYTOWN - WATER DEPARTMENT
Municipal Services Division
Phone: (555) 123-WATER

ACCOUNT: W-456789123
SERVICE ADDRESS: 123 Main Street
                Anytown, USA 12345

STATEMENT DATE: February 15, 2024
DUE DATE: March 15, 2024
BILLING PERIOD: December 15, 2023 - February 15, 2024

WATER USAGE SUMMARY:
Current Reading: 1,247,850 gallons
Previous Reading: 1,244,350 gallons
Usage This Period: 3,500 gallons

CHARGES:
Water Service (3,500 gallons): $42.50
Sewer Service: $38.75
Storm Water Management Fee: $8.25
Base Service Fee: $15.00

SUBTOTAL: $104.50
City Tax (3.5%): $3.66

TOTAL AMOUNT DUE: $108.16

VENDOR: City Water Department
AMOUNT: $108.16
DATE: 2024-02-15
CATEGORY: Utilities''',

        'internet_bill.txt': '''COMCAST XFINITY
Bringing You Closer to What You Love
Customer Service: 1-800-XFINITY

ACCOUNT NUMBER: COM-147258369
SERVICE ADDRESS: 123 Main Street, Anytown, USA 12345

STATEMENT PERIOD: February 10 - March 9, 2024
STATEMENT DATE: March 10, 2024
DUE DATE: April 5, 2024

PREVIOUS BALANCE: $89.99
PAYMENT RECEIVED 02/28/24: -$89.99
BALANCE FORWARD: $0.00

CURRENT MONTHLY CHARGES:
Xfinity Internet (200 Mbps): $79.99
Xfinity TV Select: $89.99
xFi Gateway Rental: $15.00
Broadcast TV Fee: $21.30
Regional Sports Fee: $12.95
Taxes, Fees & Other Charges: $24.67

TOTAL CURRENT CHARGES: $243.90
TOTAL AMOUNT DUE: $243.90

VENDOR: Comcast
AMOUNT: $243.90
DATE: 2024-03-10
CATEGORY: Communications''',

        'phone_bill.txt': '''VERIZON WIRELESS
America's Most Reliable Network
Account Services: 1-800-922-0204

WIRELESS ACCOUNT: VZW-987654321
BILLING ADDRESS: 123 Main Street, Anytown, USA 12345

BILL DATE: March 1, 2024
DUE DATE: March 25, 2024
BILLING CYCLE: February 1 - February 29, 2024

ACCOUNT SUMMARY:
Previous Balance: $0.00
Payments/Adjustments: $0.00
Current Charges: $156.78

LINE 1 - (555) 123-4567:
5G Unlimited Plan: $70.00
Device Payment (iPhone): $33.33

LINE 2 - (555) 987-6543:
5G Unlimited Plan: $65.00
Device Payment (Samsung): $29.17

ACCOUNT CHARGES:
Autopay Discount: -$10.00
Taxes and Fees: $19.28

TOTAL AMOUNT DUE: $156.78

VENDOR: Verizon Wireless
AMOUNT: $156.78
DATE: 2024-03-01
CATEGORY: Communications''',

        'gas_bill.txt': '''NATIONAL GRID
Natural Gas Services
Customer Care: 1-800-NATIONAL

ACCOUNT NUMBER: NG-789123456
SERVICE ADDRESS: 123 Main Street
                Anytown, USA 12345

BILL DATE: February 20, 2024
DUE DATE: March 20, 2024
SERVICE PERIOD: January 20 - February 19, 2024

PREVIOUS BALANCE: $0.00
PAYMENTS/CREDITS: $0.00

GAS USAGE:
Current Meter Reading: 8,456 CCF
Previous Meter Reading: 8,411 CCF
Usage This Period: 45 CCF (Therms)

SUPPLY CHARGES:
Gas Supply (45 therms @ $1.15): $51.75
Basic Service Charge: $18.50

DELIVERY CHARGES:
Distribution Service: $23.75
Transportation: $12.40
System Benefits: $2.85

TAXES AND FEES:
State Gross Receipts Tax: $4.50
Local Tax: $2.15

TOTAL AMOUNT DUE: $115.90

VENDOR: National Grid
AMOUNT: $115.90
DATE: 2024-02-20
CATEGORY: Utilities''',

        'credit_card_bill.txt': '''CHASE SAPPHIRE PREFERRED
Member Since: 2019

ACCOUNT NUMBER: ****1234
STATEMENT CLOSING DATE: February 29, 2024
PAYMENT DUE DATE: March 25, 2024

ACCOUNT SUMMARY:
Previous Balance: $1,247.83
Payments: -$1,247.83
Other Credits: -$25.00
Purchases: +$2,156.94
Cash Advances: $0.00
Balance Transfers: $0.00
Fees Charged: $0.00
Interest Charged: $0.00

NEW BALANCE: $2,156.94
MINIMUM PAYMENT DUE: $65.00

PAYMENT INFORMATION:
Credit Limit: $15,000.00
Available Credit: $12,843.06
Cash Advance Limit: $7,500.00

RECENT TRANSACTIONS (Sample):
02/02 Amazon Purchase: $89.99
02/05 Shell Gas Station: $45.67
02/08 Starbucks: $12.45
02/12 Target: $156.78
02/15 Restaurant: $89.34
02/18 Grocery Store: $234.56
02/22 Online Shopping: $198.99
02/25 Pharmacy: $34.67
02/28 Uber: $23.45

VENDOR: Chase Bank
AMOUNT: $2156.94
DATE: 2024-02-29
CATEGORY: Credit Card''',

        'insurance_bill.txt': '''STATE FARM INSURANCE
Like a Good Neighbor, State Farm is There
Agent: John Smith (555) 123-4567

POLICY HOLDER: Jane Doe
POLICY NUMBER: SF-123456789
BILLING ADDRESS: 123 Main Street, Anytown, USA 12345

POLICY PERIOD: March 1, 2024 - September 1, 2024
BILL DATE: February 15, 2024
DUE DATE: February 29, 2024

COVERAGE SUMMARY:
2022 Honda Accord (Vin: 1HGCV1F3XMA123456)
- Liability Coverage: $300,000 / $500,000
- Comprehensive: $500 Deductible
- Collision: $1,000 Deductible
- Uninsured Motorist: $100,000 / $300,000

2019 Toyota Camry (Vin: 4T1B11HK5KU123456)
- Liability Coverage: $300,000 / $500,000  
- Comprehensive: $500 Deductible
- Collision: $1,000 Deductible

PREMIUM BREAKDOWN:
Vehicle 1 Premium: $445.50
Vehicle 2 Premium: $398.75
Multi-Car Discount: -$67.25
Good Driver Discount: -$89.50
Paperless Billing Discount: -$12.50

TOTAL 6-MONTH PREMIUM: $675.00

VENDOR: State Farm
AMOUNT: $675.00
DATE: 2024-02-15
CATEGORY: Insurance''',

        'mortgage_bill.txt': '''WELLS FARGO HOME MORTGAGE
1-800-TO-WELLS | wellsfargo.com/mortgage

LOAN NUMBER: WF-555-8901234
BORROWER: John & Jane Doe
PROPERTY ADDRESS: 123 Main Street, Anytown, USA 12345

STATEMENT DATE: March 1, 2024
DUE DATE: April 1, 2024
BILLING PERIOD: March 2024

PAYMENT BREAKDOWN:
Principal & Interest: $1,847.65
Escrow for Property Tax: $445.83
Escrow for Insurance: $125.67
PMI (Private Mortgage Insurance): $198.50

TOTAL MONTHLY PAYMENT: $2,617.65

LOAN INFORMATION:
Original Loan Amount: $345,000.00
Current Principal Balance: $327,845.92
Interest Rate: 4.25% Fixed
Loan Term: 30 Years
Payment Number: 25 of 360

ESCROW ANALYSIS:
Escrow Balance: $1,247.83
Annual Property Tax: $5,350.00
Annual Insurance: $1,508.00

VENDOR: Wells Fargo
AMOUNT: $2617.65
DATE: 2024-03-01
CATEGORY: Housing''',

        'cable_tv_bill.txt': '''DIRECTV
Entertainment That Inspires
Customer Service: 1-800-DIRECTV

ACCOUNT: DTV-369258147
SERVICE ADDRESS: 123 Main Street
                Anytown, USA 12345

BILL PERIOD: February 25 - March 24, 2024
BILL DATE: March 25, 2024
DUE DATE: April 15, 2024

PREVIOUS BALANCE: $0.00
PAYMENTS/CREDITS: $0.00

MONTHLY SERVICES:
CHOICE Package: $84.99
HD Service: $10.00
DVR Service: $7.00
Regional Sports Networks: $11.99
Additional Receiver: $7.00

EQUIPMENT:
Genie HD DVR Lease: $15.00
Wireless Mini Genie: $7.00

FEES & TAXES:
Broadcast Fee: $12.00
Regional Sports Fee: $13.90
FCC Regulatory Fee: $0.24
State/Local Taxes: $8.95

TOTAL AMOUNT DUE: $178.07

AUTOPAY DISCOUNT AVAILABLE: Save $10/month
Sign up at directv.com/autopay

VENDOR: DirecTV
AMOUNT: $178.07
DATE: 2024-03-25
CATEGORY: Entertainment''',

        'medical_bill.txt': '''ANYTOWN MEDICAL CENTER
Excellence in Healthcare Since 1985
Patient Services: (555) 123-CARE

PATIENT: Jane Doe
PATIENT ID: AMC-789456123
DATE OF SERVICE: February 14, 2024
STATEMENT DATE: March 1, 2024

SERVICE DETAILS:
Provider: Dr. Sarah Johnson, MD
Department: Internal Medicine
Procedure: Annual Physical Examination

CHARGES:
Office Visit - Comprehensive: $285.00
Laboratory Work (Blood Panel): $175.00
EKG Test: $95.00
Vaccination (Flu Shot): $45.00

SUBTOTAL: $600.00

INSURANCE INFORMATION:
Primary Insurance: Blue Cross Blue Shield
Policy Number: BCBS-123456789
Claim Number: BC2024-789456

INSURANCE ADJUSTMENTS:
Insurance Payment: -$480.00
Contractual Adjustment: -$72.00
Patient Responsibility: $48.00

BALANCE DUE: $48.00
DUE DATE: March 31, 2024

PAYMENT OPTIONS:
Online: www.anytownmedical.com/pay
Phone: (555) 123-PAY1
Mail: 456 Healthcare Blvd, Anytown, USA 12345

VENDOR: Anytown Medical Center
AMOUNT: $48.00
DATE: 2024-03-01
CATEGORY: Healthcare''',

        'receipts_sample.txt': '''RECEIPT_001
Walmart Supercenter
123 Main Street, Anytown, USA 12345
Date: 2024-01-15
Time: 14:32:45
Items:
- Milk (1 gallon) - $3.99
- Bread (1 loaf) - $2.49
- Eggs (1 dozen) - $4.29
- Bananas (2 lbs) - $1.98
Subtotal: $12.75
Tax: $0.89
Total: $13.64
Payment: Credit Card
Category: Groceries
---

RECEIPT_002
Shell Gas Station
456 Oak Avenue, Anytown, USA 12345
Date: 2024-01-18
Time: 09:15:22
Items:
- Regular Gasoline (12.5 gallons) - $39.75
Total: $39.75
Payment: Debit Card
Category: Transportation
---

RECEIPT_003
Amazon Purchase
Online Order #112-3456789-1234567
Date: 2024-01-22
Time: 16:45:12
Items:
- Wireless Headphones - $89.99
- Phone Case - $15.99
- USB Cable - $12.99
Subtotal: $118.97
Tax: $9.52
Total: $128.49
Payment: Credit Card
Category: Electronics
---

RECEIPT_004
Starbucks Coffee
789 Pine Street, Anytown, USA 12345
Date: 2024-01-25
Time: 07:30:15
Items:
- Grande Latte - $5.45
- Blueberry Muffin - $3.25
Subtotal: $8.70
Tax: $0.61
Total: $9.31
Payment: Mobile App
Category: Food & Dining
---

RECEIPT_005
Target Store
321 Elm Road, Anytown, USA 12345
Date: 2024-02-02
Time: 11:20:33
Items:
- Laundry Detergent - $8.99
- Paper Towels (6 pack) - $12.49
- Toothpaste - $4.99
- Shampoo - $7.99
Subtotal: $34.46
Tax: $2.76
Total: $37.22
Payment: Credit Card
Category: Household
'''
    }
    
    # Create files
    created_files = []
    for filename, content in files_data.items():
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            created_files.append(filename)
            print(f"✓ Created: {filename}")
        except Exception as e:
            print(f"✗ Error creating {filename}: {e}")
    
    print(f"\nSuccessfully created {len(created_files)} files!")
    print("\nFiles created:")
    for file in created_files:
        print(f"  - {file}")
    
    return created_files

if __name__ == "__main__":
    print("Creating sample bill and receipt files...")
    create_files()
    print("\nAll files have been created in the current directory.")
    print("You can now use these files to test your receipt/bill processing system!")