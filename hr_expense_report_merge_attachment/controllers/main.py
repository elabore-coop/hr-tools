import odoo.addons.web.controllers.main as main
import ast
import base64
import io
from odoo.tools.pdf import OdooPdfFileReader, OdooPdfFileWriter
import PyPDF2
import logging
from odoo import http
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter, A4

logger = logging.getLogger(__name__)


class Extension(main.ReportController):

    @http.route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token, context=None):
        """
        In case of hr expense sheet report : merge PDF with other attachments
        """

        res = super(Extension,self).report_download(data, token, context)
                
        if "hr_expense.report_expense_sheet" in ast.literal_eval(data)[0]: #check if we are generating expense sheet report pdf
            writer = OdooPdfFileWriter() #Open a file writer to create new PDF

            # Open main pdf and read it and write it page by page in new pdf
            main_pdf_reader = OdooPdfFileReader(io.BytesIO(res.data), strict=False)
            for n in range(main_pdf_reader.getNumPages()):
                writer.addPage(main_pdf_reader.getPage(n))

            # Parse data (last char after "/") to get id of current sheet
            expense_sheet_id = int(ast.literal_eval(data)[0].split('/')[-1])

            # Get ids of related expenses
            expense_ids = [e.id for e in http.request.env['hr.expense.sheet'].browse(expense_sheet_id).expense_line_ids]

            # Get related attachments
            attachments = http.request.env['ir.attachment'].search([('res_id','in',expense_ids),('res_model','=','hr.expense')])

            # Open each attachments, and write it page by page in new pdf
            for att in attachments:
                if att.mimetype == "application/pdf":
                    try:
                        attachment_reader = OdooPdfFileReader(io.BytesIO(base64.b64decode(att.datas)), strict=False)
                        for n in range(attachment_reader.getNumPages()):
                            writer.addPage(attachment_reader.getPage(n))
                    except PyPDF2.utils.PdfReadError: # Case of non-pdf attachments
                        logger.info('Attachment %s cannot be merged in expense report'%(att.name,))
                elif 'image/' in att.mimetype:
                    packet = io.BytesIO()                    
                    can = canvas.Canvas(packet)
                    img = ImageReader(io.BytesIO(base64.b64decode(att.datas)))
                    can.drawImage(img, 0, 0, A4[0]*0.9, A4[1]*0.9, preserveAspectRatio=True)
                    can.save()
                    packet.seek(0)
                    attachment_reader = OdooPdfFileReader(packet)
                    writer.addPage(attachment_reader.getPage(0))

            # Write new pdf to res.data
            buffer = io.BytesIO()
            writer.write(buffer)
            pdf_content = buffer.getvalue()

            res.data = pdf_content

        return res