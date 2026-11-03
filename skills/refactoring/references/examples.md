# Refactoring — one Before / After per move

Read before the first pass. Each pair shows one move of the pass loop on a small piece of Python.

## Compose: a public method as named steps

```python
# Before
def invoice(self, order):
    lines = []
    for item in order.items:
        price = item.unit_price * item.qty
        if order.customer.tier == "GOLD":
            price = price * 0.9
        lines.append(Line(item.sku, price))
    total = sum(l.amount for l in lines)
    return Invoice(order.id, lines, total)

# After
def invoice(self, order):
    lines = self._priced_lines(order)
    return Invoice(order.id, lines, self._total(lines))
```

## Clean the steps: inline the pass-through

```python
# Before
def _total(self, lines):
    return self._sum_amounts(lines)

def _sum_amounts(self, lines):
    return sum(l.amount for l in lines)

# After
def _total(self, lines):
    return sum(l.amount for l in lines)
```

## Move behaviour to its data

```python
# Before: the service decides with the customer's data
def _discounted(self, price, customer):
    return price * 0.9 if customer.tier == "GOLD" else price

# After: the customer answers
class Customer:
    def discounted(self, price):
        return price * 0.9 if self.tier == "GOLD" else price
```

## Replace a chain with a query

```python
# Before: the caller walks the object graph
if order.customer.address.country == "DE":
    ...

# After: the nearest owned object answers, one level per type
if order.ships_within("DE"):
    ...

class Order:
    def ships_within(self, country):
        return self.customer.lives_in(country)
```

## First-class collection

```python
# Before: a raw list is queried in three places
open_orders = [o for o in orders if o.status == "OPEN"]
has_open = any(o.status == "OPEN" for o in orders)

# After: the collection owns its queries
class Orders:
    def __init__(self, orders): self._orders = list(orders)
    def open(self): return Orders(o for o in self._orders if o.status == "OPEN")
    def any_open(self): return bool(self.open())
```

## Hidden concept: a value type for a parameter clump

```python
# Before: the same three parameters travel together
def book(self, street, city, country): ...
def deliver_to(self, street, city, country): ...

# After: the clump is a concept with its own behaviour
@dataclass(frozen=True)
class Address:
    street: str
    city: str
    country: str
    def is_domestic(self): return self.country == "DE"

def book(self, address): ...
```
