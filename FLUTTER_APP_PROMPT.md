# Complete Flutter App Development Prompt for IPI Real Estate Investment Platform

## Project Overview
Build a complete Flutter mobile application for the IPI Real Estate Investment Platform that connects to an existing REST API backend. The app must support Arabic RTL layout and use the exact color scheme from the web application.

---

## 🎨 Exact Color Scheme (From CSS)

### Dark Mode (Default Theme)
```dart
// Primary Colors - Navy & Gold Theme
const Color primaryGold = Color(0xFFC2A14D);      // #C2A14D
const Color accentGold = Color(0xFFD8BD66);       // #D8BD66

// Backgrounds
const Color backgroundBlack = Color(0xFF0A0A0A);  // #0A0A0A (very dark navy)
const Color secondaryBlack = Color(0xFF050914);   // #050914 (almost black navy)

// Text Colors
const Color textLight = Color(0xFFFFFFFF);        // #FFFFFF
const Color textMuted = Color(0xFF999999);        // #999999

// Additional Colors
const Color success = Color(0xFF10B981);          // #10B981
const Color warning = Color(0xFFF59E0B);          // #F59E0B
const Color error = Color(0xFFEF4444);            // #EF4444
const Color info = Color(0xFF3B82F6);             // #3B82F6
const Color accentBeige = Color(0xFFE8D5B7);      // #E8D5B7
```

### Light Mode Theme
```dart
// Backgrounds
const Color backgroundLight = Color(0xFFF5F5F5);  // #F5F5F5
const Color secondaryLight = Color(0xFFFFFFFF);   // #FFFFFF

// Text (inverted)
const Color textDark = Color(0xFF1F2937);         // #1F2937
const Color textMutedLight = Color(0xFF6B7280);   // #6B7280

// Adjusted Gold for light mode
const Color primaryGoldLight = Color(0xFFB8860B); // #B8860B
const Color accentGoldLight = Color(0xFFDAA520);  // #DAA520
```

---

## 🔌 Backend API Endpoints

**Base URL:** `http://127.0.0.1:5001/api/v1`

**Note:** All endpoints are prefixed with `/api/v1`. The Flask server runs on `http://127.0.0.1:5001/`

### Authentication Endpoints
1. **POST** `/auth/register`
   - Body: `{"name": "string", "email": "string", "password": "string", "phone": "string" (optional)}`
   - Returns: `{user, access_token, refresh_token}`

2. **POST** `/auth/login`
   - Body: `{"email": "string", "password": "string"}`
   - Returns: `{user, access_token, refresh_token}`
   - **Default Credentials:** email: `admin@apartmentshare.com`, password: `admin123`

3. **GET** `/auth/me`
   - Headers: `Authorization: Bearer <token>`
   - Returns: Current user info

4. **POST** `/auth/refresh`
   - Headers: `Authorization: Bearer <refresh_token>`
   - Returns: New access token

### Apartment Endpoints
5. **GET** `/apartments`
   - Query params: `status`, `location`, `page`, `per_page`
   - Returns: List of apartments with pagination

6. **GET** `/apartments/{id}`
   - Returns: Apartment details with images

### Investment/Shares Endpoints
7. **POST** `/shares/purchase`
   - Headers: `Authorization: Bearer <token>`
   - Body: `{"apartment_id": int, "num_shares": int}`
   - Returns: Purchase confirmation

8. **GET** `/shares/my-investments`
   - Headers: `Authorization: Bearer <token>`
   - Returns: User's investment portfolio

### Wallet Endpoints
9. **GET** `/wallet/balance`
   - Headers: `Authorization: Bearer <token>`
   - Returns: Wallet and rewards balance

10. **POST** `/wallet/deposit`
    - Headers: `Authorization: Bearer <token>`
    - Body: `{"amount": float}`
    - Returns: New balance

11. **POST** `/wallet/withdraw`
    - Headers: `Authorization: Bearer <token>`
    - Body: `{"amount": float}`
    - Returns: New balance

12. **GET** `/wallet/transactions`
    - Headers: `Authorization: Bearer <token>`
    - Query params: `page`, `per_page`
    - Returns: Transaction history

### User Dashboard
13. **GET** `/user/dashboard`
    - Headers: `Authorization: Bearer <token>`
    - Returns: Complete dashboard data (wallet, investments, income, apartments count, recent transactions)

14. **PUT** `/user/profile`
    - Headers: `Authorization: Bearer <token>`
    - Body: `{"name": "string", "phone": "string"}`
    - Returns: Updated user info

### Car Endpoints
15. **GET** `/cars`
    - Query params: `page`, `per_page`
    - Returns: List of cars with pagination

16. **GET** `/cars/{id}`
    - Returns: Car details

17. **POST** `/cars/purchase`
    - Headers: `Authorization: Bearer <token>`
    - Body: `{"car_id": int, "num_shares": int}`
    - Returns: Purchase confirmation

18. **GET** `/cars/my-investments`
    - Headers: `Authorization: Bearer <token>`
    - Returns: User's car investments

### Admin Panel Endpoints (Admin Only)
19. **GET** `/admin/stats`
    - Headers: `Authorization: Bearer <token>`
    - Returns: `{total_users, total_apartments, total_cars, pending_requests, approved_requests, total_investments, total_platform_value}`
    - **Note:** Requires admin role (`is_admin: true`)

20. **GET** `/admin/investment-requests`
    - Headers: `Authorization: Bearer <token>`
    - Query params: `status` (pending/approved/rejected), `page`, `per_page`
    - Returns: List of investment requests for admin review
    - **Note:** Requires admin role

21. **POST** `/admin/investment-requests/{id}/action`
    - Headers: `Authorization: Bearer <token>`
    - Body: `{"action": "approve" or "reject", "admin_notes": "string"}`
    - Returns: Updated request status
    - **Note:** Requires admin role

### KYC & Investment Request Endpoints
22. **POST** `/user/kyc`
    - Headers: `Authorization: Bearer <token>`
    - Body: `{"phone": "string", "national_id": "string", "address": "string", "date_of_birth": "string", "nationality": "string", "occupation": "string"}`
    - Returns: `{kyc_completed: boolean}`
    - **Purpose:** Submit or update KYC information before making real investment requests

23. **POST** `/investments/request`
    - Headers: `Authorization: Bearer <token>`
    - Body: `{"apartment_id": int, "shares_requested": int, "full_name": "string", "phone": "string", "national_id": "string", "address": "string", "date_of_birth": "string", "nationality": "string", "occupation": "string", "referred_by_code": "string" (optional)}`
    - Returns: `{request_id, status, status_arabic, total_amount}`
    - **Purpose:** Create a real investment request that requires admin approval

24. **GET** `/investments/requests`
    - Headers: `Authorization: Bearer <token>`
    - Returns: List of user's investment requests with status
    - **Purpose:** Track investment request status (pending/approved/rejected)

---


## 📱 Required Screens

### 1. Splash Screen
- **Design:**
  - Dark navy gradient background (#0A0A0A to #050914)
  - Large gold apartment icon (size: 100)
  - App title "منصة الاستثمار العقاري IPI" in gold (#C2A14D)
  - Loading spinner in gold
- **Functionality:**
  - Check for stored JWT token
  - If token exists → navigate to Home
  - If no token → navigate to Login
  - Duration: 2-3 seconds

### 2. Login Screen
- **Design:**
  - Navy gradient background
  - Gold apartment icon (size: 80)
  - Title: "تسجيل الدخول" in gold
  - Email input field (dark background #050914, gold border #C2A14D)
  - Password input field (same styling)
  - Gold gradient button "دخول" (#C2A14D to #D8BD66)
  - "ليس لديك حساب؟ سجل الآن" link in gold
- **Functionality:**
  - Call POST `/auth/login`
  - Store access_token in SharedPreferences
  - Show loading indicator on button
  - Navigate to Home on success
  - Show error alert on failure
- **Pre-filled for testing:** email: admin@apartmentshare.com, password: admin123

### 3. Register Screen
- **Design:**
  - Same background as login
  - Title: "إنشاء حساب جديد"
  - Fields: Name, Email, Password, Phone (optional)
  - Gold gradient button "تسجيل"
  - "لديك حساب؟ سجل الدخول" link
- **Functionality:**
  - Call POST `/auth/register`
  - Store tokens
  - Navigate to Home

### 4. Home Dashboard (Landing Page)
- **Design:**
  - AppBar: Dark navy (#050914), title "لوحة التحكم" in gold, refresh icon button
  - Body background: #0A0A0A
  - **Stats Cards (4 cards in 2x2 grid):**
    1. Wallet Balance - Icon: account_balance_wallet (gold), value in gold
    2. Total Invested - Icon: trending_up (gold), value in gold
    3. Monthly Income - Icon: attach_money (gold), value in gold
    4. Apartments Count - Icon: apartment (gold), value in gold
  - Card styling: Dark navy background (#050914), rounded corners (16px), gold border (1px), shadow
  - **Section Title:** "العقارات المتاحة" in gold (size: 22, bold)
  - **Apartments List:**
    - Each apartment in a card (#050914 background)
    - Gold apartment icon (size: 40)
    - Title in white, bold
    - Subtitle: "السعر: {share_price} - متاح: {shares_available}" in light gray
    - Arrow icon in gold
    - Tap to navigate to Apartment Details
- **Functionality:**
  - Call GET `/user/dashboard` on load
  - Call GET `/apartments` for list
  - Pull-to-refresh functionality
  - Show loading spinner while fetching
  - Show error message if API fails with retry button

### 5. Apartment Details Screen
- **Design:**
  - AppBar: Title is apartment name in gold
  - Hero image placeholder (dark gray with gold apartment icon)
  - **Details Section:**
    - Title in gold (size: 24, bold)
    - Location with location icon (gold)
    - Description in white
  - **Investment Info Cards:**
    - Total Price
    - Share Price
    - Available Shares
    - Monthly Rent
    - Completion Percentage (progress bar in gold)
  - **Purchase Section:**
    - Number of shares selector (+ and - buttons in gold)
    - Total cost display in gold
    - "شراء الحصص" button (gold gradient)
- **Functionality:**
  - Call GET `/apartments/{id}`
  - Call POST `/shares/purchase` on buy button
  - Update wallet balance after purchase
  - Show success/error alerts

### 6. My Investments Screen
- **Design:**
  - AppBar: "استثماراتي" in gold
  - **Summary Cards:**
    - Total Invested
    - Monthly Expected Income
    - Number of Apartments
  - **Investments List:**
    - Each investment card shows:
      - Apartment image/icon
      - Apartment title
      - Shares owned
      - Total invested
      - Monthly income from this property
    - Card background: #050914, gold accents
- **Functionality:**
  - Call GET `/shares/my-investments`
  - Tap card to navigate to Apartment Details

### 7. Wallet Screen
- **Design:**
  - AppBar: "المحفظة" in gold
  - **Balance Card (large, prominent):**
    - Wallet icon (gold, size: 60)
    - Balance amount (very large, gold)
    - Rewards balance (smaller, light gold)
  - **Action Buttons:**
    - "إيداع" button (gold gradient)
    - "سحب" button (outlined gold)
  - **Transactions Section:**
    - Title: "المعاملات الأخيرة"
    - List of transactions:
      - Icon based on type (deposit: arrow_downward, withdrawal: arrow_upward, purchase: shopping_cart)
      - Description in white
      - Amount in gold (+ for deposits, - for withdrawals)
      - Date in gray
- **Functionality:**
  - Call GET `/wallet/balance`
  - Call GET `/wallet/transactions`
  - Deposit dialog: input amount, call POST `/wallet/deposit`
  - Withdraw dialog: input amount, call POST `/wallet/withdraw`

### 8. Profile Screen
- **Design:**
  - AppBar: "الملف الشخصي" in gold
  - **Profile Header:**
    - User icon (gold, size: 80)
    - Name in gold (size: 24)
    - Email in gray
  - **Info Cards:**
    - Phone number
    - Date joined
    - Member since
  - **Edit Button:** Gold gradient
  - **Logout Button:** Red outlined
- **Functionality:**
  - Call GET `/auth/me` to load data
  - Edit dialog: call PUT `/user/profile`
  - Logout: clear SharedPreferences, navigate to Login

### 9. How to Start (Tutorial Screen)
- **Design:** Based on the screenshot provided
  - Black background (#0A0A0A)
  - Title: "كيف تبدأ الاستثمار؟" in gold (centered, large)
  - Subtitle: "خطوات بسيطة للبدء في رحلتك الاستثمارية" in white
  - **4 Steps in horizontal layout:**
    1. Circle with number "1" (gold background #C2A14D)
       - Title: "إنشاء حساب" in gold
       - Description: "سجل حسابك معنا في دقائق معدودة" in white
    2. Circle with number "2" (gold)
       - Title: "اختر الأفضل" in gold
       - Description: "تصفح الوحدات والاستثمارات المتاحة واختر ما يناسبك مباشرة" in white
    3. Circle with number "3" (gold)
       - Title: "اشتر الحصص" in gold
       - Description: "حدد عدد الحصص التي تريد شراؤها" in white
    4. Circle with number "4" (gold)
       - Title: "احصل على الأرباح" in gold
       - Description: "استلم حصتك من الإيرادات (الإيجارات أو المبيعات) شهرياً" in white
  - Each step card: dark background, gold accents, rounded corners
- **Functionality:**
  - Show on first app launch
  - Skip button to go to Login
  - "ابدأ الآن" button to go to Register

### 9. Admin Dashboard Screen (Admin Only)
- **Design:**
  - AppBar: "لوحة الإدارة" in gold with admin badge icon
  - **Stats Grid (2 columns):**
    - Card for each stat with icon, number (large, gold), and label (white)
    - Total Users, Total Apartments, Total Cars
    - Pending Requests (red badge if > 0)
    - Approved Requests, Total Investments
    - Total Platform Value (largest card, gold gradient background)
  - **Quick Actions Section:**
    - "مراجعة الطلبات" button (gold gradient) → navigate to Requests Management
    - "إضافة شقة" button (outlined gold)
- **Functionality:**
  - Call GET `/admin/stats` to load dashboard
  - Check `userData.is_admin` to show/hide this screen
  - Refresh on pull-down

### 10. Admin Requests Management Screen (Admin Only)
- **Design:**
  - AppBar: "إدارة طلبات الاستثمار" in gold
  - **Filter Tabs:**
    - Tabs for: الكل (All), قيد الانتظار (Pending), تمت الموافقة (Approved), مرفوض (Rejected)
    - Selected tab in gold, others in gray
  - **Request Cards:**
    - User name and email
    - Apartment title with thumbnail
    - Shares requested & total amount (gold, large)
    - Submission date
    - KYC info preview (phone, national ID)
    - Status badge (color-coded: orange=pending, green=approved, red=rejected)
    - Action buttons (if pending):
      - "موافقة" (green button)
      - "رفض" (red button)
    - "ملاحظات الإدارة" field if rejected/approved
- **Functionality:**
  - Call GET `/admin/investment-requests?status={tab}`
  - Tap "موافقة" → Show confirmation dialog → Call POST `/admin/investment-requests/{id}/action` with `action: approve`
  - Tap "رفض" → Show dialog for admin notes → Call POST with `action: reject`
  - Refresh list after action

### 11. KYC Form Screen
- **Design:**
  - AppBar: "استكمال البيانات الشخصية" in gold
  - **Form Fields (Arabic RTL):**
    - الاسم الكامل (Full Name)
    - رقم الهاتف (Phone)
    - الرقم القومي (National ID)
    - العنوان الكامل (Address) - multi-line
    - تاريخ الميلاد (Date of Birth) - date picker
    - الجنسية (Nationality)
    - الوظيفة (Occupation)
  - **Submit Button:**
    - "حفظ البيانات" (gold gradient, full width)
- **Functionality:**
  - Call POST `/user/kyc` with form data
  - Show success message: "تم حفظ بياناتك بنجاح"
  - Navigate back or to Investment Request screen

### 12. Investment Request Screen
- **Design:**
  - AppBar: "طلب استثمار حقيقي" in gold
  - **Apartment Selection:**
    - Dropdown/picker to select apartment from available list
    - Show selected apartment details (title, price, available shares)
  - **Shares Input:**
    - Number of shares selector (+ and - buttons in gold)
    - Total amount display (gold, large, calculated)
  - **KYC Fields** (pre-filled if user submitted KYC):
    - Same fields as KYC Form Screen
  - **Referral Code (Optional):**
    - Text input for referral code
  - **Submit Button:**
    - "إرسال الطلب" (gold gradient, full width)
  - **Info Alert:**
    - "سيتم مراجعة طلبك من قبل الإدارة وسيتم إخطارك بالنتيجة"
- **Functionality:**
  - Call POST `/investments/request` with all data
  - Show success message with request ID and status
  - Navigate to My Investment Requests screen

### 13. My Investment Requests Screen
- **Design:**
  - AppBar: "طلباتي" in gold
  - **Request Cards:**
    - Apartment title
    - Shares requested & total amount
    - Status badge (color-coded)
    - Submission date
    - Admin notes (if rejected)
  - **Empty State:**
    - Icon and text: "لا توجد طلبات بعد"
    - "إنشاء طلب جديد" button (gold)
- **Functionality:**
  - Call GET `/investments/requests`
  - Tap card to view full request details
  - Pull-to-refresh

---


## 🛠️ Technical Requirements

### Dependencies (pubspec.yaml)
```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_localizations:
    sdk: flutter
  
  # State Management
  provider: ^6.1.1
  
  # HTTP & API
  http: ^1.2.0
  
  # Local Storage
  shared_preferences: ^2.2.2
  
  # Utilities
  intl: ^0.19.0
  
  # UI
  cupertino_icons: ^1.0.8
```

### Project Structure
```
lib/
├── main.dart
├── models/
│   ├── user.dart
│   ├── apartment.dart
│   ├── car.dart
│   ├── investment.dart
│   ├── investment_request.dart
│   └── transaction.dart
├── services/
│   ├── api_service.dart
│   └── auth_service.dart
├── screens/
│   ├── splash_screen.dart
│   ├── login_screen.dart
│   ├── register_screen.dart
│   ├── home_screen.dart
│   ├── apartment_details_screen.dart
│   ├── investments_screen.dart
│   ├── wallet_screen.dart
│   ├── profile_screen.dart
│   ├── admin/
│   │   ├── admin_dashboard_screen.dart
│   │   └── admin_requests_screen.dart
│   ├── kyc/
│   │   ├── kyc_form_screen.dart
│   │   ├── investment_request_screen.dart
│   │   └── my_requests_screen.dart
│   ├── profile_screen.dart
│   └── tutorial_screen.dart
├── widgets/
│   ├── stat_card.dart
│   ├── apartment_card.dart
│   ├── transaction_item.dart
│   └── custom_button.dart
└── utils/
    ├── theme.dart
    ├── constants.dart
    └── helpers.dart
```

### API Service Implementation
```dart
class ApiService {
  // Flask API runs on http://127.0.0.1:5001/
  // All endpoints are prefixed with /api/v1
  static const String baseUrl = 'http://127.0.0.1:5001/api/v1';
  String? _token;

  // Load token from SharedPreferences
  Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('access_token');
  }

  // Save token to SharedPreferences
  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token);
    _token = token;
  }

  // Clear token
  Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    _token = null;
  }

  // Headers with auth
  Map<String, String> get headers => {
    'Content-Type': 'application/json; charset=UTF-8',
    if (_token != null) 'Authorization': 'Bearer $_token',
  };

  // Implement all API calls here...
}
```

### Theme Configuration
```dart
ThemeData darkTheme = ThemeData(
  brightness: Brightness.dark,
  primaryColor: const Color(0xFFC2A14D),
  scaffoldBackgroundColor: const Color(0xFF0A0A0A),
  colorScheme: const ColorScheme.dark(
    primary: Color(0xFFC2A14D),
    secondary: Color(0xFFD8BD66),
    surface: Color(0xFF050914),
    background: Color(0xFF0A0A0A),
  ),
  appBarTheme: const AppBarTheme(
    backgroundColor: Color(0xFF050914),
    elevation: 0,
    centerTitle: true,
    titleTextStyle: TextStyle(
      fontSize: 20,
      fontWeight: FontWeight.bold,
      color: Color(0xFFC2A14D),
    ),
  ),
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: const Color(0xFFC2A14D),
      foregroundColor: const Color(0xFF0A0A0A),
      padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
    ),
  ),
  cardTheme: CardTheme(
    color: const Color(0xFF050914),
    elevation: 4,
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
  ),
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    fillColor: const Color(0xFF050914),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: const BorderSide(color: Color(0xFFC2A14D)),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: const BorderSide(color: Color(0xFFC2A14D), width: 2),
    ),
    labelStyle: const TextStyle(color: Color(0xFFC2A14D)),
  ),
);
```

### Arabic RTL Support
```dart
MaterialApp(
  title: 'منصة الاستثمار العقاري',
  locale: const Locale('ar', 'EG'),
  supportedLocales: const [Locale('ar', 'EG')],
  localizationsDelegates: const [
    GlobalMaterialLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
  ],
  theme: darkTheme,
  home: const SplashScreen(),
);
```

---

## 🎯 Key Features to Implement

1. **JWT Authentication:**
   - Store tokens in SharedPreferences
   - Auto-login if token exists
   - Refresh token when expired
   - Logout clears tokens

2. **Error Handling:**
   - Show user-friendly Arabic error messages
   - Retry buttons for failed API calls
   - Loading states for all async operations

3. **Responsive Design:**
   - Works on all screen sizes
   - Proper padding and spacing
   - Scrollable content

4. **Arabic Support:**
   - RTL layout direction
   - Arabic fonts (Cairo, Tajawal)
   - Arabic number formatting
   - Arabic date formatting

5. **Smooth Animations:**
   - Page transitions
   - Button press effects
   - Card hover effects
   - Loading spinners

6. **Pull-to-Refresh:**
   - On Home screen
   - On Investments screen
   - On Wallet screen

---

## 📝 Important Notes

1. **API Base URL:** Change to your local IP address when testing on physical device (e.g., `http://192.168.1.27:5001/api/v1`)

2. **JWT Token Format:** The backend returns tokens as strings. Store the `access_token` from login/register response.

3. **Error Response Format:**
   ```json
   {
     "success": false,
     "error": {
       "code": "ERROR_CODE",
       "message": "رسالة الخطأ بالعربية"
     }
   }
   ```

4. **Success Response Format:**
   ```json
   {
     "success": true,
     "message": "رسالة النجاح",
     "data": { ... }
   }
   ```

5. **Default Test Account:**
   - Email: admin@apartmentshare.com
   - Password: admin123

---

## 🚀 Deliverables

1. Complete Flutter project with all screens
2. API integration for all 14 endpoints
3. Proper error handling and loading states
4. Arabic RTL support throughout
5. Exact color scheme matching the web app
6. Smooth animations and transitions
7. Working authentication flow
8. Landing page (Home Dashboard) with real data from database
9. Tutorial/How to Start screen matching the provided design

---

## ✅ Testing Checklist

- [ ] Login with test credentials works
- [ ] Dashboard loads with real data
- [ ] Apartments list displays correctly
- [ ] Apartment details screen shows all info
- [ ] Share purchase works and updates wallet
- [ ] Wallet balance displays correctly
- [ ] Deposit/Withdraw functions work
- [ ] Transactions list loads
- [ ] My Investments shows user's portfolio
- [ ] Profile screen displays user info
- [ ] Logout clears session
- [ ] All colors match the CSS exactly
- [ ] Arabic text displays correctly (RTL)
- [ ] All icons are gold (#C2A14D)
- [ ] Loading states show properly
- [ ] Error messages display in Arabic
- [ ] Tutorial screen matches the design

---

**Build this complete Flutter application with all the specifications above. Ensure every screen uses the exact colors from the CSS, implements full API integration, and provides a smooth, professional user experience in Arabic.**
