def recommend_festival(products):
    if not products:
        return "No strong festival recommendation available."

    text = " ".join(products).lower()

    if any(word in text for word in ["kurta", "saree", "lehenga", "ethnic", "dress"]):
        return "Recommended for Navratri / Diwali / Wedding season."

    if any(word in text for word in ["diya", "light", "lamp", "decoration", "rangoli"]):
        return "Recommended for Diwali."

    if any(word in text for word in ["gift", "hamper", "box", "chocolate"]):
        return "Recommended for Diwali / Raksha Bandhan / New Year."

    if any(word in text for word in ["color", "gulal", "pichkari"]):
        return "Recommended for Holi."

    if any(word in text for word in ["rakhi", "bracelet"]):
        return "Recommended for Raksha Bandhan."

    return "General seasonal demand."