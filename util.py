import re


def Get_Inches(height):
    r = re.compile(r"([0-9]+)[-']([0-9]+)")
    m = r.match(height)
    if m == None:
        return float("NaN")
    else:
        return int(m.group(1)) * 12 + float(m.group(2))


def neutralInput():
    while True:
        Neutral = input("Neutral court? (yes/no): ")
        if Neutral not in ("yes", "no", "y", "n"):
            print("Not an appropriate choice.")
        else:
            return Neutral


def GetNeutralValue(num):
    if num == 1 or num == "1":
        return "y"
    return "n"


def GetBooleanValue(str_value):
    if str_value == 1 or str_value == "1":
        return True
    return False
