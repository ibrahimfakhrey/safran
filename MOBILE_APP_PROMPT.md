# Mobile App Feature: Investment Request & Confirmation

## Overview
We need to implement a new flow in the mobile app for users to submit a formal investment request. This involves a form with personal details and document uploads (KYC), followed by a confirmation screen.

## 1. Investment Request Screen

**Screen Name:** `InvestmentRequestScreen`
**Route:** `/investment-request/{apartmentId}`

### UI Components
*   **Header:** Title "Investment Request" + Apartment Title.
*   **Summary Card:**
    *   Shares Count (passed from previous screen).
    *   Share Price.
    *   Total Amount (Shares * Price).
*   **Form (Scrollable):**
    *   **Section 1: Personal Details**
        *   `Full Name` (Text Input)
        *   `Phone Number` (Phone Input)
        *   `National ID` (Number Input, 14 digits)
        *   `Date of Birth` (Date Picker)
        *   `Nationality` (Text Input)
        *   `Occupation` (Text Input)
        *   `Address` (Multi-line Text Input)
    *   **Section 2: Documents (KYC)**
        *   *Note: Use a file picker or camera integration.*
        *   `ID Front` (Image/PDF Upload)
        *   `ID Back` (Image/PDF Upload)
        *   `Proof of Address` (Image/PDF Upload) - e.g., Utility bill.
    *   **Section 3: Referral (Optional)**
        *   `Referral Code` (Text Input)
    *   **Section 4: Agreement**
        *   Checkbox: "I agree to the Terms & Conditions".
*   **Submit Button:** "Submit Request" (Disabled until form is valid).

### API Integration
*   **Endpoint:** `POST /api/v1/investments/request`
*   **Content-Type:** `multipart/form-data`
*   **Headers:** `Authorization: Bearer <token>`
*   **Body Parameters:**
    *   `apartment_id`: (Integer) ID of the apartment.
    *   `shares_requested`: (Integer) Number of shares.
    *   `full_name`: (String)
    *   `phone`: (String)
    *   `national_id`: (String)
    *   `address`: (String)
    *   `date_of_birth`: (String, YYYY-MM-DD)
    *   `nationality`: (String)
    *   `occupation`: (String)
    *   `referred_by_code`: (String, Optional)
    *   `id_document_front`: (File)
    *   `id_document_back`: (File)
    *   `proof_of_address`: (File)

### Logic
1.  Validate all required fields.
2.  Show loading indicator during submission.
3.  On success (200 OK):
    *   Parse response to get `request_id` and `total_amount`.
    *   Navigate to `RequestConfirmationScreen`.
4.  On error:
    *   Show error message (e.g., "Insufficient shares", "Missing fields").

---

## 2. Request Confirmation Screen

**Screen Name:** `RequestConfirmationScreen`
**Route:** `/request-confirmation/{requestId}`

### UI Components
*   **Success Icon:** Large checkmark or success animation.
*   **Title:** "Request Submitted Successfully!"
*   **Message:** "Your request (ID: #{requestId}) has been received. We will review your documents and contact you shortly."
*   **Details Card:**
    *   Request ID.
    *   Status: "Pending" (or Arabic "قيد الانتظار").
    *   Total Amount to Pay.
*   **Action Buttons:**
    *   "Back to Dashboard" (Navigates to Home/Dashboard).
    *   "View My Requests" (Navigates to Investment Requests list).

### Data Source
*   Pass the confirmation data (ID, Status, Amount) from the previous screen's API response.
*   *Optional:* You can also fetch details using `GET /api/v1/investments/requests` if needed.
