from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from datetime import date, timedelta

@tagged("post_install", "-at_install")
class TestHrEmployeeStatsRecovery(TransactionCase):
    def setUp(self):
        super().setUp()
        self.user = self.env['res.users'].create({
            'name': 'Camille',
            'login': 'camille',
        })
        self.recovery_type = self.env['hr.leave.type'].create({
            'name': 'Recovery',
            'request_unit': 'hour',
        })
        self.employee = self.env['hr.employee'].create({
            'name': 'Camille',
            'user_id': self.user.id,
        })
        self.base_calendar = self.env['resource.calendar'].create({
            'name': 'Default Calendar',
            'attendance_ids': [
                (0, 0, {'name': 'Monday Morning', 'dayofweek': '0', 'hour_from': 9, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Monday Afternoon', 'dayofweek': '0', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Tuesday Morning', 'dayofweek': '1', 'hour_from': 9, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Tuesday Afternoon', 'dayofweek': '1', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 9, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Thursday Morning', 'dayofweek': '3', 'hour_from': 9, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Thursday Afternoon', 'dayofweek': '3', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Friday Morning', 'dayofweek': '4', 'hour_from': 9, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Friday Afternoon', 'dayofweek': '4', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
            ],
        })
        self.employee.resource_calendar_id = self.base_calendar
        self.env.company.coef = 25

    def _create_timesheet_sheet(self, start_date):
        #Crée une feuille de temps pour la semaine du lundi au dimanche
        return self.env['hr_timesheet.sheet'].create({
            'employee_id': self.employee.id,
            'date_start': start_date,
            'date_end': start_date + timedelta(days=6),
        })

    def _create_stats(self, start_date, nb_days, unit_amount):
        # Crée des temps du lundi au vendredi (ou nb_days)
        for i in range(nb_days):
            self.env['account.analytic.line'].create({
                'employee_id': self.employee.id,
                'date': start_date + timedelta(days=i),
                'unit_amount': unit_amount,
                'account_id': 1,
                'name': 'Work Entry',
            })
            # Génère les hr_employee_stats pour chaque jour de la période
            stat = self.env['hr.employee.stats'].create({
                'employee_id': self.employee.id,
                'date': start_date + timedelta(days=i),
            })
            stat._compute_hours()
            yield stat

    def test_no_recovery_hours(self):
        start_date = date.today() - timedelta(days=date.today().weekday() + 7)  # lundi de la semaine dernière
        timesheet_sheet = self._create_timesheet_sheet(start_date)
        for stat in self._create_stats(start_date, 5, 7): #créer 5 stats de 7h chacune
            # Compare les heures de récupération calculées et le calendrier qui prévoit 7h par jour
            self.assertEqual(stat.total_hours, 7, "total_hours should be 7",) # l'employé a travaillé 7h chaque jour
            self.assertEqual(stat.total_planned_hours, 7, "total_planned_hours should be 7",) # le calendrier prévoit 7h chaque jour
            self.assertEqual(stat.total_leave_hours, 0, "total_leave_hours should be 0",) # l'employé n'a pas de congé sur ce jour
            self.assertEqual(stat.total_recovery_hours, 0, "total_recovery_hours should be 0",) # l'employé n'a pas posé de récupération sur ce jour
            self.assertEqual(stat.gap_hours, 0, "gap_hours should be 0",) # pas de différence entre les heures travaillées et les heures planifiées
        # La feuille de temps sur cette période doit compter 0h de déficit et 0h de récupération
        self.assertEqual(timesheet_sheet.timesheet_sheet_gap_hours, 0, "timesheet_sheet_gap_hours should be 0",)
        self.assertEqual(timesheet_sheet.timesheet_sheet_recovery_hours, 0, "timesheet_sheet_recovery_hours should be 0",)

    def test_positive_recovery_hours(self):
        start_date = date.today() - timedelta(days=date.today().weekday() + 7)  # lundi de la semaine dernière
        timesheet_sheet = self._create_timesheet_sheet(start_date)
        for stat in self._create_stats(start_date, 5, 8): #créer 5 stats de 8h chacune
            # Compare les heures de récupération calculées et le calendrier qui prévoit 7h par jour
            self.assertEqual(stat.total_hours, 8, "total_hours should be 8",) # l'employé a travaillé 8h chaque jour
            self.assertEqual(stat.total_planned_hours, 7, "total_planned_hours should be 7",) # le calendrier prévoit 7h chaque jour
            self.assertEqual(stat.total_leave_hours, 0, "total_leave_hours should be 0",) # l'employé n'a pas de congé sur ce jour
            self.assertEqual(stat.total_recovery_hours, 0, "total_recovery_hours should be 0",) # l'employé n'a pas posé de récupération sur ce jour
            self.assertEqual(stat.gap_hours, 1, "gap_hours should be 1",) # l'employée a travaillé une heure de plus que prévu
        # La feuille de temps doit compter 5h d'heure sup soit 6,25h de récupération avec la majoration de 25%
        self.assertEqual(timesheet_sheet.timesheet_sheet_gap_hours, 5, "timesheet_sheet_gap_hours should be 5",)
        self.assertEqual(timesheet_sheet.timesheet_sheet_recovery_hours, 6.25, "timesheet_sheet_recovery_hours should be 6,25",)

    def test_negative_recovery_hours(self):
        start_date = date.today() - timedelta(days=date.today().weekday() + 7)  # lundi de la semaine dernière
        timesheet_sheet = self._create_timesheet_sheet(start_date)
        for stat in self._create_stats(start_date, 5, 6): #créer 5 stats de 6h chacune
            # Compare les heures de récupération calculées et le calendrier qui prévoit 7h par jour
            self.assertEqual(stat.total_hours, 6, "total_hours should be 6",) # l'employé a travaillé 6h chaque jour
            self.assertEqual(stat.total_planned_hours, 7, "total_planned_hours should be 7",) # le calendrier prévoit 7h chaque jour
            self.assertEqual(stat.total_leave_hours, 0, "total_leave_hours should be 0",) # l'employé n'a pas de congé sur ce jour
            self.assertEqual(stat.total_recovery_hours, 0, "total_recovery_hours should be 0",) # l'employé n'a pas posé de récupération sur ce jour
            self.assertEqual(stat.gap_hours, -1, "gap_hours should be -1",) # l'employée a travaillé une heure de moins que prévu
        # La feuille de temps doit compter -5h de déficit et -5h de récupération
        self.assertEqual(timesheet_sheet.timesheet_sheet_gap_hours, -5, "timesheet_sheet_gap_hours should be -5",) # l'employé a travaillé -5h au total sur la semaine
        self.assertEqual(timesheet_sheet.timesheet_sheet_recovery_hours, -5, "timesheet_sheet_recovery_hours should be -5",) # -5h sera le montant de l'allocation de récupération (pas de coef appliqué pour les déficites d'heures)

    def test_recovery_hours_part_time_employee(self):
        part_time_calendar = self.env['resource.calendar'].create({
            'name': 'Part Time Calendar',
            'attendance_ids': [
                (0, 0, {'name': 'Monday Morning', 'dayofweek': '0', 'hour_from': 9, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Monday Afternoon', 'dayofweek': '0', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Tuesday Morning', 'dayofweek': '1', 'hour_from': 9, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Tuesday Afternoon', 'dayofweek': '1', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Wednesday Morning', 'dayofweek': '2', 'hour_from': 9, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Wednesday Afternoon', 'dayofweek': '2', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
                (0, 0, {'name': 'Thursday Morning', 'dayofweek': '3', 'hour_from': 9, 'hour_to': 12, 'day_period': 'morning'}),
                (0, 0, {'name': 'Thursday Afternoon', 'dayofweek': '3', 'hour_from': 13, 'hour_to': 17, 'day_period': 'afternoon'}),
            ],
        })
        self.employee.resource_calendar_id = part_time_calendar.id
    
        start_date = date.today() - timedelta(days=date.today().weekday() + 7)  # lundi de la semaine dernière
        timesheet_sheet = self._create_timesheet_sheet(start_date)
        for stat in self._create_stats(start_date, 4, 8): #créer 4 stats de 8h chacune
            # Compare les heures de récupération calculées et le calendrier qui prévoit 7h par jour pendant 4 jours
            self.assertEqual(stat.total_hours, 8, "total_hours should be 8",) # l'employé a travaillé 6h chaque jour
            self.assertEqual(stat.total_planned_hours, 7, "total_planned_hours should be 7",) # le calendrier prévoit 7h chaque jour
            self.assertEqual(stat.total_leave_hours, 0, "total_leave_hours should be 0",) # l'employé n'a pas de congé sur ce jour
            self.assertEqual(stat.total_recovery_hours, 0, "total_recovery_hours should be 0",) # l'employé n'a pas posé de récupération sur ce jour
            self.assertEqual(stat.gap_hours, 1, "gap_hours should be 1",) # l'employée a travaillé une heure de moins que prévu
        # La feuille de temps doit compter 4h d'heure sup soit 5h de récupération avec la majoration de 25%
        self.assertEqual(timesheet_sheet.timesheet_sheet_gap_hours, 4, "timesheet_sheet_gap_hours should be 4",) # l'employé a travaillé supplémentaire 4h au total sur la semaine
        self.assertEqual(timesheet_sheet.timesheet_sheet_recovery_hours, 5, "timesheet_sheet_recovery_hours should be 5",) # 5h sera le montant de l'allocation de récupération (coef de 25% de majoration)
