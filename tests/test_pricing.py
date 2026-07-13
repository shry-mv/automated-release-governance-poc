from sample_app.pricing import calculate_total, main


def test_calculate_total() -> None:
    result = calculate_total(price=125.50, quantity=2)

    assert result == 251.00


def test_main_prints_order_total(capsys) -> None:
    main()

    captured = capsys.readouterr()

    assert captured.out == "Order total: $251.00\n"
