import os
import json
import pytest
from unittest.mock import patch, MagicMock
import sys
from unittest.mock import patch, MagicMock

# Patch boto3.resource and boto3.client before importing visitor_counter
boto3_resource_patch = patch('boto3.resource', MagicMock())
boto3_client_patch = patch('boto3.client', MagicMock())
boto3_resource_patch.start()
boto3_client_patch.start()
import visitor_counter as vc

@pytest.fixture
def lambda_event_pdf_download():
    return {
        'body': json.dumps({'event': 'pdf_download'}),
        'requestContext': {
            'identity': {
                'sourceIp': '1.2.3.4'
            }
        }
    }

@patch('visitor_counter.eventbridge')
def test_pdf_download_event_sends_eventbridge(mock_eventbridge, lambda_event_pdf_download):
    mock_eventbridge.put_events = MagicMock(return_value={'FailedEntryCount': 0})
    os.environ['EVENT_BUS_NAME'] = 'test-bus'
    response = vc.lambda_handler(lambda_event_pdf_download, None)
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['message'] == 'PDF download event logged'
    mock_eventbridge.put_events.assert_called_once()
    args, kwargs = mock_eventbridge.put_events.call_args
    entries = kwargs['Entries']
    assert entries[0]['Source'] == 'cloudresume.frontend'
    assert entries[0]['DetailType'] == 'ResumePDFDownload'
    detail = json.loads(entries[0]['Detail'])
    assert detail['event'] == 'pdf_download'
    assert detail['source_ip'] == '1.2.3.4'

@patch('visitor_counter.eventbridge')
def test_pdf_download_eventbridge_failure(mock_eventbridge, lambda_event_pdf_download):
    mock_eventbridge.put_events.side_effect = Exception('EventBridge error')
    os.environ['EVENT_BUS_NAME'] = 'test-bus'
    response = vc.lambda_handler(lambda_event_pdf_download, None)
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['message'] == 'PDF download event logged'
    mock_eventbridge.put_events.assert_called_once()

@patch('visitor_counter.eventbridge')
def test_integration_pdf_download_flow(mock_eventbridge):
    """
    Integration test: Simulate a full PDF download POST from frontend to backend Lambda.
    Checks that EventBridge is called and response is correct.
    """
    mock_eventbridge.put_events = MagicMock(return_value={'FailedEntryCount': 0})
    os.environ['EVENT_BUS_NAME'] = 'integration-bus'
    event = {
        'body': json.dumps({'event': 'pdf_download'}),
        'requestContext': {
            'identity': {
                'sourceIp': '123.123.123.123'
            }
        }
    }
    response = vc.lambda_handler(event, None)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'PDF download event logged'
    mock_eventbridge.put_events.assert_called_once()
    entries = mock_eventbridge.put_events.call_args[1]['Entries']
    assert entries[0]['Source'] == 'cloudresume.frontend'
    assert entries[0]['DetailType'] == 'ResumePDFDownload'
    detail = json.loads(entries[0]['Detail'])
    assert detail['event'] == 'pdf_download'
    assert detail['source_ip'] == '123.123.123.123'
