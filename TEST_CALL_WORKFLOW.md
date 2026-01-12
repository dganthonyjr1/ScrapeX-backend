# ScrapeX Test Call Workflow with Retell AI

This document outlines the complete workflow for testing autonomous calls using Retell AI integration after TCPA certification acceptance.

## Overview

The test call workflow validates:
1. **TCPA Compliance** - Consent verification and call time validation
2. **Retell AI Integration** - Agent creation and call initiation
3. **Call Tracking** - Recording, transcription, and analytics
4. **Compliance Features** - Consent management and audit trails

## Prerequisites

Before initiating a test call, ensure:

- ✅ Lovable compliance module is fully deployed
- ✅ TCPA certification has been accepted on the Compliance page
- ✅ Retell AI API key is configured: `_a07875e170316b0f6f8481a00965`
- ✅ Backend API is running and accessible
- ✅ Test phone number is ready: `+18562001869`
- ✅ Current time is within allowed calling hours (8 AM - 9 PM)

## Test Call Workflow

### Phase 1: TCPA Certification & Consent

**User Action on Compliance Page:**
1. Navigate to **Settings → Compliance**
2. Review TCPA certification requirements
3. Check the **"I accept TCPA certification"** checkbox
4. Click **"Submit TCPA Certification"**

**Backend Processing:**
```
POST /api/v1/compliance/tcpa-certification
{
  "user_id": "user_123",
  "accepted": true,
  "timestamp": "2026-01-12T14:30:00Z"
}

Response:
{
  "success": true,
  "certification_id": "cert_abc123",
  "status": "accepted",
  "valid_until": "2027-01-12T14:30:00Z"
}
```

### Phase 2: Consent Recording

**User Action on Compliance Page:**
1. After TCPA certification, the **"Test Call"** button becomes active
2. Click **"Test Call"** to begin the test workflow
3. Select a test facility from the dropdown:
   - Cleveland Clinic
   - UCSF Health
   - Johns Hopkins Medicine
4. Review the consent message
5. Click **"I consent to this test call"**

**Backend Processing:**
```
POST /api/v1/compliance/consent
{
  "phone_number": "+18562001869",
  "consent_type": "tcpa",
  "facility_name": "Cleveland Clinic",
  "accepted": true,
  "timestamp": "2026-01-12T14:32:00Z"
}

Response:
{
  "success": true,
  "consent_id": "consent_xyz789",
  "status": "accepted",
  "expires_at": "2027-07-12T14:32:00Z"
}
```

### Phase 3: Call Initiation

**User Action on Compliance Page:**
1. After consent is recorded, click **"Initiate Test Call"**
2. A loading indicator appears showing call status
3. The system displays the call ID and status updates in real-time

**Backend Processing:**

#### Step 1: Create Retell AI Agent
```
POST /api/v1/retell/agents
{
  "facility_name": "Cleveland Clinic",
  "call_script": "Hello, this is ScrapeX calling about our healthcare lead generation platform..."
}

Response:
{
  "agent_id": "agent_cleveland_clinic_1234567890",
  "agent_name": "ScrapeX-Cleveland-Clinic",
  "status": "created"
}
```

#### Step 2: Validate Call Compliance
```
POST /api/v1/compliance/validate-call
{
  "phone_number": "+18562001869",
  "facility_name": "Cleveland Clinic",
  "current_time": "2026-01-12T14:35:00Z"
}

Validation Checks:
- ✅ TCPA consent: ACCEPTED
- ✅ Recording consent: ACCEPTED
- ✅ Call time: 14:35 (within 8 AM - 9 PM)
- ✅ Do Not Call list: NOT ON LIST
- ✅ State recording laws: COMPLIANT (two-party consent recorded)

Response:
{
  "compliant": true,
  "checks": {
    "tcpa_consent": "accepted",
    "recording_consent": "accepted",
    "call_time": "valid",
    "dnc_check": "clear",
    "state_laws": "compliant"
  }
}
```

#### Step 3: Initiate Call with Retell AI
```
POST /api/v1/retell/calls
{
  "agent_id": "agent_cleveland_clinic_1234567890",
  "phone_number": "+18562001869",
  "facility_name": "Cleveland Clinic",
  "consent_status": "accepted"
}

Response:
{
  "success": true,
  "call_id": "call_cleveland_clinic_1234567890",
  "status": "initiated",
  "facility_name": "Cleveland Clinic",
  "initiated_at": "2026-01-12T14:35:30Z"
}
```

### Phase 4: Call Execution & Monitoring

**Real-Time Updates on Compliance Page:**

The frontend polls the backend for call status updates:

```
GET /api/v1/calls/{call_id}/status

Response (updates every 2 seconds):
{
  "call_id": "call_cleveland_clinic_1234567890",
  "status": "in_progress",
  "facility_name": "Cleveland Clinic",
  "initiated_at": "2026-01-12T14:35:30Z",
  "duration": 45,
  "agent_message": "Agent is speaking with facility representative...",
  "recording_status": "recording"
}
```

**Possible Call Statuses:**
- `initiated` - Call is being set up
- `ringing` - Phone is ringing
- `in_progress` - Call is active
- `completed` - Call finished successfully
- `no_answer` - No one answered
- `voicemail` - Call went to voicemail
- `failed` - Call failed to connect

### Phase 5: Call Completion & Recording

**When Call Ends:**

```
GET /api/v1/calls/{call_id}/status

Response:
{
  "call_id": "call_cleveland_clinic_1234567890",
  "status": "completed",
  "facility_name": "Cleveland Clinic",
  "initiated_at": "2026-01-12T14:35:30Z",
  "ended_at": "2026-01-12T14:38:15Z",
  "duration": 165,
  "outcome": "interested",
  "recording_url": "https://recordings.retellai.com/call_cleveland_clinic_1234567890.mp3",
  "transcript": "Agent: Hello, this is ScrapeX...\nRecipient: Hi, how can I help?...",
  "compliance_status": "compliant"
}
```

### Phase 6: Compliance Audit Trail

**Automatic Audit Log Entry:**

```
POST /api/v1/compliance/audit-log
{
  "event_type": "call_completed",
  "call_id": "call_cleveland_clinic_1234567890",
  "facility_name": "Cleveland Clinic",
  "phone_number": "+18562001869",
  "timestamp": "2026-01-12T14:38:15Z",
  "compliance_checks": {
    "tcpa_consent": "verified",
    "recording_consent": "verified",
    "call_time": "valid",
    "dnc_check": "clear",
    "state_laws": "compliant"
  },
  "recording_url": "https://recordings.retellai.com/call_cleveland_clinic_1234567890.mp3",
  "transcript_available": true,
  "user_id": "user_123"
}
```

**Audit Log Entry Stored:**
- Call ID
- Facility name and phone number
- Timestamp
- All compliance checks performed
- Recording URL
- Transcript availability
- User who initiated the call

## Expected Outcomes

### Successful Test Call

**Scenario:** Call connects and facility representative answers

```
Call Flow:
1. Agent calls +18562001869
2. Representative answers
3. Agent introduces ScrapeX
4. Agent explains the platform
5. Representative expresses interest
6. Agent schedules follow-up call
7. Call ends after ~3-5 minutes

Outcome: "interested"
Recording: Available for review
Transcript: Available for review
Compliance: All checks passed ✅
```

### No Answer

**Scenario:** Call rings but no one answers

```
Call Flow:
1. Agent calls +18562001869
2. Phone rings 4-5 times
3. Call times out or goes to voicemail
4. Agent leaves voicemail message

Outcome: "no_answer" or "voicemail"
Recording: Available for review
Transcript: Available (voicemail message)
Compliance: All checks passed ✅
```

### Call Failed

**Scenario:** Technical issue prevents call

```
Call Flow:
1. System attempts to call +18562001869
2. Connection fails (invalid number, network issue, etc.)
3. Error is logged

Outcome: "failed"
Error Details: Provided in response
Compliance: Issue logged for review
```

## Troubleshooting

### Issue: "Test Call" button is disabled

**Solution:**
- Verify TCPA certification has been accepted
- Check that current time is within 8 AM - 9 PM
- Ensure backend API is running

### Issue: Call fails to initiate

**Solution:**
- Verify phone number format: `+18562001869`
- Check Retell AI API key is configured correctly
- Verify internet connection
- Check backend logs for errors

### Issue: No recording or transcript

**Solution:**
- Wait 30-60 seconds after call completion for processing
- Refresh the page to get updated status
- Check Retell AI dashboard for processing status

### Issue: Compliance validation fails

**Solution:**
- Verify TCPA consent was accepted
- Check current time is within allowed hours
- Verify phone number is not on Do Not Call list
- Check state recording consent requirements

## API Endpoints for Test Call Workflow

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/api/v1/compliance/tcpa-certification` | POST | Accept TCPA certification |
| `/api/v1/compliance/consent` | POST | Record consent for a call |
| `/api/v1/retell/agents` | POST | Create Retell AI agent |
| `/api/v1/retell/calls` | POST | Initiate call with Retell AI |
| `/api/v1/calls/{call_id}/status` | GET | Get call status |
| `/api/v1/calls/{call_id}/recording` | GET | Get call recording |
| `/api/v1/calls/{call_id}/transcript` | GET | Get call transcript |
| `/api/v1/compliance/validate-call` | POST | Validate call compliance |
| `/api/v1/compliance/audit-log` | POST | Create audit log entry |

## Next Steps After Successful Test

1. **Review Recording & Transcript** - Listen to the call and review the transcript
2. **Verify Compliance Audit Trail** - Check that all compliance checks were logged
3. **Test with Additional Facilities** - Repeat with UCSF Health and Johns Hopkins
4. **Gather Feedback** - Note any improvements needed
5. **Prepare for Production** - Once all tests pass, prepare for real customer calls

## Security & Compliance Notes

- All calls are recorded with explicit consent
- All recordings are encrypted and stored securely
- Audit trails are immutable and tamper-proof
- Call logs are retained for 18 months per TCPA requirements
- All data is compliant with CCPA and state privacy laws
- Opt-out requests are honored immediately
