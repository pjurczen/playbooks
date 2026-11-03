# Non-brittle tests — Avoid / Prefer

Read before the first test of a task. One pair per rule that a shape shows better than a sentence. Every parameter, return and field carries its type, in the
test and in the helpers it calls.

## B1 — Through the caller's surface

```python
# Avoid: the test knows a private method and its return shape
def test_discount() -> None:
    assert Pricing()._compute_discount(Decimal("120"), "GOLD") == Decimal("12")


# Prefer: the test calls what a caller calls and reads what a caller reads
def gold_customer() -> Customer: ...
def order_for(customer: Customer, total: Decimal) -> Order: ...


def test_gold_customer_pays_ten_percent_less() -> None:
    order: Order = order_for(gold_customer(), total=Decimal("120"))

    invoice: Invoice = Pricing().invoice(order)

    assert invoice.total == Decimal("108")
```

## D2 — A fake with a contract test

```python
# Avoid: a fake that answers what this test needs and nothing else
class FakeInventory:
    def reserve(self, sku: str, qty: int) -> bool:
        return True


# Prefer: one fake for all tests, held to the real contract by one shared test
class InMemoryInventory:
    def __init__(self) -> None:
        self.stock: dict[str, int] = {}

    def stock_up(self, sku: str, qty: int) -> None:
        self.stock[sku] = self.stock.get(sku, 0) + qty

    def reserve(self, sku: str, qty: int) -> None:
        if self.stock.get(sku, 0) < qty:
            raise OutOfStock(sku)
        self.stock[sku] -= qty


@pytest.mark.parametrize("inventory", [InMemoryInventory(), SqlInventory(test_db)])
def test_reserving_more_than_stock_fails(inventory: Inventory) -> None:
    inventory.stock_up("A1", qty=1)

    with pytest.raises(OutOfStock):
        inventory.reserve("A1", qty=2)
```

## R2 — Named values, used twice

```python
# Avoid: literals the reader must match by eye
def test_late_fee() -> None:
    assert fee_for(days_late=12) == Decimal("6.0")


# Prefer: the value appears where it is arranged and where it is expected
def test_each_late_day_costs_half_a_unit() -> None:
    days_late: int = 12
    expected_fee: Decimal = days_late * Decimal("0.5")

    assert fee_for(days_late=days_late) == expected_fee
```

## R3 and R4 — Creation methods from small named parts

```python
# Avoid: one builder with every field
customer: Customer = make_customer("Ada", "ada@x.io", "GOLD", "DE", True, None, 3)


# Prefer: the situation is the name, the parts are small and composable
def german_address() -> Address: ...
def gold_customer(address: Address | None = None) -> Customer: ...


customer: Customer = gold_customer(address=german_address())
```

## R5 — The act line shows only what matters

```python
# Avoid: arguments the behaviour ignores clutter the act line
result: CheckoutResult = checkout(cart, payment=card("4111"), shipping=standard(), coupon=None, locale="en")


# Prefer: an action helper hides the ignored arguments
def checkout_with_coupon(cart: Cart, coupon: Coupon | None) -> CheckoutResult:
    return checkout(cart, payment=card("4111"), shipping=standard(), coupon=coupon, locale="en")


result: CheckoutResult = checkout_with_coupon(cart, coupon=None)
```

## A3 — Time under control

```python
# Avoid: the test depends on the wall clock
def test_token_expires() -> None:
    token: Token = issue_token()
    time.sleep(2)
    assert token.expired()


# Prefer: time is an input
class FixedClock:
    def __init__(self, at: datetime) -> None:
        self.now: datetime = at

    def advance(self, seconds: int) -> None:
        self.now += timedelta(seconds=seconds)


def test_token_expires_after_its_lifetime() -> None:
    clock: FixedClock = FixedClock(at=datetime(2026, 1, 1, 10, 0))
    token: Token = issue_token(clock, lifetime_seconds=60)

    clock.advance(seconds=61)

    assert token.expired(clock)
```
