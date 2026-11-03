# Non-brittle tests — the rules, with the explanation and an Avoid/Prefer example for each

The full explanation and an example for every rule in the non-brittle-tests skill, by rule ID (B, D, R, A). Read this file before the first test of a task. The
measure behind every rule is the four-change check: a test is non-brittle when it stays unchanged through a pure refactoring, an unrelated compatible feature, a
bug fix elsewhere and an internal redesign, and changes only when the behaviour it specifies changes. Each explanation says which of those changes the Avoid
version breaks on. The examples are Python with pytest; every parameter, return and field carries its type, in the test and in the helpers it calls.

## Behaviour

### B1 — Define the behaviour sentence (Given–When–Then) before the test shape; one behaviour per test

The sentence is the specification; the test is its executable form. Written first, it decides the name, the arrangement and the single assertion, and it stops
the test from growing a second behaviour on the way. A test written from the code instead of from a sentence mirrors the code's structure and breaks with it on
the next redesign. Use ZOMBIES (Zero, One, Many, Boundaries, Interface, Exceptional, Simple) to choose which sentences protect a real distinction. *Breaks on:*
internal redesign.

```python
# Avoid: the test is named after the method and asserts whatever the code happens to do
def test_apply_discount() -> None:
    pricing: Pricing = Pricing()
    assert pricing.apply_discount(Decimal("100"), "GOLD") == Decimal("90")
    assert pricing.apply_discount(Decimal("100"), "SILVER") == Decimal("95")
    assert pricing.apply_discount(Decimal("100"), None) == Decimal("100")


# Prefer: one sentence, one test; given a gold customer, when an order of 100 is priced, then the invoice is 90
def test_gold_customer_pays_ten_percent_less() -> None:
    order: Order = order_for(gold_customer(), total=Decimal("100"))

    invoice: Invoice = Pricing().invoice(order)

    assert invoice.total == Decimal("90")


def test_customer_without_tier_pays_the_full_price() -> None:
    order: Order = order_for(customer_without_tier(), total=Decimal("100"))

    invoice: Invoice = Pricing().invoice(order)

    assert invoice.total == Decimal("100")
```

### B2 — Test through the owned public API, the way a real caller does

A caller sees the public surface: the constructor, the public methods, the returned values and the observable state. A test that reaches a private method or a
private field binds itself to the implementation, so every refactoring that moves, renames or inlines that private part breaks the test while the behaviour is
intact. The public surface is the one thing a refactoring promises to keep. *Breaks on:* pure refactoring, internal redesign.

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

### B3 — Choose the smallest scope that still proves the behaviour; never mock the infrastructure under test

Scope is how much real code runs between the act line and the assertion. Too wide, and the test fails for reasons the sentence does not name and takes long to
run; too narrow, and the test mocks away the very thing it claims to prove. When the behaviour is "the repository persists an order", the database is under test
and a mock of it proves nothing. When the behaviour is "a gold customer pays less", the repository is not under test and a real in-memory one is enough. *Breaks
on:* internal redesign (too narrow), unrelated feature (too wide).

```python
# Avoid: the behaviour is persistence, and the store is mocked away
def test_order_is_persisted() -> None:
    store: MagicMock = MagicMock()
    OrderRepository(store).save(an_order())
    store.insert.assert_called_once()


# Prefer: the smallest scope that proves persistence runs the real store on a test database
def test_saved_order_can_be_read_back(test_db: Database) -> None:
    repository: OrderRepository = OrderRepository(test_db)
    order: Order = an_order()

    repository.save(order)

    assert repository.find(order.number) == order
```

## Doubles

### D1 — Prefer real collaborators: real → stub → fake → mock. Replace only awkward boundaries

A real collaborator proves the integration for free and never drifts from production. Replace a collaborator only when it is awkward: slow, nondeterministic,
external or costly to set up. Even then, take the simplest double that works: a stub that returns an input, a fake with real behaviour in memory, and a mock
only when the interaction itself is the behaviour (D4). A mock of an internal collaborator fixes the conversation between two classes, so any redesign of that
conversation breaks the test with the behaviour unchanged. *Breaks on:* pure refactoring, internal redesign.

```python
# Avoid: internal collaborators mocked "to isolate the unit"
def test_invoice_total() -> None:
    pricing: MagicMock = MagicMock()
    pricing.discounted.return_value = Decimal("90")
    tax: MagicMock = MagicMock()
    tax.for_amount.return_value = Decimal("9")
    invoice: Invoice = Invoicing(pricing, tax).invoice(an_order())
    assert invoice.total == Decimal("99")


# Prefer: the real pricing and tax rules run; only the external rate source is a stub
def test_invoice_total_includes_tax_on_the_discounted_amount() -> None:
    rates: RateSource = fixed_rates(tax_rate=Decimal("0.10"))
    invoicing: Invoicing = Invoicing(Pricing(), Tax(rates))
    order: Order = order_for(gold_customer(), total=Decimal("100"))

    invoice: Invoice = invoicing.invoice(order)

    assert invoice.total == Decimal("99")
```

### D2 — Stubs supply inputs only; never stub the logic under test

A stub answers a question the code asks on the way to the behaviour: a rate, a lookup, a clock. The moment a stub returns the result the test asserts, the test
proves only that the stub was wired, and the real logic can be wrong without a failure. A stub of the logic under test also breaks on every bug fix in that
logic, because the stub still returns the old answer. *Breaks on:* bug fix elsewhere; proves nothing meanwhile.

```python
# Avoid: the stub returns the answer the test then asserts
def test_shipping_fee() -> None:
    calculator: MagicMock = MagicMock()
    calculator.fee_for.return_value = Decimal("5")
    checkout: Checkout = Checkout(calculator)
    assert checkout.shipping_fee(a_cart()) == Decimal("5")


# Prefer: the stub supplies an input, the real calculator computes the answer
def test_a_cart_over_fifty_ships_free() -> None:
    rates: ShippingRates = flat_rate(Decimal("5"), free_above=Decimal("50"))
    checkout: Checkout = Checkout(FeeCalculator(rates))
    cart: Cart = cart_worth(Decimal("60"))

    fee: Decimal = checkout.shipping_fee(cart)

    assert fee == Decimal("0")
```

### D3 — Fakes honour the real contract and get a shared contract test

A fake is a working implementation in memory. It is only as trustworthy as its fidelity to the real thing: a fake that accepts what the real store rejects lets
a defect through every test that uses it. One contract test, parameterized over the fake and the real implementation, keeps the two in step, so a change to the
real contract fails in one place instead of silently diverging. *Breaks on:* unrelated feature that changes the contract; proves too much meanwhile.

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

### D4 — Verify an interaction only when the interaction is the behaviour

"Called with these arguments" is a fact about the implementation, not about the outcome. Two correct implementations can make different calls, and an
interaction assertion fails one of them. Assert the state or the returned value instead. The exception is a behaviour that *is* an interaction: an email was
sent, an event was published, a payment was captured. There, the outgoing call is the observable outcome, and the double that records it is the right place to
look. *Breaks on:* pure refactoring, internal redesign.

```python
# Avoid: the assertion is about the call, and the discount is never checked
def test_discount_applied() -> None:
    pricing: MagicMock = MagicMock()
    Invoicing(pricing).invoice(an_order())
    pricing.discounted.assert_called_once()


# Prefer: the outcome is the assertion
def test_gold_customer_pays_ten_percent_less() -> None:
    invoice: Invoice = Invoicing(Pricing()).invoice(order_for(gold_customer(), total=Decimal("100")))

    assert invoice.total == Decimal("90")


# Fine: sending the mail is the behaviour, so the recorded interaction is the outcome
def test_a_paid_order_sends_one_receipt() -> None:
    mailer: RecordingMailer = RecordingMailer()
    Receipts(mailer).send_for(paid_order())

    assert mailer.sent == [receipt_for(paid_order())]
```

## Readability

### R1 — Behaviour names, one behaviour, Arrange–Act–Assert separated by blank lines

The name is the sentence; a reader should know what failed from the name alone. One behaviour per test means one reason to fail, so a red test points at one
thing. The three blocks, separated by blank lines, let the reader find the act line and the assertion without reading the setup. *Breaks on:* any change,
because a test with two behaviours fails for either and the name explains neither.

```python
# Avoid
def test_order() -> None:
    order: Order = Order(customer=Customer("Ada", "GOLD"), lines=[Line("A1", 2, Decimal("10"))])
    assert order.total() == Decimal("18")
    order.cancel()
    assert order.is_cancelled()


# Prefer
def test_gold_customer_total_includes_the_tier_discount() -> None:
    order: Order = order_for(gold_customer(), lines=[line("A1", qty=2, unit_price=Decimal("10"))])

    total: Decimal = order.total()

    assert total == Decimal("18")


def test_a_cancelled_order_reports_itself_cancelled() -> None:
    order: Order = an_order()

    order.cancel()

    assert order.is_cancelled()
```

### R2 — Every relevant value is a named variable, used to arrange and to expect

A literal that appears in the arrangement and again, transformed, in the assertion forces the reader to recompute the relation by eye. A named value, used in
both places, states the relation once and survives a change of the number. *Breaks on:* none directly; it is what makes a failure readable.

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

### R3 — Build test objects with creation methods named after the situation

A constructor call with every field shows the reader seven values of which one matters. A creation method named after the situation (`gold_customer()`,
`overdue_invoice()`) states the one thing that matters and hides the rest with sane defaults. When a field is added to the type, one creation method changes
instead of every test. *Breaks on:* unrelated feature (a new field), without creation methods.

```python
# Avoid: one builder with every field
customer: Customer = make_customer("Ada", "ada@x.io", "GOLD", "DE", True, None, 3)


# Prefer: the situation is the name
def gold_customer() -> Customer:
    return Customer(name="Ada", email="ada@x.io", tier="GOLD", country="DE", active=True, referrer=None, orders=3)


customer: Customer = gold_customer()
```

### R4 — Compose inputs from small named parts; about three parameters per helper

A helper with many parameters becomes a second constructor and hides which argument changed. Small parts that compose
(`gold_customer(address=german_address())`) keep each name meaningful and let a test state exactly the variation it needs. *Breaks on:* readability only; a long
argument list hides the variation that matters.

```python
# Avoid: one helper with every knob
customer: Customer = customer_with("GOLD", "DE", "Berlin", "10115", True, 3)


# Prefer: the parts are small and composable
def german_address(city: str = "Berlin") -> Address: ...
def gold_customer(address: Address | None = None, active: bool = True) -> Customer: ...


customer: Customer = gold_customer(address=german_address())
```

### R5 — Action helpers hide arguments the behaviour ignores

The act line should show the inputs the sentence mentions and nothing else. Arguments the behaviour ignores, such as a default payment method in a test about
coupons, belong in an action helper named after what the test does. *Breaks on:* unrelated feature that adds a parameter: every act line changes instead of one
helper.

```python
# Avoid: arguments the behaviour ignores clutter the act line
result: CheckoutResult = checkout(cart, payment=card("4111"), shipping=standard(), coupon=None, locale="en")


# Prefer: an action helper hides the ignored arguments
def checkout_with_coupon(cart: Cart, coupon: Coupon | None) -> CheckoutResult:
    return checkout(cart, payment=card("4111"), shipping=standard(), coupon=coupon, locale="en")


result: CheckoutResult = checkout_with_coupon(cart, coupon=None)
```

### R6 — Name stub, fake and setup steps after the situation they create

A setup line that configures a double should read as a fact about the world ("the rate source has a ten percent tax rate"), not as mechanics
(`rates.get.return_value = ...`). Named setup steps make the arrangement part of the sentence and keep the double's mechanics in one place. *Breaks on:*
internal redesign of the double's interface, without named steps.

```python
# Avoid
rates: MagicMock = MagicMock()
rates.get.return_value = Decimal("0.10")
rates.get.side_effect = None


# Prefer
rates: RateSource = fixed_rates(tax_rate=Decimal("0.10"))
```

### R7 — No logic in tests; parameterize only rows of the same behaviour

A loop, a condition or a computed expectation in a test is code that can be wrong and that nobody tests. A test states inputs and expected outputs as plain
values. Parameterization is fine when every row is the same sentence with different values; it is wrong when the rows need an `if` to know what to assert.
*Breaks on:* bug fix elsewhere, when the computed expectation duplicates the production formula.

```python
# Avoid: the expectation recomputes the production rule and the loop hides which case fails
def test_fees() -> None:
    for days in range(0, 30):
        assert fee_for(days_late=days) == (Decimal(days) * Decimal("0.5") if days > 0 else Decimal(0))


# Prefer: rows of the same behaviour, plain values
@pytest.mark.parametrize("days_late, expected_fee", [(0, Decimal("0")), (1, Decimal("0.5")), (12, Decimal("6.0"))])
def test_each_late_day_costs_half_a_unit(days_late: int, expected_fee: Decimal) -> None:
    assert fee_for(days_late=days_late) == expected_fee
```

### R8 — DAMP over premature DRY; keep inline what the test is about

Descriptive and meaningful phrases beat deduplication in tests: a reader should understand a test without opening three helpers. Extract what is noise (creation
of irrelevant objects, ignored arguments) and keep inline what the sentence is about (the value that varies, the act, the assertion). A helper that hides the
assertion hides the behaviour. *Breaks on:* readability; a failure in a shared helper is a failure nobody can place.

```python
# Avoid: the assertion is hidden in a helper, and the test says nothing
def test_gold_discount() -> None:
    assert_invoice_total_for_tier("GOLD", Decimal("90"))


# Prefer: the noise is extracted, the behaviour is inline
def test_gold_customer_pays_ten_percent_less() -> None:
    order: Order = order_for(gold_customer(), total=Decimal("100"))

    invoice: Invoice = Pricing().invoice(order)

    assert invoice.total == Decimal("90")
```

## Assertions

### A1 — Assert behaviour, not representation

A behaviour is a value a caller can use or a state a caller can observe. A representation is how the code stores it: the order of keys in a dict, the class of
an intermediate object, a string that happens to be produced on the way. Asserting on representation binds the test to one implementation of the same behaviour.
*Breaks on:* pure refactoring, internal redesign.

```python
# Avoid: the internal representation is the test surface
def test_cart_lines() -> None:
    cart: Cart = cart_with(line("A1", qty=2), line("B2", qty=1))
    assert cart._lines == {"A1": 2, "B2": 1}


# Prefer: what a caller can observe
def test_a_cart_reports_the_quantity_of_each_item() -> None:
    cart: Cart = cart_with(line("A1", qty=2), line("B2", qty=1))

    assert cart.quantity_of("A1") == 2
    assert cart.quantity_of("B2") == 1
```

### A2 — Assert only what the behaviour promises

An assertion on something the sentence does not mention (the exact timestamp, the full object, an unrelated field) makes the test fail for a change the
behaviour allows. Compare the promised part, and let the rest vary. *Breaks on:* unrelated feature, bug fix elsewhere.

```python
# Avoid: the whole object is compared, timestamp and all
def test_receipt() -> None:
    receipt: Receipt = Receipts().for_order(paid_order())
    assert receipt == Receipt(number="R-1", total=Decimal("99"), issued_at=datetime.now(), footer="Thank you")


# Prefer: the promise is the total and the order number
def test_a_receipt_carries_the_order_number_and_its_total() -> None:
    order: Order = paid_order()

    receipt: Receipt = Receipts().for_order(order)

    assert receipt.number == order.number
    assert receipt.total == order.total()
```

### A3 — Control time, randomness, I/O, shared state and order

A test that reads the wall clock, draws a random value, touches the network or depends on another test's leftovers fails for reasons the sentence does not name,
and the usual response, a retry or a sleep, hides the uncontrolled input instead of removing it. Make time an input, seed or inject randomness, replace I/O at
the boundary (D1) and give each test its own state. *Breaks on:* nothing in the code and everything in the environment, which is worse.

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
