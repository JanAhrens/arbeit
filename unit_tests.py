import unittest
from freezegun import freeze_time
import arbeitcli
from datetime import date

class ArbeitcliTest(unittest.TestCase):
    def setUp(self):
        self.empty_date = {
            "breaks": [],
            "start": None,
            "end": None,
            "comment": None
        }

    def test_find_date_returns_empty(self):
        self.assertEqual(arbeitcli.find_date({}, "2014-01-01"), self.empty_date)

    def test_find_date_find_match(self):
        self.assertEqual(
            arbeitcli.find_date({'dates': {'2014-01-01': 'found'}}, '2014-01-01'),
            'found'
        )

    def test_hours_to_minutes(self):
        self.assertEqual(
            arbeitcli.hours_to_minutes('13:24'),
            13 * 60 + 24
        )

        self.assertEqual(
            arbeitcli.hours_to_minutes('1:10'),
            1 * 60 + 10
        )

    def test_minutes_to_hours(self):
        self.assertEqual(
            arbeitcli.minutes_to_hours(13 * 60 + 24),
            '13:24'
        )

        self.assertEqual(
            arbeitcli.minutes_to_hours(23),
            '00:23'
        )

    def test_calculate_working_hours_aborts_when_not_complete(self):
        self.assertEqual(
            arbeitcli.calculate_working_hours({'start': 0,  'end': None}),
            0
        )

        self.assertEqual(
            arbeitcli.calculate_working_hours({'start': None, 'end': 0}),
            0
        )

    def test_calculate_working_hours_succeeds(self):
        self.assertEqual(
            arbeitcli.calculate_working_hours({'start': '13:00', 'end': '14:00', 'breaks': []}),
            60
        )

        self.assertEqual(
            arbeitcli.calculate_working_hours({'start': '12:00', 'end': '15:00', 'breaks': [{'start': '12:30', 'end': '12:52'}]}),
            158
        )

    def test_show_diff(self):
        self.assertEqual(
            arbeitcli.show_diff(7 * 60 + 30, 8 * 60),
            "07:30 (%s)" % arbeitcli.colored('-00:30', 'yellow')
        )

        self.assertEqual(
            arbeitcli.show_diff(8 * 60 + 12, 8 * 60),
            '08:12 (%s)' % arbeitcli.colored('00:12', 'green')
        )

    @freeze_time('2012-12-12 11:12:00Z', tz_offset=1)
    def test_now(self):
        self.assertEqual(arbeitcli.now(), '12:12')

    @freeze_time('2012-12-12 10:00:00Z', tz_offset=1)
    def test_replace_today(self):
        db = {'dates': {'2012-12-12': 'BEFORE'}}
        arbeitcli.replace_today(db, 'AFTER')
        self.assertEqual(db, {'dates': {'2012-12-12': 'AFTER'}})

    def test_days_in_calendar_week(self):
        days = arbeitcli.days_in_calendar_week(2, 2012)
        self.assertEqual(days, [
            date(2012, 1, 9),
            date(2012, 1, 10),
            date(2012, 1, 11),
            date(2012, 1, 12),
            date(2012, 1, 13),
            date(2012, 1, 14),
            date(2012, 1, 15)
        ])

    def test_calc_week_data(self):
        db = {
            "dates": {
                '2012-01-10': {
                    'start': '12:00',
                    'end': '14:00',
                    'breaks': [],
                    'comment': None
                },
                '2012-01-12': {
                    'start': '10:00',
                    'end': '19:00',
                    'breaks': [],
                    'comment': None
                },
                '2012-01-14': {
                    'start': '08:00',
                    'end': '17:00',
                    'breaks': [{
                        'start': '12:00',
                        'end': '13:00',
                        'comment': None
                    }],
                    'comment': None
                },
                '2012-01-15': {
                    'start': '08:30',
                    'end': '17:30',
                    'breaks': [],
                    'comment': None
                }
            }
        }

        week_data = arbeitcli.calc_week_data(db, 2, 2012)
        self.maxDiff = None
        self.assertEqual(week_data, {
            "days": [
                {"date": date(2012, 1,  9), "minutes": 0},
                {"date": date(2012, 1, 10), "minutes": 2 * 60},
                {"date": date(2012, 1, 11), "minutes": 0},
                {"date": date(2012, 1, 12), "minutes": 9 * 60},
                {"date": date(2012, 1, 13), "minutes": 0},
                {"date": date(2012, 1, 14), "minutes": 8 * 60},
                {"date": date(2012, 1, 15), "minutes": 9 * 60}
            ],
            "sum": 28 * 60
        })

if __name__ == '__main__':
    unittest.main()
