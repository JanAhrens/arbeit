import unittest
from arbeitcli import *

class ArbeitcliTest(unittest.TestCase):
    def setUp(self):
        self.empty_date = {
            "breaks": [],
            "start": None,
            "end": None,
            "comment": None
        }

    def test_find_date_returns_empty(self):
        self.assertEqual(find_date({}, "2014-01-01"), self.empty_date)

    def test_find_date_find_match(self):
        self.assertEqual(
            find_date({'dates': {'2014-01-01': 'found'}}, '2014-01-01'),
            'found'
        )

    def test_hours_to_minutes(self):
        self.assertEqual(
            hours_to_minutes('13:24'),
            13 * 60 + 24
        )

        self.assertEqual(
            hours_to_minutes('1:10'),
            1 * 60 + 10
        )

    def test_minutes_to_hours(self):
        self.assertEqual(
            minutes_to_hours(13 * 60 + 24),
            '13:24'
        )

        self.assertEqual(
            minutes_to_hours(23),
            '00:23'
        )

    def test_calculate_working_hours_aborts_when_not_complete(self):
        self.assertEqual(
            calculate_working_hours({'start': 0,  'end': None}),
            0
        )

        self.assertEqual(
            calculate_working_hours({'start': None, 'end': 0}),
            0
        )

    def test_calculate_working_hours_succeeds(self):
        self.assertEqual(
            calculate_working_hours({'start': '13:00', 'end': '14:00', 'breaks': []}),
            60
        )

        self.assertEqual(
            calculate_working_hours({'start': '12:00', 'end': '15:00', 'breaks': [{'start': '12:30', 'end': '12:52'}]}),
            158
        )

if __name__ == '__main__':
    unittest.main()
