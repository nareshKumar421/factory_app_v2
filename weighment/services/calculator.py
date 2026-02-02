# weighment/services/calculator.py

def calculate_net_weight(gross_weight, tare_weight):
    if gross_weight is None or tare_weight is None:
        return 0
    if gross_weight < tare_weight:
        raise ValueError("Gross weight cannot be less than tare weight")
    return gross_weight - tare_weight
