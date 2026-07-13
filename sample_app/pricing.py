def calculate_total(price: float, quantity: int) -> float:
    """Calculate the total price of an order."""
    return price * quantity


def main() -> None:
    total = calculate_total(price=125.50, quantity=2)
    print(f"Order total: ${total:.2f}")


if __name__ == "__main__":
    main()
