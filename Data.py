import re
import requests
import pdfplumber
from io import BytesIO
import csv
import json
from getpass import getpass


def getData():
    listOfStringToIgnore = [
        "University Surplus and Salvage",
        "To search this document press the 'Ctrl' key",
        "Property Surplus Listing",
        "and the letter 'f' key at the same time.",
        """Property for auction posted under the hyperlink icon called "Vehicles and Online Auctions" on the main""",
        "University Surplus and Salvage Department web page.",
        "https://fbs.admin.utah.edu/surplus/",
        "(Please call to verify date)",
        "Prices and availablity of surplus property subject to verification and change without notice.",
        "Property sold without hard drives.",
        "*Federal agencies, state agencies, university departments, and public education institutions may purchase property",
        "as soon as it is displayed in the University Surplus and Salvage (Surplus) warehouse. The public, university",
        "employees and students are welcome to purchase property beginning on the public sale date or public date listed",
        """on property for sale. Most property has a fifteen day government surplus cycle. The "Public Date" column in this""",
        "document is the estimated date (computer generated) on which the public may purchase the property listed above.",
        "The actual public sale date is on the price stickers of property for sale at the University Surplus and Salvage",
        """Department. There are times when the actual public sale date on a price sticker and the "public date" in this""",
        """document vary. Please contact Surplus to verify the actual "public date" of an item for sale. The government surplus""",
        """cycle is estimated to have expired if there is no date in the "Public Date" column.""",
        "When an item becomes available for sale to the public, if only one person is present (lined up at the public entrance",
        "door) for the item when the doors open for business, it will be sold at its marked price. If two or more people are",
        "present (lined up at the public entrance door) when the doors open for business, the item will be auctioned to the",
        "highest bidder with the price marked as the minimum acceptable bid. When an item is to be auctioned to the",
        "highest bidder, customers, arriving after the doors open for business, on the public sale date, will not be allowed to",
        "participate in the auction. The item is reserved for those present (lined up at the public entrance door) when the",
        "doors open for business. If no one is present (lined up at the public entrance door) when the doors open for",
        "business, the item will be sold on a “first come, first serve” basis. If the Public Sale Date is marked for a date the",
        "University Surplus and Salvage Department is closed, the Public Sale Date becomes the next open business day.",
        "Bid items will have a bid document explaining the terms and conditions for those items.",
        "Surplus reserves the right to waive, extend, change or restart the government surplus cycle on property placed for",
        """sale by Surplus. If property is dated to a shorter or longer government surplus cycle, the official "public date" or""",
        '"public sale date" is on the price sticker. Some items listed above may be sold through an online auction site or',
        """through a bid process and are not available for purchase on the "Public Date" above. Items marked bid and""",
        "property listed for sale online are available through the terms and conditions posted for those items. Property may",
        "be removed from sale without notice. Prices of property for sale may change without notice. Property may be",
        """placed for bid or auction without notice. The "Public Date" or "Public Sale Date" may change on property for sale""",
        "without notice.",
    ]
    firstDatePattern = r"(\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{1,2} [APap][Mm])"
    itemPattern = (
        r"(\d+\s\d+\s\d+)\s(\d+)\s(.*?)\s(\$[\d.]+)(?:\s(\d{1,2}/\d{1,2}/\d{4}))?"
    )

    def sanitizePage(pages, outputPages):
        for page in pages:
            # Extract the text from the current page
            text = page.extract_text()

            # Split the text into lines
            lines = text.split("\n")

            for line in lines:
                if re.search(firstDatePattern, line):
                    continue

                if line in listOfStringToIgnore:
                    continue

                outputPages.append(line)

        return outputPages

    ap_url = "https://fbs.admin.utah.edu/download/Surplus/listing.pdf"
    response = requests.get(ap_url)

    # ap = download_file(ap_url)
    csv_data = []
    category = ""
    type = ""

    if response.status_code == 200:
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            totalPages = []
            sanitizePage(pdf.pages, totalPages)

            for i, line in enumerate(totalPages):
                # print(line)

                next_line = totalPages[i + 1] if i + 1 < len(totalPages) else None
                next_next_line = totalPages[i + 2] if i + 2 < len(totalPages) else None

                if (
                    next_line != "Surplus Number Qty Description Price Public Date*"
                    and next_next_line
                    == "Surplus Number Qty Description Price Public Date*"
                    and not re.search(itemPattern, line)
                ):
                    category = line
                    # print(f"Category: {category}")

                elif next_line == "Surplus Number Qty Description Price Public Date*":
                    type = line
                    # print(f"Type: {type}")

                elif re.search(itemPattern, line):
                    match = re.search(itemPattern, line)
                    surplus_number, qty, description, price, public_date = (
                        match.groups()
                    )
                    # print(f"Item: {line}")
                    csv_data.append(
                        [
                            surplus_number,
                            qty,
                            description,
                            price[1:] if price and price[0] == "$" else price,
                            public_date if public_date else "null",
                            type,
                            category,
                        ]
                    )
    json_data = []
    for row in csv_data:
        json_data.append(
            {
                "SurplusNumber": row[0],
                "Qty": row[1],
                "Description": row[2],
                "Price": row[3],
                "PublicDate": row[4],
                "Type": row[5],
                "Category": row[6],
            }
        )

    # Write the data to the JSON file
    with open("output.json", "w") as jsonfile:
        json.dump(json_data, jsonfile, indent=2)
        # print(text)

    return json_data
    
    