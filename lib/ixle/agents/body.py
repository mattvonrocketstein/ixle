""" ixle.agents.body
"""
from report import report
from ixle.python import ope
from .base import ItemIterator

import pyPdf

#print getPDFContent("test.pdf").encode("ascii", "ignore")
def getPDFContent(path):
    content = ""
    # Load PDF into pyPDF
    pdf = pyPdf.PdfFileReader(file(path, "rb"))
    # Iterate pages
    for i in range(0, pdf.getNumPages()):
        # Extract text from page and add to content
        content += pdf.getPage(i).extractText() + "\n"
    # Collapse whitespace
    content = " ".join(content.replace(u"\xa0", " ").strip().split())
    return content

def item2text(item):
    report('reading file')
    if ope(item.abspath):
        with open(item.abspath, 'r') as fhandle:
            if item.fext in 'txt'.split():
                return fhandle
            elif item.fext=='pdf':
                import StringIO
                body = StringIO.StringIO(getPDFContent(item.abspath))
                return body

#scanner
class Body(ItemIterator):
    nickname = 'body'
    covers_fields = ['body']

    def callback(self, item, fname=None, **kargs):
        report(item.fname)

        if item.file_type=='document':
            if self.force or not item.has_body:
                if not item.exists():
                    report('doesnt exist')
                    self.complain_missing(item.abspath)
                    return

                if item.file_type=='document':
                    success = self.set_attachment(item)
                    if success:
                        item.has_body = True
                        report('finished setting body.')
                        self.save(item)
                    else:
                        report("no success")
                else:
                    report('Not a document')
            else:
                report('already handled')
        else:
            report(str(item.file_type))

    def set_attachment(self, item):
        contents = item2text(item)
        report('saving attachment: ')
        report.console.draw_line()
        print contents
        report.console.draw_line()
        attachment_filename = 'body.txt'
        r = self.database.delete_attachment(item, attachment_filename)
        try:
            self.database.put_attachment(
                item, contents,
                filename=attachment_filename,
                content_type=None, # depends on filename ^
                )
            report('set attachment')
            return True
        except Exception,e:
            report("could not save body."+str(e))
            return False
