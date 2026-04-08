# Statistics to use: 
# xG(30%), xGA(25%), direct matchups(10%), current form (last 5 games)(15%), home/away strength(20%)


xG = 1.77
xGA = 0.99

results = "WDLDWLDLDWLWDDWWDLWWLWLLDWWDWDWWWWDWDW"

# Functions to normalize all the relevant metrics
def normalized_current_form(results):
    last_5 = results[-5:]
    form = list(last_5)
    points = 0
    for outcome in form:
        if outcome == "W":
            points += 3
        elif outcome == "D":
            points += 1
        else:
            points += 0
    return points/15

def normalized_xG(xG):
    return xG/2

def normalized_xGA(xGA):
    return (2-xGA)/2

weighted_xG = normalized_xG(xG)*0.30 # 30%
weighted_current_form = normalized_current_form(results)*0.15 #15%
weighted_xGA = normalized_xGA(xGA)*0.25 # 25%

print(f"xG: {weighted_xG}")
print(f"Current form: {weighted_current_form}")
print(f"xGA: {weighted_xGA}")
