# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import time

from odoo.tests.common import TransactionCase, tagged

_logger = logging.getLogger(__name__)

@tagged('post_install_l10n', 'post_install', '-at_install', 'french_leaves')
class TestFrenchLeaves(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        country_fr = cls.env.ref('base.fr')
        cls.company = cls.env['res.company'].create({
            'name': 'French Company',
            'country_id': country_fr.id,
        })

        cls.employee = cls.env['hr.employee'].create({
            'name': 'Louis',
            'gender': 'other',
            'birthday': '1973-03-29',
            'country_id': country_fr.id,
            'company_id': cls.company.id,
        })

        cls.time_off_type = cls.env['hr.leave.type'].create({
            'name': 'Time Off',
            'requires_allocation': 'no',
            'request_unit': 'half_day',
        })
        cls.company.write({
            'l10n_fr_reference_leave_type': cls.time_off_type.id,
        })

        cls.base_calendar = cls.env['resource.calendar'].create({
            'name': 'default calendar',
        })

    def test_no_differences(self):
        # Base case that should not have a different behaviour
        self.company.resource_calendar_id = self.base_calendar
        self.employee.resource_calendar_id = self.base_calendar

        leave = self.env['hr.leave'].create({
            'name': 'Test',
            'holiday_status_id': self.time_off_type.id,
            'employee_id': self.employee.id,
            'request_date_from': '2021-09-06',
            'request_date_to': '2021-09-10',
            'company_id': self.company.id,
            'resource_calendar_id': self.employee.resource_calendar_id.id,
        })
        leave._compute_date_from_to()
        self.assertEqual(leave.number_of_days, 5, 'The number of days should be equal to 5.')
        leave.unlink()

    def test_end_of_week(self):
        employee_calendar = self.env['resource.calendar'].create({
            'name': 'Employee Calendar',
            'attendance_ids': [
                (0, 0, {'name': 'Monday Morning', 'dayofweek': '0', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Monday Afternoon', 'dayofweek': '0', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Tuesday Morning', 'dayofweek': '1', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Tuesday Afternoon', 'dayofweek': '1', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
            ],
        })
        self.company.resource_calendar_id = self.base_calendar
        self.employee.resource_calendar_id = employee_calendar

        leave = self.env['hr.leave'].create({
            'name': 'Test',
            'holiday_status_id': self.time_off_type.id,
            'employee_id': self.employee.id,
            'request_date_from': '2021-09-06', #monday
            'request_date_to': '2021-09-08', #wednesday
            'company_id': self.company.id,
            'resource_calendar_id': self.employee.resource_calendar_id.id,
        })
        leave._compute_date_from_to()
        self.assertEqual(leave.number_of_days, 5, 'The number of days should be equal to 5.')
        leave.unlink()

    def test_start_of_week(self):
        employee_calendar = self.env['resource.calendar'].create({
            'name': 'Employee Calendar',
            'attendance_ids': [
                (0, 0, {'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Thursday Morning', 'dayofweek': '3', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Thursday Afternoon', 'dayofweek': '3', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Friday Morning', 'dayofweek': '4', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Friday Afternoon', 'dayofweek': '4', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
            ],
        })
        self.company.resource_calendar_id = self.base_calendar
        self.employee.resource_calendar_id = employee_calendar

        leave = self.env['hr.leave'].create({
            'name': 'Test',
            'holiday_status_id': self.time_off_type.id,
            'employee_id': self.employee.id,
            'request_date_from': '2021-09-08',
            'request_date_to': '2021-09-10',
            'company_id': self.company.id,
            'resource_calendar_id': self.employee.resource_calendar_id.id,
        })
        
        leave._compute_date_from_to()
        self.assertEqual(leave.number_of_days, 5, 'The number of days should be equal to 5.')
        leave.unlink()

    def test_last_day_half(self):
        employee_calendar = self.env['resource.calendar'].create({
            'name': 'Employee Calendar',
            'attendance_ids': [
                (0, 0, {'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Thursday Morning', 'dayofweek': '3', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Thursday Afternoon', 'dayofweek': '3', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Friday Morning', 'dayofweek': '4', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Friday Afternoon', 'dayofweek': '4', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
            ],
        })
        self.company.resource_calendar_id = self.base_calendar
        self.employee.resource_calendar_id = employee_calendar

        leave = self.env['hr.leave'].create({
            'name': 'Test',
            'holiday_status_id': self.time_off_type.id,
            'employee_id': self.employee.id,
            'request_date_from': '2021-09-10', #friday
            'request_date_to': '2021-09-10',
            'request_unit_half': True,
            'request_date_from_period': 'am',
            'company_id': self.company.id,
            'resource_calendar_id': self.employee.resource_calendar_id.id,
        })
        leave._compute_date_from_to()
        # Since the employee works on the afternoon, the date_to is not post-poned
        self.assertEqual(leave.number_of_days, 0.5, 'The number of days should be equal to 0.5.')

        leave.request_date_from_period = 'pm'

        # This however should push the date_to
        self.assertEqual(leave.number_of_days, 2.5, 'The number of days should be equal to 2.5.')
        leave.unlink()

    def test_full_time_am_day_half(self):
        employee_calendar = self.env['resource.calendar'].create({
            'name': 'Employee Calendar',
            'attendance_ids': [
                (0, 0, {'name': 'Monday Morning', 'dayofweek': '0', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Monday Afternoon', 'dayofweek': '0', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Tuesday Morning', 'dayofweek': '1', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Tuesday Afternoon', 'dayofweek': '1', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Thursday Morning', 'dayofweek': '3', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Thursday Afternoon', 'dayofweek': '3', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Friday Morning', 'dayofweek': '4', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
            ],
        })
        self.company.resource_calendar_id = self.base_calendar
        self.employee.resource_calendar_id = employee_calendar

        leave = self.env['hr.leave'].create({
            'name': 'Test',
            'holiday_status_id': self.time_off_type.id,
            'employee_id': self.employee.id,
            'request_date_from': '2021-09-10', #friday
            'request_date_to': '2021-09-10',
            'request_unit_half': True,
            'request_date_from_period': 'am',
            'company_id': self.company.id,
            'resource_calendar_id': self.employee.resource_calendar_id.id,
        })
        leave._compute_date_from_to()
        # Since the employee works doesnt work the afternoon, the date_to is post-poned
        self.assertEqual(leave.number_of_days, 1, 'The number of days should be equal to 1.')
        leave.unlink()

    def test_am_day_half(self):
        employee_calendar = self.env['resource.calendar'].create({
            'name': 'Employee Calendar',
            'attendance_ids': [
                (0, 0, {'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Thursday Morning', 'dayofweek': '3', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Thursday Afternoon', 'dayofweek': '3', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Friday Morning', 'dayofweek': '4', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
            ],
        })
        self.company.resource_calendar_id = self.base_calendar
        self.employee.resource_calendar_id = employee_calendar

        leave = self.env['hr.leave'].create({
            'name': 'Test',
            'holiday_status_id': self.time_off_type.id,
            'employee_id': self.employee.id,
            'request_date_from': '2021-09-24', #friday
            'request_date_to': '2021-09-24',
            'request_unit_half': True,
            'request_date_from_period': 'am',
            'company_id': self.company.id,
            'resource_calendar_id': self.employee.resource_calendar_id.id,
        })
        leave._compute_date_from_to()
        # Since the employee works doesnt work the afternoon, the date_to is post-poned
        self.assertEqual(leave.number_of_days, 3, 'The number of days should be equal to 3.')
        leave.unlink()

    def test_calendar_with_holes(self):
        employee_calendar = self.env['resource.calendar'].create({
            'name': 'Employee Calendar',
            'attendance_ids': [
                (0, 0, {'name': 'Monday Morning', 'dayofweek': '0', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Monday Afternoon', 'dayofweek': '0', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Friday Morning', 'dayofweek': '4', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Friday Afternoon', 'dayofweek': '4', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
            ],
        })
        self.company.resource_calendar_id = self.base_calendar
        self.employee.resource_calendar_id = employee_calendar

        leave = self.env['hr.leave'].create({
            'name': 'Test',
            'holiday_status_id': self.time_off_type.id,
            'employee_id': self.employee.id,
            'request_date_from': '2021-09-06',
            'request_date_to': '2021-09-10',
            'company_id': self.company.id,
            'resource_calendar_id': self.employee.resource_calendar_id.id,
        })
        leave._compute_date_from_to()
        self.assertEqual(leave.number_of_days, 5, 'The number of days should be equal to 5.')
        leave.unlink()

    def test_calendar_end_week_hole(self):
        employee_calendar = self.env['resource.calendar'].create({
            'name': 'Employee Calendar',
            'attendance_ids': [
                (0, 0, {'name': 'Monday Morning', 'dayofweek': '0', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Monday Afternoon', 'dayofweek': '0', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
            ],
        })
        self.company.resource_calendar_id = self.base_calendar
        self.employee.resource_calendar_id = employee_calendar

        leave = self.env['hr.leave'].create({
            'name': 'Test',
            'holiday_status_id': self.time_off_type.id,
            'employee_id': self.employee.id,
            'request_date_from': '2021-09-06',
            'request_date_to': '2021-09-08',
            'company_id': self.company.id,
            'resource_calendar_id': self.employee.resource_calendar_id.id,
        })
        leave._compute_date_from_to()
        self.assertEqual(leave.number_of_days, 5, 'The number of days should be equal to 5.')
        leave.unlink()

    def test_2_weeks_calendar(self):
        company_calendar = self.env['resource.calendar'].create({
            'name': 'Company Calendar',
            'two_weeks_calendar': True,
            'attendance_ids': [
                (0, 0, {'week_type': '0', 'name': 'Monday Morning', 'dayofweek': '0', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'week_type': '0', 'name': 'Monday Afternoon', 'dayofweek': '0', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'week_type': '0', 'name': 'Tuesday Morning', 'dayofweek': '1', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'week_type': '0', 'name': 'Tuesday Afternoon', 'dayofweek': '1', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'week_type': '0', 'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'week_type': '0', 'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'week_type': '0', 'name': 'Thursday Morning', 'dayofweek': '3', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'week_type': '0', 'name': 'Thursday Afternoon', 'dayofweek': '3', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'week_type': '0', 'name': 'Friday Morning', 'dayofweek': '4', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'week_type': '0', 'name': 'Friday Afternoon', 'dayofweek': '4', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),

                (0, 0, {'week_type': '1', 'name': 'Monday Morning', 'dayofweek': '0', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'week_type': '1', 'name': 'Monday Afternoon', 'dayofweek': '0', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'week_type': '1', 'name': 'Tuesday Morning', 'dayofweek': '1', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'week_type': '1', 'name': 'Tuesday Afternoon', 'dayofweek': '1', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'week_type': '1', 'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'week_type': '1', 'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
            ],
        })
        employee_calendar = self.env['resource.calendar'].create({
            'name': 'Employee Calendar',
            'attendance_ids': [
                (0, 0, {'name': 'Monday Morning', 'dayofweek': '0', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Monday Afternoon', 'dayofweek': '0', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Tuesday Morning', 'dayofweek': '1', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Tuesday Afternoon', 'dayofweek': '1', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 8, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
            ],
        })
        self.company.resource_calendar_id = company_calendar
        self.employee.resource_calendar_id = employee_calendar

        # Week type 0
        leave = self.env['hr.leave'].create({
            'name': 'Test',
            'holiday_status_id': self.time_off_type.id,
            'employee_id': self.employee.id,
            'request_date_from': '2021-09-06',
            'request_date_to': '2021-09-08',
            'company_id': self.company.id,
            'resource_calendar_id': self.employee.resource_calendar_id.id,
        })
        leave._compute_date_from_to()
        self.assertEqual(leave.number_of_days, 5, 'The number of days should be equal to 5.')
        leave.unlink()

        # Week type 1
        leave = self.env['hr.leave'].create({
            'name': 'Test',
            'holiday_status_id': self.time_off_type.id,
            'employee_id': self.employee.id,
            'request_date_from': '2021-09-13',
            'request_date_to': '2021-09-15',
            'company_id': self.company.id,
            'resource_calendar_id': self.employee.resource_calendar_id.id,
        })
        leave._compute_date_from_to()
        self.assertEqual(leave.number_of_days, 3, 'The number of days should be equal to 3.')
        leave.unlink()

        # Both ending with week type 1
        leave = self.env['hr.leave'].create({
            'name': 'Test',
            'holiday_status_id': self.time_off_type.id,
            'employee_id': self.employee.id,
            'request_date_from': '2021-09-06',
            'request_date_to': '2021-09-15',
            'company_id': self.company.id,
            'resource_calendar_id': self.employee.resource_calendar_id.id,
        })
        leave._compute_date_from_to()
        self.assertEqual(leave.number_of_days, 8, 'The number of days should be equal to 3.')
        leave.unlink()

        # Both ending with week type 0
        with self.assertQueryCount(118):
            start_time = time.time()
            leave = self.env['hr.leave'].create({
                'name': 'Test',
                'holiday_status_id': self.time_off_type.id,
                'employee_id': self.employee.id,
                'request_date_from': '2021-09-13',
                'request_date_to': '2021-09-22',
                'company_id': self.company.id,
                'resource_calendar_id': self.employee.resource_calendar_id.id,
            })
            leave._compute_date_from_to()
            # --- 0.11486363410949707 seconds ---
            _logger.info("French Leave Creation: --- %s seconds ---", time.time() - start_time)
        self.assertEqual(leave.number_of_days, 8, 'The number of days should be equal to 3.')
        leave.unlink()
