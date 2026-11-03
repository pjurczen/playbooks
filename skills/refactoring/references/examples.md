# Software design — the rules, with the explanation and a full example for each

The complete Avoid/Prefer example for every rule the refactoring skill applies, by rule ID (M1–T9). Read this file before the first pass of a refactoring and
when reviewing a design change.

Rules for how methods and types read. Apply them to code you write or change, not as a refactoring of untouched code. They keep methods flat, named and
single-purpose, which also removes deep nesting and complicated boolean expressions. The rule line is binding; the examples illustrate it, so do not copy their
shape where it does not fit. Favour simplicity (KISS, YAGNI, a single level of abstraction) over SOLID and design patterns; apply those only where they solve a
problem you actually have and they reduce complexity rather than increase it. Refactor only code that tests cover; if they do not, write tests that pin today's
behaviour first. The examples are Python; every parameter, return and field carries its type.

## Method shape

### M1 — One level of abstraction per method

A method is a module, the smallest after a variable (then class, package, module, application): it groups what belongs together (high cohesion, low coupling).
Read it from the outside in: the upper steps say *what* happens in domain language, each level down reveals more of *how*. Name each step after a
human-understandable intention, not after low-level mechanics, even before the concept has a type of its own. A step returns at most one result for the next
step; building a value and performing I/O with it are separate steps. Separate an orchestrator's steps with blank lines. When private steps pile up in one
class, move them into a domain type (T1, T2). *Prevents:* mixed abstraction levels, long method.

```python
# Avoid
def process(self, orders: Orders) -> None:
    invoices: Invoices = self.printer.print(orders)
    for order in orders:
        invoices.line_for(order.number)
    for order in orders:
        self.gateway.submit(order.number, self.repository.read_version(order.number))


# Prefer
def process(self, orders: Orders) -> None:
    invoices: Invoices = self.printer.print(orders)

    self._check_every_order_invoiced(orders, invoices)

    self._submit_each(orders)
```

### M2 — At most two nesting levels

Leave early with guard clauses instead of nesting. *(also a linter rule)* *Prevents:* deeply nested control flow.

```python
# Avoid
def reserve_lines(self, order: Order) -> None:
    if order.is_open():
        if order.has_lines():
            for line in order.lines:
                self._reserve(line)


# Prefer
def reserve_lines(self, order: Order) -> None:
    if order.is_closed() or order.is_empty():
        return
    for line in order.lines:
        self._reserve(line)
```

### M3 — One calculation per line

Extract an explaining variable, declared right before its first use. No nested calls: an argument is a variable, a plain value or a simple accessor, never a
call that computes, converts or does I/O; `f(g(h(x)))` becomes named steps. Wrapping a named value (`ArchiveId(value)`) is fine. A call to a query without
arguments whose name states the value it returns reads like a variable and may stay an argument (`order.submitted_at(self._submitted_now())`); a call with
arguments, a chain, or a gateway or repository call stays a named variable. A simple accessor is one attribute on something the method holds, never a chain.
Never move a computation that runs only conditionally (behind `and`/`or`, in a branch) into a variable before it: it would then run when it did not before.
Lines that only build one value (a converted domain value, a request, a command) for the rest of a method are a step of their own when they sit below the level
of the rest: several intermediate values, or details the method's name does not speak about. This holds in every method, private steps included. Extract them
into a query named after that value (M1) or a creation method on the value's type (T3). A single read-and-convert pair on the same level as its use may stay
inline. The receiving domain type keeps taking the domain type, never the raw value it is built from. *Prevents:* dense expressions, distant temporaries, hidden
I/O, conversion pipelines in an orchestrator.

```python
# Avoid
def close(self, orders: Orders, customer: Customer, total: Decimal, documents: Documents) -> ArchiveId:
    numbers: OrderNumbers = OrderNumbers.from_orders(orders)
    self._archive(orders)
    self._invoice(customer, numbers, self.pricing.discounted(total, customer.discount()))
    return self.archive_gateway.store(self.pdf_gateway.merge(documents))


# Prefer
def close(self, orders: Orders, customer: Customer, total: Decimal, documents: Documents) -> ArchiveId:
    self._archive(orders)

    numbers: OrderNumbers = OrderNumbers.from_orders(orders)
    discounted_total: Decimal = self.pricing.discounted(total, customer.discount())
    self._invoice(customer, numbers, discounted_total)

    merged: MergedDocument = self.pdf_gateway.merge(documents)
    archive_id: ArchiveId = self.archive_gateway.store(merged)
    return archive_id
```

```python
# Avoid — a conversion pipeline in an orchestrator, one level below its neighbours
def confirm(self, order: Order) -> None:
    now: datetime = self.clock.now()
    submitted_at: SubmittedAt = SubmittedAt.of(now)
    order.submitted_at(submitted_at)
    order.confirm()


# Prefer — a query named after the value reads like a variable; Order keeps taking the domain type
def confirm(self, order: Order) -> None:
    order.submitted_at(self._submitted_now())
    order.confirm()

def _submitted_now(self) -> SubmittedAt:
    now: datetime = self.clock.now()
    return SubmittedAt.of(now)
```

```python
# Avoid — a private step that builds a request and uses it
def _is_blocked(self, reference: CustomerReference) -> bool:
    customer_number: CustomerNumber = reference.customer_number
    today: date = self.clock.today()
    request: ReadCustomerRequest = ReadCustomerRequest(customer_number, today)
    customer: Customer = self.customer_gateway.read(request)
    return customer.is_blocked()


# Prefer — building the request is a step inside the step
def _is_blocked(self, reference: CustomerReference) -> bool:
    request: ReadCustomerRequest = self._create_read_customer_request(reference)
    customer: Customer = self.customer_gateway.read(request)
    return customer.is_blocked()

def _create_read_customer_request(self, reference: CustomerReference) -> ReadCustomerRequest:
    customer_number: CustomerNumber = reference.customer_number
    today: date = self.clock.today()
    return ReadCustomerRequest(customer_number, today)


# Fine — one read-and-convert pair on the same level as its use stays inline
def _refresh_address(self, order_number: OrderNumber) -> None:
    version: Version = self._read_version(order_number)
    common_version: CommonVersion = version.to_common_version()
    self.address_gateway.refresh(order_number, common_version)
```

### M4 — One-line conditional expressions only

A conditional expression fits on one line and chooses between two simple values (`"paid" if order.is_paid() else "open"`); otherwise use `if`/`else` or a named
variable or method. *Prevents:* unreadable multi-line conditionals.

```python
# Avoid
def document_for(self, order: Order) -> Document:
    return (self.printer.print(order)
            if order.is_printable()
            else self.printer.empty_document())


# Prefer
def document_for(self, order: Order) -> Document:
    if order.is_printable():
        return self.printer.print(order)
    return self.printer.empty_document()
```

### M5 — Name magic values

A number or string whose meaning is not obvious becomes a named constant, enum or explaining variable. `0`/`1` as loop bounds and log or user-facing texts stay
inline. *(also a linter rule)* *Prevents:* magic number, magic string.

```python
# Avoid
if len(order.lines) > 50:
    ...


# Prefer
MAX_LINES_PER_PARCEL: Final[int] = 50

if len(order.lines) > MAX_LINES_PER_PARCEL:
    ...
```

### M6 — Queries don't change state

A method that answers a question (`is_…`, `has_…`, `get_…`, `validate_…`) changes no state. If both are needed, split it into a query and a command and let the
caller call both. *Prevents:* hidden side effect.

```python
# Avoid
def is_valid(self, order: Order) -> bool:
    if order.is_empty():
        order.mark_invalid()
        return False
    return True


# Prefer
if order.is_empty():
    order.mark_invalid()
```

### M7 — Compute in the narrowest scope

Declare a value inside the branch that uses it, after the guards that may make it unnecessary. A value computed before an `if` or an early `return` that leaves
it unused costs I/O, may raise on a path that never needed it, and makes the reader look for a use that is not there. When a refactoring moves such a call into
its branch, the skipped work and failures on the other paths are a behaviour change: say so. *Prevents:* wasted work, misleading data flow.

```python
# Avoid
def send_receipt(self, order: Order) -> None:
    customer: Customer = self.customers.read(order.customer_id)
    if order.is_paid():
        self.mailer.send_receipt(customer, order)


# Prefer
def send_receipt(self, order: Order) -> None:
    if order.is_paid():
        customer: Customer = self.customers.read(order.customer_id)
        self.mailer.send_receipt(customer, order)
```

### M8 — No pass-through methods

A method whose body only forwards to one other call, with the same arguments, adds a name but no concept: the reader jumps one level deeper to find nothing.
Inline it. Keep a wrapper only when its name states a domain concept the callee does not express, or when it hides arguments the callers should not assemble. A
framework decorator (`@transactional`, `@traced`, `@retry`) justifies a wrapper only where the framework actually applies it; a decorator that works through a
proxy or an interceptor does nothing on a private method or on a call from inside the same object. Check every private method after an extraction: did it become
a pass-through? *Prevents:* middle-man methods, lazy methods, decorators that silently do nothing.

```python
# Avoid
def _store(self, documents: Documents) -> Archive:
    merged: MergedDocument = self._merge(documents)
    return self.archive_gateway.store(merged)

@traced                                              # private, called from inside: the span never starts
def _merge(self, documents: Documents) -> MergedDocument:
    return self.pdf_gateway.merge(documents)


# Prefer
def _store(self, documents: Documents) -> Archive:
    merged: MergedDocument = self.pdf_gateway.merge(documents)
    return self.archive_gateway.store(merged)
```

## Conditions

### C1 — Affirmative, domain-named predicates

Ask the positive question in domain language (`is_leaf()`, not `not has_children()`); never negate a negation. *Prevents:* negative conditions.

```python
# Avoid
if not customer.is_not_active() and not order.has_lines():
    ...


# Prefer
if customer.is_active() and order.is_empty():
    ...
```

### C2 — Name compound conditions

A compound boolean expression becomes a predicate method that names the intention. A condition that builds an object and checks it, or negates a call result, is
compound too. *Prevents:* complicated boolean expression.

```python
# Avoid
if request.is_print_required() and orders:
    ...
if not credit_rule(customer, today).is_satisfied_by(order):
    ...


# Prefer
if self._should_print(orders, request):
    ...
if self._exceeds_credit_limit(order):
    ...

@staticmethod
def _should_print(orders: Orders, request: PrintRequest) -> bool:
    return request.is_print_required() and not orders.is_empty()
```

### C3 — No boolean parameters

Use two methods, an enum or a named constant. Pass the domain type, not the boolean unwrapped from it. *Prevents:* flag argument.

```python
# Avoid
self._print_invoices(orders, request.is_print_required())
create_file(path, True)


# Prefer
self._print_invoices(orders, request)
create_read_only_file(path)
```

### C4 — The caller decides whether an optional step runs

A step whose input can legitimately be missing does not take it as `None` only to return early; the caller skips it. Checks for invalid input or preconditions
stay in the method as guard clauses (M2, C5). *Prevents:* hidden no-op branch, nullable parameter.

```python
# Avoid
def send_confirmation(self, order: Order, confirmation: Confirmation | None) -> None:
    if confirmation is None:
        return
    self.mailer.send(order, confirmation)


# Prefer
if confirmation is not None:
    self.send_confirmation(order, confirmation)
```

### C5 — Name checks that only raise

A call made only for the exception it may raise gets a name that says so: `ensure_x_or_raise`. *Prevents:* hidden check.

```python
# Avoid
for order in orders:
    invoices.line_for(order.number)


# Prefer
self._ensure_every_order_invoiced_or_raise(orders, invoices)
```

## Comprehensions, maybe-values and collections

### S1 — One loop, one result

A loop that yields several results becomes one named method per result. Exception: keep one loop when each extra pass is expensive (for example an external call
per element), with a comment saying why. *Prevents:* loop doing too much.

```python
# Avoid
open_orders: list[Order] = []
total: Decimal = Decimal(0)
for order in orders:
    if order.is_open():
        open_orders.append(order)
    total = total + order.total


# Prefer
open_orders: Orders = self._open_orders(orders)
total: Decimal = self._total_of(orders)
```

### S2 — Collect, don't fill from outside

Build a collection with a comprehension or a constructor, not with `append` inside a loop; flatten nested collections with a nested comprehension or `chain`;
combine results with `extend`. The same holds for methods: no method returning `None` that fills a collection or object passed in; return the result.
*Prevents:* collecting parameter, output parameter.

```python
# Avoid
for customer in customers:
    all_orders.extend(customer.orders)


# Prefer
orders: list[Order] = [order for customer in customers for order in customer.orders]
all_orders.extend(orders)
```

### S3 — Filter and map before the side effect

A `for` loop performs only the final side effect, where no comprehension fits; the selection and the conversion happen before it, in a named query or a
comprehension. Do not hide a condition and a lookup inside the loop body. *Prevents:* logic hidden in a loop.

```python
# Avoid
for order in orders:
    if order.is_open():
        self.gateway.submit(order.number, self.repository.read_version(order.number))


# Prefer
for order in orders.open():
    self._submit(order)
```

### S4 — One operation per line, one call per step

Put each step of a pipeline on its own line. Each selection or conversion is one call or one named function; no multi-clause comprehensions, no lambdas stored
in variables, no inline constructors inside the expression: name a method instead. A lambda body follows M3 too: if it needs more than one call, extract a
method and pass it. A guard that only raises may be written as one `if` line; it is a check written as a pipeline step. *Prevents:* anonymous logic.

```python
# Avoid
to_line: Callable[[Order], InvoiceLine] = lambda order: InvoiceLine(order.number, order.total)
return [to_line(order) for order in orders]


# Prefer
return [self._to_invoice_line(order) for order in orders]


# Fine: a guard that only raises
if (reason := order.blocking_reason()) is not None:
    raise order_blocked(order.number, reason)
```

### S5 — Readable maybe-values

Return `T | None` for a value that may be absent; never store or pass a maybe-value where an overload or a caller-side guard says it plainly (C4). Handle `None`
once, at the top, with a guard, and then use the value as its type. Chain conversions of a present value in a pipeline of single calls, whatever its length;
unwrap with a guard only when a step needs logic (a condition, a negation, more than one call). Never test for `None` and then keep working through `None`-aware
steps anyway. *Prevents:* unreadable maybe-chains, nullable parameters.

```python
# Avoid
address: Address | None = order.delivery_address()
if address is not None and address.zip and not address.zip.isspace():
    region: Region | None = self.regions.of(address.zip)
    if region is not None:
        return region.carrier
return self._default_carrier()


# Prefer: a guard at the top, then the value as its type
address: Address | None = order.delivery_address()
if address is None or address.zip.is_blank():
    return self._default_carrier()
region: Region = self.regions.of(address.zip)
return region.carrier
```

### S6 — Telling loop and comprehension variable names

Name loop and comprehension variables after what they hold (`order`, not `o`). The form of the comprehension (line breaks, parentheses) is left to the
formatter. *(also a linter rule)* *Prevents:* cryptic comprehensions.

```python
# Avoid
[o for o in orders if o.is_from(customer)]


# Prefer
[order for order in orders if order.is_from(customer)]
```

## Types and responsibilities

### T1 — Value types for clumps, tiny types for values

Parameters or primitives that travel together become a frozen dataclass with a domain name; domain values become tiny types. Two or more methods taking the same
parameters reveal a concept the code does not name yet: wrap them in a dataclass and move the behaviour that uses them into it. Start such a type private in the
module that needs it; make it public only once it carries behaviour or is used elsewhere, that is, it is a real domain concept, not just a parameter container.
*Prevents:* data clump, long parameter list, primitive obsession, hidden domain concepts.

```python
# Avoid
def ship(self, number: OrderNumber, street: str, zip_code: str, city: str) -> None: ...


# Prefer
@dataclass(frozen=True)
class ShippingAddress:
    street: Street
    zip_code: ZipCode
    city: City


def ship(self, number: OrderNumber, address: ShippingAddress) -> None: ...
```

### T2 — Move behaviour to the data it uses; no anemic domain model

Domain objects carry their behaviour, services only orchestrate. A helper that only uses one parameter's data moves to that parameter's type as a domain method.
After every extraction (M1), check each private method for a better home (Emerging Design): find the state it really uses, wrap that state in a domain class if
none exists yet, move the method there as public and drop parameters it no longer needs. Never move it across a layer boundary or into a class it must not
depend on. *Prevents:* feature envy, anemic domain model.

```python
# Avoid (in OrderService)
def total(self, order: Order) -> Decimal:
    return sum((line.price for line in order.lines), Decimal(0))


# Prefer (in Order)
def total(self) -> Decimal:
    return sum((line.price for line in self.lines), Decimal(0))
```

### T3 — Creation methods for conversions

A conversion between domain types becomes a class method on the target type, replacing every copy. It returns exactly its own type and takes domain types only;
DTO or entity conversion stays in a mapper. Merge copies only when their callers change for the same reason; code that is equal by coincidence stays duplicated,
or the merged version soon grows flags. When every caller builds a factory's arguments the same way, give the factory one named creation method per purpose
(`new_cancellation_invoice(order)`, not `new_invoice(order, CANCELLATION, …)`). A creation step that needs I/O (reading the clock, calling a gateway) stays a
private query in the orchestrating service (`_submitted_now()`, see M3); a separate factory class only once several callers assemble the same value (T7).
*Prevents:* duplicated conversion, layer leak, premature deduplication, argument assembly at every call site.

```python
# Avoid
numbers: OrderNumbers = OrderNumbers({order.number for order in orders})


# Prefer
numbers: OrderNumbers = OrderNumbers.from_orders(orders)


@dataclass(frozen=True)
class OrderNumbers:
    values: frozenset[OrderNumber]

    @classmethod
    def from_orders(cls, orders: Orders) -> "OrderNumbers":
        return cls(frozenset(order.number for order in orders))
```

### T4 — No temporary fields

A field that is valid only after another command has been called: the class's lifecycle is not the same as the field's. It works as a hidden side channel to
pass data between methods, and the caller may not be aware of it. Instead, calculate a value in one method and pass it as a parameter to another. *Prevents:*
temporary field.

```python
# Avoid
class InvoiceService:
    _total: Decimal

    def invoice(self, order: Order) -> None:
        self._calculate_total(order)
        self._print(order, self._total)


# Prefer
class InvoiceService:
    def invoice(self, order: Order) -> None:
        total: Decimal = order.total()
        self._print(order, total)
```

### T5 — Composition over inheritance

Inherit only for polymorphic behaviour, where the subclass overrides something and is used through the parent. To reuse code, hold the other class as a field.
*Prevents:* unnecessary inheritance, deep hierarchies, refused bequest.

```python
# Avoid
class InvoicePrinter(PdfRenderer):
    def print(self, invoice: Invoice) -> None:
        self.render(invoice.to_document())


# Prefer
class InvoicePrinter:
    def __init__(self, renderer: PdfRenderer) -> None:
        self._renderer: PdfRenderer = renderer

    def print(self, invoice: Invoice) -> None:
        self._renderer.render(invoice.to_document())
```

### T6 — Polymorphism over type switches, only when it pays off

Keep a `match` or an `if` cascade until polymorphism is clearly simpler; it must be justified, because it adds complexity too. Only a `match` or `if` cascade on
a type that repeats across methods and selects real strategies becomes polymorphism: an enum with behaviour, a protocol with one class per case, or a dict of
strategies. A single mapping `match` stays. *Prevents:* simulated polymorphic behaviour, over-engineering.

```python
# Avoid (repeated in fee(), delivery_days(), label())
match shipping_type:
    case ShippingType.STANDARD:
        return base
    case ShippingType.EXPRESS:
        return base * EXPRESS_FACTOR


# Prefer
return shipping_method.fee(base)


class ShippingMethod(Enum):
    STANDARD = "standard"
    EXPRESS = "express"

    def fee(self, base: Decimal) -> Decimal:
        return base * EXPRESS_FACTOR if self is ShippingMethod.EXPRESS else base
```

### T7 — No speculative abstractions

No protocol, abstract class, parameter or configuration without a second use today. A protocol with one implementation is right only where it crosses a layer
boundary (a port implemented by an adapter). In general, this applies to software design within a layer and does not touch architectural styles like hexagonal
architecture. *Prevents:* speculative generality, lazy class.

```python
# Avoid (one implementation, same layer)
class DiscountPolicy(Protocol):
    def discount_for(self, customer: Customer) -> Decimal: ...

class DiscountPolicyImpl:
    def discount_for(self, customer: Customer) -> Decimal: ...


# Prefer
class DiscountPolicy:
    def discount_for(self, customer: Customer) -> Decimal: ...
```

### T8 — Ask the nearest object (Law of Demeter)

A method calls methods only on what it holds: its fields, its parameters, its local variables and objects it creates. It never calls a method on the result of
another call. Every chain `a.b().c()` exposes how `a` is built, so a change inside `a` ripples to every caller; inside an argument list it also forces the
formatter to break the call apart. Fluent pipelines (comprehensions, builders) are the exception. Unwrapping a tiny type (`.value`) is reserved for adapters and
mappers towards a foreign API; inside domain and application code, overload the callee for the tiny type (`creator(editor)`, not
`creator(task.editor().value)`).

- **Type you own** (also a private dataclass): give the nearest object a query or command named after the concept the caller needs, and let each type delegate
  one level down. An explaining variable alone would only name the chain.
- **Type you cannot change** (another module's API, generated or library DTOs, framework records): assign the reached value to an explaining variable named
  after the concept, right before its use (M3). That is the accepted fallback.

*Prevents:* message chains, inappropriate intimacy, exposed internals, wrapped argument lists.

```python
# Avoid
valid_from: date = contract.id_attributes().validity().valid_from()
order.content().set_discount(discount)
shipping.send(request.customer().address())            # DTO from another module


# Prefer — owned types answer themselves (Contract → IdAttributes → Validity)
valid_from: date = contract.valid_from()
order.set_discount(discount)


# Prefer — foreign DTO: name the reached value, then use it
customer: CustomerDto = request.customer()
delivery_address: AddressDto = customer.address()
shipping.send(delivery_address)
```

### T9 — First-class collections

A collection of domain values that the code queries becomes a domain type wrapping it, named after the concept, and the queries move into it as methods named
after their intention. Callers ask the collection instead of iterating over a raw `list` or `set`. Reuse an existing wrapper before creating one; create it
where the collection enters the code you own (a gateway, repository or factory result) and pass the wrapper on. A raw collection stays only where nothing is
asked of it beyond iterating or passing it on. Name the collection after the type it wraps (`OrderHeaders` for `OrderHeader`), not after a broader concept. A
collection that crosses a port or public method as a domain concept (an event's content, a request's items) is a first-class collection too, even if nobody
queries it. Before writing a query over a collection, look for an existing first-class collection of its element type and add the method there. *Prevents:*
primitive obsession for collections, the same query repeated in several services, data clumps around a collection.

```python
# Avoid (in OrderService)
orders: list[Order] = self.order_gateway.read_orders(customer_number)
open_order_numbers: list[OrderNumber] = [
    order.number for order in orders
    if order.customer_number == customer_number and order.is_open()
]
if len(open_order_numbers) > 1:
    log.warning("Several open orders for %s", customer_number)
return open_order_numbers[0] if open_order_numbers else None


# Prefer (Orders wraps the list, the gateway returns it)
orders: Orders = self.order_gateway.read_orders(customer_number)
open_orders: Orders = orders.open_orders_of(customer_number)
if open_orders.has_several():
    log.warning("Several open orders for %s", customer_number)
return open_orders.first_number()


class Orders:
    def __init__(self, orders: Iterable[Order]) -> None:
        self._orders: list[Order] = list(orders)

    def open_orders_of(self, customer_number: CustomerNumber) -> "Orders":
        return Orders(order for order in self._orders if order.customer_number == customer_number and order.is_open())

    def has_several(self) -> bool:
        return len(self._orders) > 1

    def first_number(self) -> OrderNumber | None:
        return self._orders[0].number if self._orders else None
```
