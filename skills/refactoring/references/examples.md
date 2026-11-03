# Refactoring — one Before / After per move

Read before the first pass. Each pair shows one move of the pass loop on a small piece of Python. Every parameter, return and field carries its type.

## Compose: a public method as named steps

```python
# Before
def invoice(self, order: Order) -> Invoice:
    lines: list[Line] = []
    for item in order.items:
        price: Decimal = item.unit_price * item.qty
        if order.customer.tier == "GOLD":
            price = price * Decimal("0.9")
        lines.append(Line(item.sku, price))
    total: Decimal = sum((line.amount for line in lines), Decimal(0))
    return Invoice(order.id, lines, total)


# After
def invoice(self, order: Order) -> Invoice:
    lines: list[Line] = self._priced_lines(order)
    return Invoice(order.id, lines, self._total(lines))
```

## Clean the steps: inline the pass-through

```python
# Before
def _total(self, lines: list[Line]) -> Decimal:
    return self._sum_amounts(lines)


def _sum_amounts(self, lines: list[Line]) -> Decimal:
    return sum((line.amount for line in lines), Decimal(0))


# After
def _total(self, lines: list[Line]) -> Decimal:
    return sum((line.amount for line in lines), Decimal(0))
```

## Move behaviour to its data

```python
# Before: the service decides with the customer's data
def _discounted(self, price: Decimal, customer: Customer) -> Decimal:
    return price * Decimal("0.9") if customer.tier == "GOLD" else price


# After: the customer answers
@dataclass(frozen=True)
class Customer:
    name: str
    tier: str

    def discounted(self, price: Decimal) -> Decimal:
        return price * Decimal("0.9") if self.tier == "GOLD" else price
```

## Replace a chain with a query

```python
# Before: the caller walks the object graph
if order.customer.address.country == "DE":
    ...


# After: the nearest owned object answers, one level per type
if order.ships_within("DE"):
    ...


@dataclass(frozen=True)
class Order:
    id: str
    customer: Customer
    items: tuple[Item, ...]

    def ships_within(self, country: str) -> bool:
        return self.customer.lives_in(country)
```

## First-class collection

```python
# Before: a raw list is queried in three places
open_orders: list[Order] = [o for o in orders if o.status == "OPEN"]
has_open: bool = any(o.status == "OPEN" for o in orders)


# After: the collection owns its queries
class Orders:
    def __init__(self, orders: Iterable[Order]) -> None:
        self._orders: list[Order] = list(orders)

    def open(self) -> "Orders":
        return Orders(o for o in self._orders if o.status == "OPEN")

    def any_open(self) -> bool:
        return bool(self.open()._orders)
```

## Hidden concept: a value type for a parameter clump

```python
# Before: the same three parameters travel together
def book(self, street: str, city: str, country: str) -> Booking: ...
def deliver_to(self, street: str, city: str, country: str) -> Delivery: ...


# After: the clump is a concept with its own behaviour
@dataclass(frozen=True)
class Address:
    street: str
    city: str
    country: str

    def is_domestic(self) -> bool:
        return self.country == "DE"


def book(self, address: Address) -> Booking: ...
```
