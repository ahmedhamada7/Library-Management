#
# import oracledb as cx_Oracle
# import pandas as pd
# import logging
# from datetime import datetime
# from odoo import models, fields, api, _
# from odoo.exceptions import ValidationError, UserError
# import json
#
# logger = logging.getLogger(__name__)
#
#
# class OracleConnector(models.Model):
#     _name = 'oracle.connector'
#     _description = 'Oracle Database Connector'
#     _order = 'name asc'
#
#     name = fields.Char(string='Connection Name', required=True)
#     host = fields.Char(string='Host/IP', required=True, default='192.168.0.194')
#     port = fields.Char(string='Port', required=True, default='1521')
#     service_name = fields.Char(string='SID/Service Name', required=True, default='test')
#     username = fields.Char(string='Username', required=True)
#     password = fields.Char(string='Password', required=True, groups="base.group_user")
#     active = fields.Boolean(string='Active', default=True)
#     last_connection_test = fields.Datetime(string='Last Test')
#     connection_status = fields.Selection([
#         ('success', 'Connected'),
#         ('failed', 'Failed'),
#         ('not_tested', 'Not Tested')
#     ], string='Status', default='not_tested')
#     connection_string = fields.Char(
#         string='Connection String',
#         compute='_compute_connection_string'
#     )
#
#     @api.depends('host', 'port', 'service_name')
#     def _compute_connection_string(self):
#         for record in self:
#             record.connection_string = f"{record.username}@{record.host}:{record.port}/{record.service_name}" if all(
#                 [record.host, record.port, record.service_name]) else "Not Configured"
#
#     def get_dsn(self):
#         """Get DSN string"""
#         try:
#             return cx_Oracle.makedsn(self.host, int(self.port), service_name=self.service_name)
#         except ValueError:
#             raise ValidationError(_("Port must be a valid number."))
#
#     def get_connection(self):
#         self.ensure_one()
#         try:
#             dsn = self.get_dsn()
#             connection = cx_Oracle.connect(
#                 user=self.username,
#                 password=self.password,
#                 dsn=dsn
#             )
#             logger.info("Successfully connected to Oracle database")
#             return connection
#         except cx_Oracle.Error as e:
#             logger.error(f"Error connecting to Oracle: {e}")
#             raise ValidationError(_("Connection failed: %s") % str(e))
#
#     def test_connection(self):
#         """Test Oracle connection"""
#         self.ensure_one()
#         connection = None
#         try:
#             connection = self.get_connection()
#             self.write({
#                 'last_connection_test': datetime.now(),
#                 'connection_status': 'success'
#             })
#             return {
#                 'type': 'ir.actions.client',
#                 'tag': 'display_notification',
#                 'params': {
#                     'title': _('Success'),
#                     'message': _('Connection to Oracle database successful!'),
#                     'type': 'success',
#                     'sticky': False,
#                 }
#             }
#         except Exception as e:
#             logger.error(f"Oracle connection failed: {str(e)}")
#             self.write({
#                 'last_connection_test': datetime.now(),
#                 'connection_status': 'failed'
#             })
#             raise ValidationError(_("Connection failed: %s") % str(e))
#         finally:
#             if connection:
#                 connection.close()
#
#     def execute_select_query(self, query, params=None):
#         self.ensure_one()
#         conn = None
#         cursor = None
#         try:
#             conn = self.get_connection()
#             cursor = conn.cursor()
#             if params:
#                 cursor.execute(query, params)
#             else:
#                 cursor.execute(query)
#
#             columns = [desc[0].lower() for desc in cursor.description]
#             rows = cursor.fetchall()
#             df = pd.DataFrame(rows, columns=columns)
#             logger.info(f"Query executed successfully, fetched {len(df)} rows")
#             return df
#         except Exception as e:
#             logger.error(f"Error executing Oracle query: {e}")
#             raise ValidationError(_("Error executing query: %s") % str(e))
#         finally:
#             if cursor:
#                 cursor.close()
#             if conn:
#                 conn.close()
#
#     def fetch_table_data(self, table_name):
#         """Fetch data from specified table"""
#         self.ensure_one()
#
#         query = f"""
#             SELECT *
#             FROM {table_name}
#             WHERE ROWNUM <= 100
#         """
#
#         try:
#             df = self.execute_select_query(query)
#             data_records = df.to_dict('records')
#             logger.info(f"Fetched {len(data_records)} rows from {table_name}")
#
#             return data_records
#
#         except Exception as e:
#             logger.error(f"Error fetching table data: {e}")
#             raise
#
#     def fetch_customer_records(self):
#         self.ensure_one()
#         query = """
#             SELECT
#                 customer_name,
#                 customer_number,
#                 cust_account_id,
#                 insert_date
#             FROM
#                 XX_ODOO_CUSTOMER_HEADER
#             ORDER BY
#                 insert_date DESC
#         """
#         try:
#             df = self.execute_select_query(query)
#             logger.info(f"Successfully fetched {len(df)} customer records from XX_ODOO_CUSTOMER_HEADER")
#             return df
#
#         except Exception as e:
#             logger.error(f"Error fetching customer records: {e}")
#             raise ValidationError(_("Error fetching customer records: %s") % str(e))
#
#     def insert_customer_record(self, customer_data):
#         """Insert a new customer record into XX_ODOO_CUSTOMER_HEADER table"""
#         self.ensure_one()
#
#         insert_query = """
#             INSERT INTO XX_ODOO_CUSTOMER_HEADER (
#                 customer_name,
#                 customer_number,
#                 cust_account_id,
#                 insert_date
#             ) VALUES (
#                 :customer_name,
#                 :customer_number,
#                 :cust_account_id,
#                 :insert_date
#             )
#         """
#
#         conn = None
#         cursor = None
#
#         try:
#             conn = self.get_connection()
#             cursor = conn.cursor()
#             if 'insert_date' not in customer_data:
#                 customer_data['insert_date'] = datetime.now()
#             cursor.execute(insert_query, customer_data)
#             conn.commit()
#             logger.info(f"Successfully inserted customer record: {customer_data.get('customer_number')}")
#             return True
#         except Exception as e:
#             logger.error(f"Error inserting customer record: {e}")
#             if conn:
#                 conn.rollback()
#             return False
#         finally:
#             if cursor:
#                 cursor.close()
#             if conn:
#                 conn.close()
#
#
#     def update_customer_record(self, customer_number, update_data):
#         self.ensure_one()
#         update_query = """
#             UPDATE XX_ODOO_CUSTOMER_HEADER
#             SET customer_name = :customer_name,
#                 cust_account_id = :cust_account_id
#             WHERE customer_number = :customer_number
#         """
#         update_data['customer_number'] = customer_number
#         conn = None
#         cursor = None
#
#         try:
#             conn = self.get_connection()
#             cursor = conn.cursor()
#
#             cursor.execute(update_query, update_data)
#             conn.commit()
#
#             logger.info(f"Successfully updated customer record: {customer_number}")
#             return True
#
#         except Exception as e:
#             logger.error(f"Error updating customer record: {e}")
#             if conn:
#                 conn.rollback()
#             return False
#         finally:
#             if cursor:
#                 cursor.close()
#             if conn:
#                 conn.close()
#
#     def action_open_table_selector(self):
#         """Open wizard to select table and view data"""
#         self.ensure_one()
#         return {
#             'type': 'ir.actions.act_window',
#             'name': _('Select Oracle Table'),
#             'res_model': 'oracle.table.selector',
#             'view_mode': 'form',
#             'target': 'new',
#             'context': {
#                 'default_connector_id': self.id,
#             }
#         }
#
#     def action_fetch_customers(self):
#         self.ensure_one()
#         try:
#             df = self.fetch_customer_records()
#             if not df.empty:
#                 preview_model = self.env['oracle.data.preview']
#                 preview_model.search([('connector_id', '=', self.id)]).unlink()
#                 data_records = df.to_dict('records')
#                 for idx, record in enumerate(data_records, 1):
#                     preview_model.create({
#                         'connector_id': self.id,
#                         'row_number': idx,
#                         'data_json': json.dumps(record, ensure_ascii=False, indent=2),
#                         'table_name': 'XX_ODOO_CUSTOMER_HEADER'
#                     })
#
#                 return {
#                     'name': _('Customer Records - XX_ODOO_CUSTOMER_HEADER'),
#                     'type': 'ir.actions.act_window',
#                     'res_model': 'oracle.data.preview',
#                     'view_mode': 'tree,form',
#                     'domain': [('connector_id', '=', self.id)],
#                     'target': 'current',
#                     'context': {'default_connector_id': self.id},
#                 }
#             else:
#                 raise UserError(_("تم الاتصال بنجاح، لكن لم يتم جلب أي بيانات من جدول العملاء."))
#
#         except Exception as e:
#             raise UserError(_("فشل في جلب بيانات العملاء: %s") % str(e))
#
#     def copy(self, default=None):
#         """Override copy to avoid password duplication"""
#         default = dict(default or {})
#         default.update({
#             'name': _("%s (Copy)") % self.name,
#             'password': '',
#         })
#         return super(OracleConnector, self).copy(default)
#
#
# class OracleTableSelector(models.TransientModel):
#     _name = 'oracle.table.selector'
#     _description = 'Select Table for Oracle Data Fetch'
#
#     connector_id = fields.Many2one(
#         'oracle.connector',
#         string='Oracle Connection',
#         required=True,
#         ondelete='cascade',
#         default=lambda self: self.env.context.get('active_id')
#     )
#
#     table_name = fields.Char(
#         string='Table Name',
#         required=True,
#         default='XX_ODOO_CUSTOMER_HEADER',
#         help="Example: XX_ODOO_CUSTOMER_HEADER or SCHEMA.TABLE_NAME"
#     )
#
#     def action_fetch_data(self):
#         self.ensure_one()
#         if not self.table_name:
#             raise UserError(_("Please enter table name."))
#
#         try:
#             data_records = self.connector_id.fetch_table_data(self.table_name)
#
#             if data_records:
#                 logger.info("====================================")
#                 logger.info(f"Fetched {len(data_records)} records from {self.table_name}")
#                 logger.info(f"First record: {data_records[0]}")
#                 logger.info("====================================")
#                 preview_model = self.env['oracle.data.preview']
#                 preview_model.search([('connector_id', '=', self.connector_id.id)]).unlink()
#                 for idx, record in enumerate(data_records, 1):
#                     preview_model.create({
#                         'connector_id': self.connector_id.id,
#                         'row_number': idx,
#                         'data_json': json.dumps(record, ensure_ascii=False, indent=2) if isinstance(record,
#                                                                                                     dict) else str(
#                             record),
#                         'table_name': self.table_name
#                     })
#                 return {
#                     'name': _('Oracle Data Preview - %s') % self.table_name,
#                     'type': 'ir.actions.act_window',
#                     'res_model': 'oracle.data.preview',
#                     'view_mode': 'list,form',
#                     'domain': [('connector_id', '=', self.connector_id.id)],
#                     'target': 'current',
#                     'context': {'default_connector_id': self.connector_id.id},
#                 }
#             else:
#                 raise UserError(_("Connection successful, but no data was fetched."))
#
#         except Exception as e:
#             raise UserError(_("Failed to fetch data: %s") % str(e))
#
#
# class OracleDataPreview(models.Model):
#     """Model to preview Oracle data"""
#     _name = 'oracle.data.preview'
#     _description = 'Oracle Data Preview'
#     _order = 'row_number asc'
#
#     connector_id = fields.Many2one('oracle.connector', string='Connection', required=True)
#     row_number = fields.Integer(string='Row #')
#     data_json = fields.Text(string='Data (JSON)')
#     table_name = fields.Char(string='Table Name')
#     create_date = fields.Datetime(string='Fetched Date', default=fields.Datetime.now)
#
#     def name_get(self):
#         result = []
#         for record in self:
#             name = f"Row {record.row_number} - {record.table_name}"
#             result.append((record.id, name))
#         return result

import oracledb
import pandas as pd
import logging
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class OracleConnector(models.Model):
    _name = 'oracle.connector'
    _description = 'Oracle Database Connector'
    _order = 'name asc'

    name = fields.Char(string='Connection Name', required=True)
    host = fields.Char(string='Host/IP', required=True, default='192.168.0.194')
    port = fields.Char(string='Port', required=True, default='1521')
    service_name = fields.Char(string='SID/Service Name', required=True, default='test')
    username = fields.Char(string='Username', required=True)
    password = fields.Char(string='Password', required=True, groups="base.group_user")
    active = fields.Boolean(default=True)

    last_connection_test = fields.Datetime(string='Last Test')
    connection_status = fields.Selection([
        ('success', 'Connected'),
        ('failed', 'Failed'),
        ('not_tested', 'Not Tested')
    ], default='not_tested')

    connection_string = fields.Char(
        compute='_compute_connection_string',
        string='Connection String'
    )

    # ----------------------------------------------------------
    # COMPUTED
    # ----------------------------------------------------------

    @api.depends('host', 'port', 'service_name', 'username')
    def _compute_connection_string(self):
        for rec in self:
            if rec.host and rec.port and rec.service_name:
                rec.connection_string = (
                    f"{rec.username}@{rec.host}:{rec.port}/{rec.service_name}"
                )
            else:
                rec.connection_string = "Not Configured"

    # ----------------------------------------------------------
    # ORACLE CONNECTION - SIMPLIFIED FOR THIN MODE
    # ----------------------------------------------------------

    def get_dsn(self):
        """Create DSN string for Thin mode."""
        return f"{self.host}:{self.port}/{self.service_name}"

    def get_connection(self):
        """Establish connection using python-oracledb Thin mode."""
        self.ensure_one()
        dsn = self.get_dsn()

        try:
            # SIMPLIFIED: Thin mode connection without encoding parameters
            conn = oracledb.connect(
                user=self.username,
                password=self.password,
                dsn=dsn
            )
            # Note: In Thin mode, UTF-8 is usually the default encoding
            # If you need to explicitly set encoding, do it like this:
            # conn.encoding = "UTF-8"
            # conn.nencoding = "UTF-8"

            _logger.info("Oracle connection established successfully (Thin mode)")
            return conn

        except oracledb.Error as e:
            error = e.args[0] if e.args else str(e)
            _logger.error("Oracle connection error: %s", error.message)
            raise ValidationError(_("Oracle connection failed:\n%s") % error.message)

    # ----------------------------------------------------------
    # TEST CONNECTION
    # ----------------------------------------------------------

    def test_connection(self):
        self.ensure_one()
        conn = None
        try:
            conn = self.get_connection()
            # Test with a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM DUAL")
            result = cursor.fetchone()
            cursor.close()

            self.write({
                'last_connection_test': fields.Datetime.now(),
                'connection_status': 'success'
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Connection to Oracle database successful'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            self.write({
                'last_connection_test': fields.Datetime.now(),
                'connection_status': 'failed'
            })
            _logger.error("Connection test failed: %s", str(e))
            raise ValidationError(_("Connection failed:\n%s") % str(e))
        finally:
            if conn:
                conn.close()

    # ----------------------------------------------------------
    # QUERY EXECUTION
    # ----------------------------------------------------------

    def execute_select_query(self, query, params=None):
        self.ensure_one()
        conn = cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            columns = [col[0].lower() for col in cursor.description]
            rows = cursor.fetchall()

            df = pd.DataFrame(rows, columns=columns)
            _logger.info("Fetched %s rows from Oracle", len(df))
            return df

        except oracledb.Error as e:
            error = e.args[0] if e.args else str(e)
            _logger.error("Query failed: %s", error.message)
            raise ValidationError(_("Query execution failed:\n%s") % error.message)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # ----------------------------------------------------------
    # DATA FETCH
    # ----------------------------------------------------------

    def fetch_table_data(self, table_name):
        query = f"""
            SELECT *
            FROM {table_name}
            WHERE ROWNUM <= 100
        """
        df = self.execute_select_query(query)
        return df.to_dict('records')

    def fetch_customer_records(self):
        query = """
            SELECT customer_name,
                   customer_number,
                   cust_account_id,
                   insert_date
            FROM XX_ODOO_CUSTOMER_HEADER
            ORDER BY insert_date DESC
        """
        return self.execute_select_query(query)

    # ----------------------------------------------------------
    # INSERT / UPDATE
    # ----------------------------------------------------------

    def insert_customer_record(self, customer_data):
        self.ensure_one()
        query = """
            INSERT INTO XX_ODOO_CUSTOMER_HEADER (
                customer_name,
                customer_number,
                cust_account_id,
                insert_date
            ) VALUES (
                :customer_name,
                :customer_number,
                :cust_account_id,
                :insert_date
            )
        """
        customer_data.setdefault('insert_date', datetime.now())

        conn = cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, customer_data)
            conn.commit()
            return True
        except oracledb.Error as e:
            if conn:
                conn.rollback()
            error = e.args[0] if e.args else str(e)
            _logger.error("Insert failed: %s", error.message)
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def update_customer_record(self, customer_number, update_data):
        self.ensure_one()
        query = """
            UPDATE XX_ODOO_CUSTOMER_HEADER
               SET customer_name = :customer_name,
                   cust_account_id = :cust_account_id
             WHERE customer_number = :customer_number
        """
        update_data['customer_number'] = customer_number

        conn = cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, update_data)
            conn.commit()
            return True
        except oracledb.Error as e:
            if conn:
                conn.rollback()
            error = e.args[0] if e.args else str(e)
            _logger.error("Update failed: %s", error.message)
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # ----------------------------------------------------------
    # COPY
    # ----------------------------------------------------------

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': _("%s (Copy)") % self.name,
            'password': '',
        })
        return super().copy(default)


class OracleTableSelector(models.TransientModel):
    _name = 'oracle.table.selector'
    _description = 'Select Table for Oracle Data Fetch'

    connector_id = fields.Many2one(
        'oracle.connector',
        string='Oracle Connection',
        required=True,
        ondelete='cascade',
        default=lambda self: self.env.context.get('active_id')
    )

    table_name = fields.Char(
        string='Table Name',
        required=True,
        default='XX_ODOO_CUSTOMER_HEADER',
        help="Example: XX_ODOO_CUSTOMER_HEADER or SCHEMA.TABLE_NAME"
    )

    def action_fetch_data(self):
        self.ensure_one()
        if not self.table_name:
            raise UserError(_("Please enter table name."))

        try:
            data_records = self.connector_id.fetch_table_data(self.table_name)

            if data_records:
                logger.info("====================================")
                logger.info(f"Fetched {len(data_records)} records from {self.table_name}")
                logger.info(f"First record: {data_records[0]}")
                logger.info("====================================")
                preview_model = self.env['oracle.data.preview']
                preview_model.search([('connector_id', '=', self.connector_id.id)]).unlink()
                for idx, record in enumerate(data_records, 1):
                    preview_model.create({
                        'connector_id': self.connector_id.id,
                        'row_number': idx,
                        'data_json': json.dumps(record, ensure_ascii=False, indent=2) if isinstance(record,
                                                                                                    dict) else str(
                            record),
                        'table_name': self.table_name
                    })
                return {
                    'name': _('Oracle Data Preview - %s') % self.table_name,
                    'type': 'ir.actions.act_window',
                    'res_model': 'oracle.data.preview',
                    'view_mode': 'list,form',
                    'domain': [('connector_id', '=', self.connector_id.id)],
                    'target': 'current',
                    'context': {'default_connector_id': self.connector_id.id},
                }
            else:
                raise UserError(_("Connection successful, but no data was fetched."))

        except Exception as e:
            raise UserError(_("Failed to fetch data: %s") % str(e))


class OracleDataPreview(models.Model):
    """Model to preview Oracle data"""
    _name = 'oracle.data.preview'
    _description = 'Oracle Data Preview'
    _order = 'row_number asc'

    connector_id = fields.Many2one('oracle.connector', string='Connection', required=True)
    row_number = fields.Integer(string='Row #')
    data_json = fields.Text(string='Data (JSON)')
    table_name = fields.Char(string='Table Name')
    create_date = fields.Datetime(string='Fetched Date', default=fields.Datetime.now)

    def name_get(self):
        result = []
        for record in self:
            name = f"Row {record.row_number} - {record.table_name}"
            result.append((record.id, name))
        return result
