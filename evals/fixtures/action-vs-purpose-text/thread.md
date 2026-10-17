# Ticket #5120 — Shift export CSV times are wrong (again)

**Customer:** Dana Whitlock, Operations Manager, Harbor Lane Bakery (account HLB-0417)
**Channel:** email · **Status:** open · **Assigned:** you

---

**From:** Dana Whitlock · 2026-09-24 09:12

Hi, since last week's update the "Export shifts (CSV)" file has every start and
end time nine hours early. A 07:00 opening shift shows up as 22:00 the previous
day. We paste this file into payroll every Friday and I had to correct 38 rows
by hand this week. Can you look at this?

---

**From:** Marcus (Support) · 2026-09-24 15:40

Hi Dana, thanks for flagging this. I reproduced it on your account — the export
is writing UTC instead of your location's time zone. Engineering has it logged
and told me the fix will be out by October 3rd. I'll let you know as soon as it
ships.

---

**From:** Dana Whitlock · 2026-10-03 17:05

Any update? Still wrong in today's export.

*(no reply sent)*

---

**From:** Dana Whitlock · 2026-10-17 08:31

It's October 17th and the export is still nine hours off. That's four payroll
runs I've fixed by hand now, and nobody got back to me after the 3rd. This is
the second time this year we've had an export problem (we had a ticket in
March too), and the owner is asking me why we're paying for this.

I need a straight answer on when this gets fixed.

Dana
