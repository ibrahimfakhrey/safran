# Admin Panel & KYC Investment Features - Flutter Implementation

## Overview
Add Admin Panel and Real Investment (KYC) features to the existing IPI Real Estate Investment Flutter app.

---

## 🔌 New API Endpoints

**Base URL:** `http://127.0.0.1:5001/api/v1`

### Admin Panel Endpoints (Admin Only)
1. **GET** `/admin/stats`
   - Headers: `Authorization: Bearer <token>`
   - Returns: `{total_users, total_apartments, total_cars, pending_requests, approved_requests, total_investments, total_platform_value}`
   - **Requires:** `is_admin: true` in user object

2. **GET** `/admin/investment-requests`
   - Headers: `Authorization: Bearer <token>`
   - Query params: `status` (pending/approved/rejected), `page`, `per_page`
   - Returns: List of investment requests with user info, apartment details, KYC data
   ```json
   {
     "requests": [{
       "id": 1,
       "user_name": "أحمد محمد",
       "user_email": "ahmed@example.com",
       "apartment_title": "شقة فاخرة",
       "shares_requested": 5,
       "total_amount": 500000,
       "status": "pending",
       "status_arabic": "قيد الانتظار",
       "full_name": "أحمد محمد علي",
       "phone": "01234567890",
       "national_id": "12345678901234",
       "date_submitted": "2025-11-23T10:00:00"
     }]
   }
   ```

3. **POST** `/admin/investment-requests/{id}/action`
   - Headers: `Authorization: Bearer <token>`
   - Body: `{"action": "approve" or "reject", "admin_notes": "string"}`
   - Returns: Updated request status

### KYC & Investment Request Endpoints
4. **POST** `/user/kyc`
   - Headers: `Authorization: Bearer <token>`
   - Body: 
   ```json
   {
     "phone": "01234567890",
     "national_id": "12345678901234",
     "address": "123 شارع الجمهورية، القاهرة",
     "date_of_birth": "1990-01-15",
     "nationality": "مصري",
     "occupation": "مهندس"
   }
   ```
   - Returns: `{kyc_completed: boolean}`

5. **POST** `/investments/request`
   - Headers: `Authorization: Bearer <token>`
   - Body:
   ```json
   {
     "apartment_id": 1,
     "shares_requested": 5,
     "full_name": "أحمد محمد علي",
     "phone": "01234567890",
     "national_id": "12345678901234",
     "address": "123 شارع الجمهورية، القاهرة",
     "date_of_birth": "1990-01-15",
     "nationality": "مصري",
     "occupation": "مهندس",
     "referred_by_code": "REF123" // optional
   }
   ```
   - Returns: `{request_id, status, status_arabic, total_amount}`
   - **Purpose:** Real investment requiring admin approval

6. **GET** `/investments/requests`
   - Headers: `Authorization: Bearer <token>`
   - Returns: User's investment requests with status tracking

---

## 📱 New Screens to Implement

### 1. Admin Dashboard Screen (`admin/admin_dashboard_screen.dart`)
**Route:** `/admin/dashboard` (only show if `user.is_admin == true`)

**Design:**
- AppBar: "لوحة الإدارة" with admin badge icon (gold)
- **Stats Grid (2 columns):**
  - Total Users (Users icon, large number in gold)
  - Total Apartments (Building icon)
  - Total Cars (Car icon)
  - Pending Requests (Bell icon, RED badge if > 0)
  - Approved Requests (Checkmark icon, green)
  - Total Investments (Chart icon)
  - Total Platform Value (Money icon, large card with gold gradient)
- **Quick Actions:**
  - "مراجعة الطلبات" button (gold gradient) → Navigate to Admin Requests Screen
  - "إضافة شقة جديدة" button (outlined gold)

**Functionality:**
```dart
Future<void> loadAdminStats() async {
  final response = await apiService.get('/admin/stats');
  setState(() {
    stats = AdminStats.fromJson(response['data']);
  });
}
```

**Model:**
```dart
class AdminStats {
  final int totalUsers;
  final int totalApartments;
  final int totalCars;
  final int pendingRequests;
  final int approvedRequests;
  final int totalInvestments;
  final double totalPlatformValue;
}
```

---

### 2. Admin Requests Management Screen (`admin/admin_requests_screen.dart`)
**Route:** `/admin/requests`

**Design:**
- AppBar: "إدارة طلبات الاستثمار"
- **Tab Bar:**
  - الكل (All)
  - قيد الانتظار (Pending) - with badge count
  - تمت الموافقة (Approved)
  - مرفوض (Rejected)
- **Request Cards:**
  - User avatar + name + email
  - Apartment thumbnail + title
  - Shares requested: **5 حصص**
  - Total amount: **500,000 جنيه** (large, gold)
  - KYC Info Preview:
    - 📱 Phone: 01234567890
    - 🆔 National ID: 12345...
  - Status Badge (color-coded)
  - **Action Buttons (if pending):**
    - "✓ موافقة" (green solid button)
    - "✗ رفض" (red outlined button)

**Functionality:**
```dart
// Approve Request
Future<void> approveRequest(int requestId) async {
  await apiService.post('/admin/investment-requests/$requestId/action', {
    'action': 'approve',
    'admin_notes': 'تمت الموافقة'
  });
  refreshRequests();
}

// Reject Request
Future<void> rejectRequest(int requestId, String notes) async {
  // Show dialog for admin notes
  await apiService.post('/admin/investment-requests/$requestId/action', {
    'action': 'reject',
    'admin_notes': notes
  });
  refreshRequests();
}
```

---

### 3. KYC Form Screen (`kyc/kyc_form_screen.dart`)
**Route:** `/kyc/form`

**Design:**
- AppBar: "استكمال البيانات الشخصية"
- **Form Fields (RTL, Arabic):**
  1. رقم الهاتف (Phone) - TextFormField
  2. الرقم القومي (National ID) - 14 digits, validated
  3. العنوان الكامل (Address) - multiline TextFormField
  4. تاريخ الميلاد (Date of Birth) - DatePicker
  5. الجنسية (Nationality) - Dropdown or TextField
  6. الوظيفة (Occupation) - TextField
- **Submit Button:** "حفظ البيانات" (gold gradient, full width)

**Validation:**
- All fields required
- National ID must be 14 digits
- Phone must start with 01 and be 11 digits

**Functionality:**
```dart
Future<void> submitKYC() async {
  final response = await apiService.post('/user/kyc', {
    'phone': phoneController.text,
    'national_id': nationalIdController.text,
    'address': addressController.text,
    'date_of_birth': selectedDate.toString(),
    'nationality': nationalityController.text,
    'occupation': occupationController.text,
  });
  
  if (response['success']) {
    showSuccessSnackBar('تم حفظ بياناتك بنجاح');
    Navigator.pop(context);
  }
}
```

---

### 4. Investment Request Screen (`kyc/investment_request_screen.dart`)
**Route:** `/investments/request`

**Design:**
- AppBar: "طلب استثمار حقيقي"
- **Apartment Selection:**
  - Dropdown showing available apartments
  - Selected apartment details card (image, title, price, available shares)
- **Shares Selector:**
  - [-] Number [+] buttons (gold)
  - Total Amount: **500,000 جنيه** (calculated, large, gold)
- **KYC Section:**
  - If user has KYC data: Show pre-filled fields (read-only with edit button)
  - If not: Show KYC form fields (same as KYC Form Screen)
- **Referral Code (Optional):**
  - TextField: "كود الإحالة (اختياري)"
- **Info Alert:**
  - Blue info box: "سيتم مراجعة طلبك من قبل الإدارة وسيتم إخطارك بالنتيجة"
- **Submit Button:** "إرسال الطلب" (gold gradient, full width)

**Functionality:**
```dart
Future<void> submitInvestmentRequest() async {
  final response = await apiService.post('/investments/request', {
    'apartment_id': selectedApartment.id,
    'shares_requested': sharesCount,
    'full_name': fullNameController.text,
    'phone': phoneController.text,
    'national_id': nationalIdController.text,
    'address': addressController.text,
    'date_of_birth': dateOfBirth,
    'nationality': nationalityController.text,
    'occupation': occupationController.text,
    'referred_by_code': referralCodeController.text.isNotEmpty 
        ? referralCodeController.text 
        : null,
  });
  
  if (response['success']) {
    showSuccessDialog(
      'تم إرسال طلبك بنجاح\n'
      'رقم الطلب: ${response['data']['request_id']}\n'
      'الحالة: ${response['data']['status_arabic']}'
    );
    Navigator.pushNamed(context, '/investments/my-requests');
  }
}
```

---

### 5. My Investment Requests Screen (`kyc/my_requests_screen.dart`)
**Route:** `/investments/my-requests`

**Design:**
- AppBar: "طلباتي"
- **Request Cards:**
  - Apartment thumbnail + title
  - Shares: **5 حصص**
  - Total: **500,000 جنيه**
  - Status Badge:
    - 🟠 قيد الانتظار (Orange, pending)
    - 🟢 تمت الموافقة (Green, approved)
    - 🔴 مرفوض (Red, rejected)
  - Submission Date: "٢٣ نوفمبر ٢٠٢٥"
  - Admin Notes (if rejected): Red text box
- **Empty State:**
  - Icon: 📋
  - Text: "لا توجد طلبات استثمار بعد"
  - Button: "إنشاء طلب جديد" (gold) → Navigate to Investment Request Screen
- **Pull to Refresh**

**Functionality:**
```dart
Future<void> loadMyRequests() async {
  final response = await apiService.get('/investments/requests');
  setState(() {
    requests = (response['data']['requests'] as List)
        .map((r) => InvestmentRequest.fromJson(r))
        .toList();
  });
}
```

---

## 📦 New Models

### `investment_request.dart`
```dart
class InvestmentRequest {
  final int id;
  final int apartmentId;
  final String apartmentTitle;
  final int sharesRequested;
  final double totalAmount;
  final String status;
  final String statusArabic;
  final DateTime dateSubmitted;
  final String? adminNotes;

  factory InvestmentRequest.fromJson(Map<String, dynamic> json) {
    return InvestmentRequest(
      id: json['id'],
      apartmentId: json['apartment_id'],
      apartmentTitle: json['apartment_title'],
      sharesRequested: json['shares_requested'],
      totalAmount: json['total_amount'].toDouble(),
      status: json['status'],
      statusArabic: json['status_arabic'],
      dateSubmitted: DateTime.parse(json['date_submitted']),
      adminNotes: json['admin_notes'],
    );
  }
}
```

---

## 🎨 Color Scheme (Use Existing)
- Primary Gold: `Color(0xFFC2A14D)`
- Background: `Color(0xFF0A0A0A)`
- Success: `Color(0xFF10B981)` (green for approve)
- Error: `Color(0xFFEF4444)` (red for reject)
- Warning: `Color(0xFFF59E0B)` (orange for pending)

---

## 🔐 Admin Access Control
Check user's admin status before showing admin routes:
```dart
if (user.isAdmin) {
  // Show admin menu item
  ListTile(
    leading: Icon(Icons.admin_panel_settings, color: primaryGold),
    title: Text('لوحة الإدارة'),
    onTap: () => Navigator.pushNamed(context, '/admin/dashboard'),
  ),
}
```

---

## 📝 Implementation Checklist
- [ ] Create `models/investment_request.dart`
- [ ] Create `screens/admin/admin_dashboard_screen.dart`
- [ ] Create `screens/admin/admin_requests_screen.dart`
- [ ] Create `screens/kyc/kyc_form_screen.dart`
- [ ] Create `screens/kyc/investment_request_screen.dart`
- [ ] Create `screens/kyc/my_requests_screen.dart`
- [ ] Add routes to `main.dart`
- [ ] Add admin menu item to drawer/navigation
- [ ] Test with admin credentials: `admin@apartmentshare.com` / `admin123`
