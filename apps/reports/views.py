from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def generate_report(request):
    template = get_template('reports/report.html')

    context = {
        'title': 'Sales Forecast Report',
        'data': [100, 120, 150]
    }

    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    pisa.CreatePDF(html, dest=response)

    return response