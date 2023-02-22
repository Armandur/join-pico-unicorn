import requests
import sys
from datetime import date, datetime
import locale

def getNextDelivery(postalcode: int) -> date:
    url = f"https://portal.postnord.com/api/sendoutarrival/closest?postalCode={postalcode}"

    response = requests.get(url)
    if response.status_code != 200:
        print(f"GET {url} Error {response.status_code}", file=sys.stderr)
        sys.exit(1) 

    json = response.json()
    deliveryDate = json["delivery"]
    
    deliveryDate = deliveryDate.split(" ") # "23", "februari," "2023"
    deliveryDate[1] = deliveryDate[1][:-1] # "februari"
    deliveryDate[0] = int(deliveryDate[0]) # 23
    deliveryDate[2] = int(deliveryDate[2]) # 2023

    sweMonths = {
        "januari"   : 1,
        "februari"  : 2,
        "mars"      : 3,
        "april"     : 4,
        "maj"       : 5,
        "juni"      : 6,
        "juli"      : 7,
        "augusti"   : 8,
        "september" : 9,
        "oktober"   : 10,
        "november"  : 11,
        "december"  : 12
    }

    deliveryDate[1] = sweMonths[deliveryDate[1]] # 2
    deliveryDate = date(deliveryDate[2], deliveryDate[1], deliveryDate[0])

    return deliveryDate

def getCurrentDate() -> date:
    url = "https://google.se"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"GET {url} Error {response.status_code}", file=sys.stderr)
        sys.exit(1) 

    # Wed, 22 Feb 2023 19:03:29 GMT
    # %a, %d %b %Y %H:%M:%S %Z    

    currentDate = datetime.strptime(response.headers["Date"], '%a, %d %b %Y %H:%M:%S %Z').date()
    return currentDate

if __name__ == "__main__":
    postalcode = 87153
    nextDelivery = getNextDelivery(postalcode)
    
    print(f"När kommer posten? {postalcode}")

    if(nextDelivery == getCurrentDate()):
        print("Idag!")
    else:
        locale.setlocale(locale.LC_TIME, "sv_SE")
        print(f"På {nextDelivery.strftime('%A')}")