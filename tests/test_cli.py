import copy
import os
import tempfile
import unittest

from campusflow.cli_views import (
    add_note_view,
    find_ticket,
    format_search_results,
    format_ticket_notes,
    parse_menu_choice,
    prompt_filter,
    prompt_ticket_title,
    search_view,
    understanding_check_view,
    view_notes_view,
)
from campusflow.search import VALID_CATEGORIES


class ScriptedInput:
    def __init__(self, replies):
        self.replies = list(replies)

    def __call__(self, prompt=""):
        if not self.replies:
            raise AssertionError("The program asked for more input than the test supplied.")
        return self.replies.pop(0)


class OutputCollector:

    def __init__(self):
        self.lines = []

    def __call__(self, text=""):
        self.lines.append(text)

    def text(self):
        return "\n".join(self.lines)


def make_ticket(ticket_id, title, category, status, priority, notes=None):
    return {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": "low",
        "affected_users": 1,
        "priority": priority,
        "status": status,
        "assigned_to": "Staff A",
        "notes": notes if notes is not None else [],
    }


def sample_tickets():
    return [
        make_ticket("T001", "Wifi down in library", "Network", "open", "high"),
        make_ticket("T002", "WIFI slow in hostel", "Network", "resolved", "medium"),
        make_ticket("T003", "Laptop wifi adapter broken", "Hardware", "open", "low"),
        make_ticket("T004", "Install Python on lab PCs", "Software", "in_progress", "critical"),
    ]


class TestParseMenuChoice(unittest.TestCase):
    def test_valid_choices(self):
        self.assertEqual(parse_menu_choice("1", 1, 11), 1)
        self.assertEqual(parse_menu_choice(" 11 ", 1, 11), 11)

    def test_invalid_choices_return_none(self):
        for bad in ("", "  ", "0", "12", "-1", "abc", "1.5", "7a", None):
            self.assertIsNone(parse_menu_choice(bad, 1, 11), repr(bad))


class TestPromptFilter(unittest.TestCase):
    def test_blank_means_no_filter(self):
        out = OutputCollector()
        result = prompt_filter("Category", VALID_CATEGORIES, ScriptedInput([""]), out)
        self.assertIsNone(result)

    def test_invalid_option_reprompts_until_valid(self):
        out = OutputCollector()
        fake_input = ScriptedInput(["Banana", "123", "network"])

        result = prompt_filter("Category", VALID_CATEGORIES, fake_input, out)

        self.assertEqual(result, "Network")
        self.assertEqual(fake_input.replies, [])
        self.assertEqual(out.text().count("Invalid category"), 2)


class TestSearchView(unittest.TestCase):
    def setUp(self):
        self.tickets = sample_tickets()
        self.out = OutputCollector()

    def test_combined_filters_through_the_cli(self):
        fake_input = ScriptedInput(["wifi", "Network", "open", "", "n"])

        results = search_view(self.tickets, fake_input, self.out)

        self.assertEqual([t["id"] for t in results], ["T001"])
        self.assertIn("Wifi down in library", self.out.text())
        self.assertNotIn("Laptop wifi adapter broken", self.out.text())

    def test_invalid_filter_reprompts_then_search_runs(self):
        fake_input = ScriptedInput(["wifi", "Banana", "network", "closed", "open", "", "n"])

        results = search_view(self.tickets, fake_input, self.out)

        self.assertEqual([t["id"] for t in results], ["T001"])
        self.assertEqual(fake_input.replies, [])

    def test_all_blank_filters_return_everything(self):
        fake_input = ScriptedInput(["", "", "", "", "n"])
        results = search_view(self.tickets, fake_input, self.out)
        self.assertEqual(len(results), 4)

    def test_no_match_shows_friendly_message(self):
        fake_input = ScriptedInput(["printer", "", "", ""])
        results = search_view(self.tickets, fake_input, self.out)
        self.assertEqual(results, [])
        self.assertIn("No tickets match your search.", self.out.text())

    def test_sort_option_orders_by_priority(self):
        fake_input = ScriptedInput(["", "", "", "", "maybe", "y"])

        results = search_view(self.tickets, fake_input, self.out)

        self.assertEqual([t["id"] for t in results], ["T004", "T001", "T002", "T003"])
        self.assertIn("Please enter y or n.", self.out.text())

    def test_search_view_does_not_modify_tickets(self):
        before = copy.deepcopy(self.tickets)
        search_view(self.tickets, ScriptedInput(["wifi", "", "", "", "y"]), self.out)
        self.assertEqual(self.tickets, before)

    def test_empty_collection_does_not_prompt(self):
        fake_input = ScriptedInput([])  # any input() call would fail the test
        results = search_view([], fake_input, self.out)
        self.assertEqual(results, [])
        self.assertIn("no tickets to search", self.out.text())

    def test_results_show_the_required_columns(self):
        text = format_search_results([self.tickets[0]])
        for expected in ("ID: T001", "Title: Wifi down in library", "Category: Network",
                         "Priority: high", "Status: open", "Assigned to: Staff A"):
            self.assertIn(expected, text)


class TestAddNoteView(unittest.TestCase):
    def setUp(self):
        self.tickets = sample_tickets()
        self.out = OutputCollector()
        self.calls = []

    def fake_add_note(self, ticket_id, author, message):
        self.calls.append((ticket_id, author, message))
        return {"note_id": "N001", "author": author, "message": message}

    def test_successful_note_reports_the_note_id(self):
        fake_input = ScriptedInput(["t001", "Mentor A", "Wi-Fi router reboot attempted"])

        added = add_note_view(self.tickets, self.fake_add_note, fake_input, self.out)

        self.assertTrue(added)
        self.assertEqual(self.calls, [("T001", "Mentor A", "Wi-Fi router reboot attempted")])
        self.assertIn("Note N001 added to T001.", self.out.text())

    def test_rejected_note_shows_message_and_reports_not_added(self):
        def rejecting_add_note(ticket_id, author, message):
            raise ValueError("Resolved tickets cannot receive notes until reopened.")

        fake_input = ScriptedInput(["T002", "Mentor A", "Trying to add a note"])

        added = add_note_view(self.tickets, rejecting_add_note, fake_input, self.out)

        self.assertFalse(added)
        self.assertIn("Note not added: Resolved tickets cannot receive notes", self.out.text())

    def test_unknown_ticket_never_calls_add_note(self):
        fake_input = ScriptedInput(["T999"])

        added = add_note_view(self.tickets, self.fake_add_note, fake_input, self.out)

        self.assertFalse(added)
        self.assertEqual(self.calls, [])
        self.assertIn("Ticket not found", self.out.text())

    def test_missing_business_function_shows_friendly_message(self):
        added = add_note_view(self.tickets, None, ScriptedInput([]), self.out)
        self.assertFalse(added)
        self.assertIn("not available yet", self.out.text())

    def test_no_tickets_does_not_prompt(self):
        added = add_note_view([], self.fake_add_note, ScriptedInput([]), self.out)
        self.assertFalse(added)
        self.assertIn("no tickets", self.out.text())

    def test_view_does_not_change_tickets_when_note_rejected(self):
        def rejecting_add_note(ticket_id, author, message):
            raise ValueError("Message is too short.")

        before = copy.deepcopy(self.tickets)
        add_note_view(
            self.tickets, rejecting_add_note,
            ScriptedInput(["T001", "Mentor A", "no"]), self.out,
        )
        self.assertEqual(self.tickets, before)


class TestViewNotesView(unittest.TestCase):
    def setUp(self):
        self.out = OutputCollector()
        self.notes = [
            {"note_id": "N002", "author": "Mentor B", "message": "Investigating switch ports"},
            {"note_id": "N001", "author": "Mentor A", "message": "Wi-Fi router reboot attempted"},
            {"note_id": "N010", "author": "Mentor A", "message": "Switch replaced on site"},
        ]
        self.tickets = [
            make_ticket("T001", "Wifi down", "Network", "open", "high", self.notes),
            make_ticket("T002", "Printer jam", "Hardware", "resolved", "low", [
                {"note_id": "N001", "author": "Mentor A", "message": "Paper removed from tray"},
            ]),
            make_ticket("T003", "No notes here", "Other", "open", "low"),
        ]

    def test_notes_are_shown_in_note_id_order(self):
        view_notes_view(self.tickets, ScriptedInput(["T001"]), self.out)
        text = self.out.text()
        self.assertLess(text.index("N001"), text.index("N002"))
        self.assertLess(text.index("N002"), text.index("N010"))

    def test_notes_on_resolved_ticket_are_still_visible(self):
        view_notes_view(self.tickets, ScriptedInput(["t002"]), self.out)
        self.assertIn("Paper removed from tray", self.out.text())

    def test_ticket_without_notes_shows_friendly_message(self):
        view_notes_view(self.tickets, ScriptedInput(["T003"]), self.out)
        self.assertIn("has no notes yet", self.out.text())

    def test_old_ticket_without_notes_key_does_not_crash(self):
        old_ticket = make_ticket("T004", "Old ticket", "Other", "open", "low")
        del old_ticket["notes"]
        self.assertIn("has no notes yet", format_ticket_notes(old_ticket))

    def test_unknown_ticket_shows_friendly_message(self):
        result = view_notes_view(self.tickets, ScriptedInput(["T404"]), self.out)
        self.assertIsNone(result)
        self.assertIn("Ticket not found", self.out.text())

    def test_viewing_notes_does_not_modify_tickets(self):
        before = copy.deepcopy(self.tickets)
        view_notes_view(self.tickets, ScriptedInput(["T001"]), self.out)
        self.assertEqual(self.tickets, before)


class TestFindTicket(unittest.TestCase):
    def test_find_ticket_ignores_case_and_spaces(self):
        tickets = sample_tickets()
        self.assertIs(find_ticket(tickets, " t003 "), tickets[2])

    def test_find_ticket_returns_none_when_missing(self):
        self.assertIsNone(find_ticket(sample_tickets(), "T999"))


class TestUnderstandingCheckView(unittest.TestCase):
    def test_check_runs_and_saves_explanations(self):
        replies = [
            "Engineer B",
            "B", "C", "B", "C", "C", "B",
            "2", "Zero tickets would divide by zero so the report returns 0 percent.",
            "3", "Filters use AND so a ticket must match every supplied filter.",
        ]
        out = OutputCollector()

        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "notes.md")
            result = understanding_check_view(ScriptedInput(replies), out, path)
            with open(path, encoding="utf-8") as notes_file:
                saved = notes_file.read()

        self.assertEqual(result["score"], 6)
        self.assertIn("Engineer B", saved)
        self.assertIn("Score: 6/6", saved)
        self.assertIn("Zero tickets would divide by zero", saved)

    def test_blank_label_is_rejected(self):
        replies = [
            "   ", "Engineer B",
            "B", "C", "B", "C", "C", "B",
            "1", "Unassigned tickets are rejected and nothing changes.",
            "2", "Zero tickets must report zero percent safely.",
        ]
        out = OutputCollector()

        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "notes.md")
            understanding_check_view(ScriptedInput(replies), out, path)

        self.assertIn("The label cannot be blank.", out.text())


class TestPromptTicketTitle(unittest.TestCase):
    def test_empty_title_is_rejected_and_prompts_again(self):
        out = OutputCollector()
        fake_input = ScriptedInput(["", "Wifi down in library"])

        title = prompt_ticket_title(fake_input, out)

        self.assertEqual(title, "Wifi down in library")
        self.assertEqual(fake_input.replies, [])
        self.assertIn("The title cannot be empty", out.text())

    def test_spaces_only_title_is_rejected(self):
        out = OutputCollector()
        fake_input = ScriptedInput(["   ", "\t", "Printer jam"])

        title = prompt_ticket_title(fake_input, out)

        self.assertEqual(title, "Printer jam")
        self.assertEqual(out.text().count("The title cannot be empty"), 2)

    def test_program_does_not_continue_until_a_valid_title_is_given(self):
        fake_input = ScriptedInput(["", "", ""])  # never gives a valid title
        with self.assertRaises(AssertionError):
            prompt_ticket_title(fake_input, OutputCollector())

    def test_title_with_numbers_is_still_rejected(self):
        out = OutputCollector()
        fake_input = ScriptedInput(["Lab 3 projector", "Lab projector"])

        title = prompt_ticket_title(fake_input, out)

        self.assertEqual(title, "Lab projector")
        self.assertIn("cannot contain numbers", out.text())

    def test_valid_title_is_trimmed(self):
        self.assertEqual(
            prompt_ticket_title(ScriptedInput(["  Wifi down  "]), OutputCollector()),
            "Wifi down",
        )


class TestNotesViewsWithRealAddNote(unittest.TestCase):

    def setUp(self):
        from campusflow.notes import add_note
        self.tickets = [make_ticket("T001", "Wifi down", "Network", "open", "high")]

        def adapter(ticket_id, author, message):
            ticket = find_ticket(self.tickets, ticket_id)
            if ticket is None:
                raise ValueError("Ticket not found.")
            return add_note(ticket, author, message)

        self.adapter = adapter

    def test_add_then_view_notes_end_to_end(self):
        out = OutputCollector()
        added = add_note_view(
            self.tickets, self.adapter,
            ScriptedInput(["T001", "Mentor A", "Wi-Fi router reboot attempted"]), out,
        )
        self.assertTrue(added)
        self.assertIn("Note N001 added to T001.", out.text())

        out = OutputCollector()
        view_notes_view(self.tickets, ScriptedInput(["T001"]), out)
        self.assertIn("Note ID: N001", out.text())
        self.assertIn("Wi-Fi router reboot attempted", out.text())

    def test_rejected_note_on_resolved_ticket_shows_message(self):
        self.tickets[0]["status"] = "resolved"
        before = copy.deepcopy(self.tickets)
        out = OutputCollector()

        added = add_note_view(
            self.tickets, self.adapter,
            ScriptedInput(["T001", "Mentor A", "This should be rejected"]), out,
        )

        self.assertFalse(added)
        self.assertIn("Note not added:", out.text())
        self.assertEqual(self.tickets, before)


if __name__ == "__main__":
    unittest.main()