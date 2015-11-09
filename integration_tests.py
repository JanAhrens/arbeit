import unittest
from unittest.mock import MagicMock

from freezegun import freeze_time
import arbeitcli

class ArbeitcliIntegrationTest(unittest.TestCase):

    @freeze_time('2012-12-12 11:00:00Z', tz_offset=1)
    def test_set_time(self):
        arbeitcli.load_db = MagicMock(return_value={"dates": {}})
        arbeitcli.write_db = MagicMock()

        arbeitcli.set_time('start', '12:00', False)

        arbeitcli.write_db.assert_called_with({"dates": {'2012-12-12': {'start': '12:00', 'end': None, 'breaks': [], 'comment': None}}})

    @freeze_time('2012-12-12 11:00:00Z', tz_offset=1)
    def test_set_time_with_no_force(self):
        arbeitcli.load_db = MagicMock(return_value={"dates": {'2012-12-12': {'start': '09:00', 'end': None, 'breaks': [], 'comment': None}}})
        arbeitcli.write_db = MagicMock()

        arbeitcli.set_time('start', '12:00', False)

        arbeitcli.write_db.assert_not_called()

    @freeze_time('2012-12-12 11:00:00Z', tz_offset=1)
    def test_set_time_with_with_force(self):
        fake_breaks = [1, 2, 3]
        arbeitcli.load_db = MagicMock(return_value={
            "dates": {
                '2012-12-12': {
                    'start': '09:00',
                    'end': None,
                    'breaks': fake_breaks,
                    'comment': None}
            }
        })
        arbeitcli.write_db = MagicMock()

        arbeitcli.set_time('start', '12:00', True)

        arbeitcli.write_db.assert_called_with({
            "dates": {
                '2012-12-12': {
                    'start': '12:00',
                    'end': None,
                    'breaks': fake_breaks,
                    'comment': None
                }
            }
        })

    @freeze_time('2012-12-12 12:00:00Z', tz_offset=1)
    def test_add_break_without_end(self):
        arbeitcli.load_db = MagicMock(return_value={"dates": {}})
        arbeitcli.write_db = MagicMock()

        arbeitcli.add_break('12:00', None, None)

        arbeitcli.write_db.assert_called_with({
            "dates": {
                '2012-12-12': {
                    'start': None,
                    'end': None,
                    'breaks': [{
                        'start': '12:00',
                        'end': '13:00',
                        'comment': None
                    }],
                    'comment': None
                }
            }
        })

    @freeze_time('2012-12-12 15:00:00Z', tz_offset=1)
    def test_add_break_with_end_and_comment(self):
        arbeitcli.load_db = MagicMock(return_value={"dates": {}})
        arbeitcli.write_db = MagicMock()

        arbeitcli.add_break('12:00', '13:00', 'lunch')

        arbeitcli.write_db.assert_called_with({
            "dates": {
                '2012-12-12': {
                    'start': None,
                    'end': None,
                    'breaks': [{
                        'start': '12:00',
                        'end': '13:00',
                        'comment': 'lunch'
                    }],
                    'comment': None
                }
            }
        })

if __name__ == '__main__':
    unittest.main()
