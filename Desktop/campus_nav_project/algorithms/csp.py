"""
Constraint Satisfaction Problem (CSP) solvers.

1) N-Queens: the classic textbook CSP - place N queens on an NxN board so that
   no two queens attack each other (no shared row, column, or diagonal).
   Solved with backtracking search + constraint checking, exactly as taught
   in the AI course.

2) Classroom / time-slot booking: a more "applied" CSP relevant to the campus
   navigation project - assign each course a (room, time-slot) pair such that
   no room/slot combination is double-booked. Same backtracking pattern as
   N-Queens, just with a different constraint definition.
"""


def solve_nqueens(n):
    solution = [-1] * n          # solution[row] = column of the queen in that row
    stats = {"calls": 0}
    steps = []

    def safe(row, col):
        for r in range(row):
            c = solution[r]
            if c == col or abs(c - col) == abs(r - row):
                return False
        return True

    def backtrack(row):
        stats["calls"] += 1
        if row == n:
            return True
        for col in range(n):
            if safe(row, col):
                solution[row] = col
                steps.append({"row": row, "col": col, "action": "place"})
                if backtrack(row + 1):
                    return True
                steps.append({"row": row, "col": col, "action": "remove"})
                solution[row] = -1
        return False

    found = backtrack(0)
    return {
        "found": found,
        "solution": solution if found else [],
        "n": n,
        "backtrack_calls": stats["calls"],
        "steps": steps,
    }


def solve_room_booking(bookings, rooms, slots):
    """
    bookings: list like [{"course": "CSE316"}, {"course": "CSE311"}, ...]
    rooms:    list of room names, e.g. ["E-103", "E-105"]
    slots:    list of time-slot labels, e.g. ["9:00-10:30", "10:30-12:00"]

    Assigns each course a unique (room, slot) pair via backtracking.
    """
    assignment = {}
    used = set()

    def backtrack(index):
        if index == len(bookings):
            return True
        course = bookings[index]["course"]
        for room in rooms:
            for slot in slots:
                key = (room, slot)
                if key not in used:
                    used.add(key)
                    assignment[course] = {"room": room, "slot": slot}
                    if backtrack(index + 1):
                        return True
                    used.discard(key)
                    del assignment[course]
        return False

    success = backtrack(0)
    return {"success": success, "assignment": assignment}
