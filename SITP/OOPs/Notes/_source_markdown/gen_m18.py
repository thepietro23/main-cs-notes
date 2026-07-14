"""Module 18 — Low-Level Design (LLD): diagram generator."""
import viz_style as V
IMG = "../images/"


def d01_approach():
    fig, ax = V.new_canvas()
    V.title(ax, "The LLD interview flow")
    steps = ["Clarify\nrequirements", "Identify\nentities", "Relationships\n+ UML",
             "Apply SOLID\n+ patterns", "Code the\nclasses", "Discuss\nextensions"]
    ys = [80, 66, 52, 38, 24, 10]
    for i, (t, y) in enumerate(zip(steps, ys)):
        c = V.GREEN_F if i in (0, 4) else V.BLUE_F
        e = V.GREEN if i in (0, 4) else V.NAVY
        V.box(ax, 50, y, 40, 10, t, fill=c, edge=e, size=10)
        if i < len(steps) - 1:
            V.arrow(ax, 50, y - 5, 50, ys[i + 1] + 5, color=V.GRAY)
    V.caption(ax, "Always clarify FIRST; never jump straight to code. Talk through each step.")
    V.save(fig, IMG + "m18_01_approach.png")


def d02_parking_classes():
    fig, ax = V.new_canvas()
    V.title(ax, "Parking Lot — class model")
    V.box(ax, 50, 80, 22, 9, "ParkingLot", fill=V.BLUE_F, size=10)
    V.box(ax, 22, 60, 20, 9, "Level", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 22, 42, 20, 9, "ParkingSpot", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.box(ax, 78, 60, 20, 9, "Vehicle", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.box(ax, 78, 42, 22, 9, "Car/Bike/Truck", fill=V.ORANGE_F, edge=V.ORANGE, size=8)
    V.box(ax, 50, 24, 20, 9, "Ticket", fill=V.BLUE_F, size=10)
    V.arrow(ax, 44, 76, 26, 65, color=V.NAVY)
    V.arrow(ax, 22, 55, 22, 47, color=V.NAVY)
    V.arrow(ax, 78, 47, 78, 56, color=V.NAVY, style="-|>")
    V.arrow(ax, 56, 76, 74, 65, color=V.NAVY)
    V.arrow(ax, 40, 40, 46, 29, color=V.GRAY)
    V.note(ax, 15, 30, "Lot has Levels\nhas Spots", color=V.GRAY, size=8)
    V.note(ax, 88, 30, "Vehicle types\n= inheritance", color=V.GRAY, size=8)
    V.caption(ax, "Lot -> Levels -> Spots (composition); Vehicle hierarchy; Ticket on park.")
    V.save(fig, IMG + "m18_02_parking_classes.png")


def d03_parking_strategy():
    fig, ax = V.new_canvas()
    V.title(ax, "Parking: pluggable spot-allocation Strategy")
    V.box(ax, 25, 62, 30, 14, "ParkingLot\n.park(vehicle)", fill=V.BLUE_F, size=10)
    V.box(ax, 72, 76, 30, 9, "NearestSpot", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.box(ax, 72, 62, 30, 9, "RandomSpot", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.box(ax, 72, 48, 30, 9, "CheapestSpot", fill=V.GREEN_F, edge=V.GREEN, size=9)
    for y in (76, 62, 48):
        V.arrow(ax, 40, 62, 57, y, color=V.NAVY, dashed=True)
    V.note(ax, 45, 30, "swap allocation policy without touching ParkingLot (OCP)", color=V.RED, size=10)
    V.caption(ax, "Strategy pattern makes the allocation policy pluggable — Open/Closed in action.")
    V.save(fig, IMG + "m18_03_parking_strategy.png")


def d04_elevator_states():
    fig, ax = V.new_canvas()
    V.title(ax, "Elevator — a State machine")
    V.box(ax, 20, 60, 18, 11, "Idle", fill=V.BLUE_F, size=11)
    V.box(ax, 50, 60, 18, 11, "MovingUp", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 80, 60, 18, 11, "MovingDown", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.arrow(ax, 29, 62, 41, 62, color=V.NAVY)
    V.arrow(ax, 41, 58, 29, 58, color=V.NAVY)
    V.arrow(ax, 59, 62, 71, 62, color=V.NAVY, dashed=True)
    V.note(ax, 50, 40, "requests -> a scheduler picks direction; State drives behaviour", color=V.RED, size=10)
    V.note(ax, 50, 30, "classes: Elevator, Request, Scheduler(Strategy), State", color=V.GRAY, size=10)
    V.caption(ax, "Elevator uses State (Idle/Up/Down) + a Strategy scheduler (SCAN/FCFS).")
    V.save(fig, IMG + "m18_04_elevator_states.png")


def d05_deck_cards():
    fig, ax = V.new_canvas()
    V.title(ax, "Deck of Cards — model")
    V.box(ax, 25, 66, 22, 10, "Suit (Enum)", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.box(ax, 25, 48, 22, 10, "Rank (Enum)", fill=V.ORANGE_F, edge=V.ORANGE, size=10)
    V.box(ax, 60, 57, 20, 10, "Card\n(frozen)", fill=V.GREEN_F, edge=V.GREEN, size=10)
    V.box(ax, 88, 57, 18, 10, "Deck\nshuffle/deal", fill=V.BLUE_F, size=9)
    V.arrow(ax, 36, 64, 50, 59, color=V.NAVY)
    V.arrow(ax, 36, 50, 50, 55, color=V.NAVY)
    V.arrow(ax, 70, 57, 79, 57, color=V.NAVY)
    V.note(ax, 55, 34, "Card = frozen dataclass (Suit, Rank) -> hashable, immutable", color=V.RED, size=10)
    V.note(ax, 55, 26, "Deck holds 52 Cards; shuffle(), deal(n)", color=V.GRAY, size=10)
    V.caption(ax, "Enums for Suit/Rank, a frozen Card value object, a Deck that shuffles/deals.")
    V.save(fig, IMG + "m18_05_deck_cards.png")


def d06_rate_limiter():
    fig, ax = V.new_canvas()
    V.title(ax, "Rate Limiter — Token Bucket")
    V.box(ax, 25, 62, 26, 20, "", fill=V.BLUE_F, edge=V.NAVY)
    V.note(ax, 25, 74, "bucket", color=V.NAVY, bold=True, size=10)
    V.note(ax, 25, 62, "tokens: 3/5", size=11)
    V.note(ax, 25, 52, "refills over time", color=V.GRAY, size=9)
    V.arrow(ax, 40, 64, 55, 64, color=V.GREEN)
    V.box(ax, 70, 72, 24, 9, "token left -> ALLOW", fill=V.GREEN_F, edge=V.GREEN, size=9)
    V.box(ax, 70, 54, 24, 9, "empty -> REJECT", fill=V.RED, tcolor="white", size=9)
    V.note(ax, 50, 30, "each request consumes a token; refill rate caps throughput", color=V.RED, size=10)
    V.caption(ax, "Token bucket: allow while tokens remain, refill at a fixed rate (classic LLD).")
    V.save(fig, IMG + "m18_06_rate_limiter.png")


def d07_patterns_in_lld():
    fig, ax = V.new_canvas()
    V.title(ax, "Patterns that recur in LLD problems")
    rows = [(72, "Strategy", "pluggable policy (parking, scheduling, pricing)"),
            (58, "State", "modes (elevator, order, vending machine)"),
            (44, "Factory", "create by type (vehicles, notifications)"),
            (30, "Observer", "notify (elevator display, stock ticker)"),
            (16, "Singleton", "one manager (lot, logger) — or a module")]
    for y, name, use in rows:
        V.box(ax, 22, y, 24, 10, name, fill=V.BLUE_F, size=11)
        V.note(ax, 74, y, use, size=9)
    V.caption(ax, "Recognising which pattern a sub-problem needs is the core LLD skill.")
    V.save(fig, IMG + "m18_07_patterns_in_lld.png")


def d08_lld_checklist():
    fig, ax = V.new_canvas()
    V.title(ax, "What interviewers score in LLD")
    V.box(ax, 27, 58, 40, 40, "", fill=V.GREEN_F, edge=V.GREEN)
    V.note(ax, 27, 72, "THEY WANT", color=V.GREEN, bold=True, size=12)
    V.note(ax, 27, 58, "clarify reqs\nclean class boundaries\nSOLID + right patterns\nextensible design", size=9)
    V.box(ax, 73, 58, 40, 40, "", fill=V.RED, edge=V.RED)
    V.note(ax, 73, 72, "RED FLAGS", color="white", bold=True, size=12)
    V.note(ax, 73, 58, "jump to code\none giant class\nhard-coded if/elif\nno extensibility", color="white", size=9)
    V.caption(ax, "Communicate, model cleanly, apply principles, and design for change.")
    V.save(fig, IMG + "m18_08_lld_checklist.png")


if __name__ == "__main__":
    for f in [d01_approach, d02_parking_classes, d03_parking_strategy,
              d04_elevator_states, d05_deck_cards, d06_rate_limiter,
              d07_patterns_in_lld, d08_lld_checklist]:
        f()
    print("M18 diagrams done.")
