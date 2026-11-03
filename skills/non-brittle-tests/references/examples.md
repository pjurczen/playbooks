# Non-brittle tests — Avoid / Prefer

Read before the first test of a task. One pair per rule that a shape shows better than a sentence.

## B1 — Through the caller's surface

```python
# Avoid: the test knows a private method and its return shape
def test_discount():
    assert Pricing()._compute_discount(120, "GOLD") == 12

# Prefer: the test calls what a caller calls and reads what a caller reads
def test_gold_customer_pays_ten_percent_less():
    order = order_for(gold_customer(), total=120)

    invoice = Pricing().invoice(order)

    assert invoice.total == 108
```

## D2 — A fake with a contract test

```python
# Avoid: a fake that answers what this test needs and nothing else
class FakeInventory:
    def reserve(self, sku, qty): return True

# Prefer: one fake for all tests, held to the real contract by one shared test
class InMemoryInventory:
    def __init__(self): self.stock = {}
    def reserve(self, sku, qty):
        if self.stock.get(sku, 0) < qty: raise OutOfStock(sku)
        self.stock[sku] -= qty

@pytest.mark.parametrize("inventory", [InMemoryInventory(), SqlInventory(test_db)])
def test_reserving_more_than_stock_fails(inventory):
    inventory.stock_up("A1", qty=1)

    with pytest.raises(OutOfStock):
        inventory.reserve("A1", qty=2)
```

## R2 — Named values, used twice

```python
# Avoid: literals the reader must match by eye
def test_late_fee():
    assert fee_for(days_late=12) == 6.0

# Prefer: the value appears where it is arranged and where it is expected
def test_each_late_day_costs_half_a_unit():
    days_late = 12
    expected_fee = days_late * 0.5

    assert fee_for(days_late=days_late) == expected_fee
```

## R3 and R4 — Creation methods from small named parts

```python
# Avoid: one builder with every field
customer = make_customer("Ada", "ada@x.io", "GOLD", "DE", True, None, 3)

# Prefer: the situation is the name, the parts are small and composable
customer = gold_customer(address=german_address())
```

## R5 — The act line shows only what matters

```python
# Avoid: arguments the behaviour ignores clutter the act line
result = checkout(cart, payment=card("4111"), shipping=standard(), coupon=None, locale="en")

# Prefer: an action helper hides the ignored arguments
result = checkout_with_coupon(cart, coupon=None)
```

## A3 — Time under control

```python
# Avoid: the test depends on the wall clock
def test_token_expires():
    token = issue_token()
    time.sleep(2)
    assert token.expired()

# Prefer: time is an input
def test_token_expires_after_its_lifetime():
    clock = FixedClock(at="2026-01-01T10:00")
    token = issue_token(clock, lifetime_seconds=60)

    clock.advance(seconds=61)

    assert token.expired(clock)
```
