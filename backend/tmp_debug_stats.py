import os
import django
import traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.test import RequestFactory
from apps.reports.views import ReportViewSet

rf = RequestFactory()
req = rf.get('/api/reports/statistics/')

view = ReportViewSet.as_view({'get': 'statistics'})

try:
    resp = view(req)
    # If DRF Response
    try:
        data = resp.data
    except Exception:
        data = getattr(resp, 'content', None)
    print('STATUS:', getattr(resp, 'status_code', 'N/A'))
    print('DATA:')
    print(data)
except Exception as e:
    print('EXCEPTION TRACEBACK:')
    traceback.print_exc()
