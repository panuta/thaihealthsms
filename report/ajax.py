from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils import simplejson

from models import *

from helper.utilities import format_abbr_datetime

def ajax_approve_report_submission(request):
    if request.method == 'POST':
        report_submission_id = request.POST['id']
        
        report_submission = ReportSubmission.objects.get(pk=report_submission_id)
        report_submission.state = APPROVED_ACTIVITY
        report_submission.approval_on = datetime.now()
        report_submission.save()
        
        return HttpResponse(simplejson.dumps({'timestamp':format_abbr_datetime(report_submission.approval_on)}))
        
    else:
        raise Http404

def ajax_reject_report_submission(request):
    if request.method == 'POST':
        report_submission_id = request.POST['id']
        
        report_submission = ReportSubmission.objects.get(pk=report_submission_id)
        report_submission.state = REJECTED_ACTIVITY
        report_submission.approval_on = datetime.now()
        report_submission.save()
        
        return HttpResponse(simplejson.dumps({'timestamp':format_abbr_datetime(report_submission.approval_on)}))
        
    else:
        raise Http404

def ajax_delete_report_file(request):
    if request.method == 'POST':
        file_id = request.POST['id']
        
        file_response = ReportSubmissionFileResponse.objects.get(pk=file_id)
        submission = file_response.submission
        
        uploading_directory = "%s/%d/%d/" % (settings.REPORT_SUBMIT_FILE_PATH, file_response.submission.report.id, file_response.submission.id)
        
        try:
            import os
            os.remove(uploading_directory + file_response.filename.encode('utf-8'))
        except OSError:
            pass
        
        file_response.delete()
        
        if not ReportSubmissionFileResponse.objects.filter(submission=submission).count():
            submission.state = NO_ACTIVITY
            submission.save()
        
        return HttpResponse("")
        
    else:
        raise Http404
