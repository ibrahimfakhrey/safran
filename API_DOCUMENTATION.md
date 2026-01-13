# API Documentation

Base URL: `/api/v1`

## Authentication

### Register
- **Method:** `POST`
- **URL:** `/auth/register`
- **Description:** Register a new user account.
- **Request Body:**
  ```json
  {
      "name": "Full Name",
      "email": "user@example.com",
      "password": "password123",
      "phone": "01234567890" // Optional
  }
  ```
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم إنشاء الحساب بنجاح",
      "data": {
          "user": { ... },
          "access_token": "jwt_access_token",
          "refresh_token": "jwt_refresh_token"
      }
  }
  ```

### Login
- **Method:** `POST`
- **URL:** `/auth/login`
- **Description:** Authenticate a user and receive tokens.
- **Request Body:**
  ```json
  {
      "email": "user@example.com",
      "password": "password123"
  }
  ```
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم تسجيل الدخول بنجاح",
      "data": {
          "user": { ... },
          "access_token": "jwt_access_token",
          "refresh_token": "jwt_refresh_token"
      }
  }
  ```

### Get Current User
- **Method:** `GET`
- **URL:** `/auth/me`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Get current authenticated user info.
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم جلب بيانات المستخدم بنجاح",
      "data": {
          "user": { ... }
      }
  }
  ```

### Refresh Token
- **Method:** `POST`
- **URL:** `/auth/refresh`
- **Headers:** `Authorization: Bearer <refresh_token>`
- **Description:** Refresh the access token using a refresh token.
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم تحديث الرمز بنجاح",
      "data": {
          "access_token": "new_access_token"
      }
  }
  ```

## Apartments

### Get Apartments
- **Method:** `GET`
- **URL:** `/apartments`
- **Query Parameters:**
  - `status`: 'available', 'closed', 'new' (Optional)
  - `location`: Filter by location (Optional)
  - `page`: Page number (Default: 1)
  - `per_page`: Items per page (Default: 10)
- **Description:** Get a list of apartments with optional filters.
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم جلب العقارات بنجاح",
      "data": {
          "apartments": [ ... ],
          "total": 10,
          "page": 1,
          "per_page": 10,
          "total_pages": 1
      }
  }
  ```

### Get Apartment Details
- **Method:** `GET`
- **URL:** `/apartments/<id>`
- **Description:** Get detailed information about a specific apartment.
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم جلب تفاصيل العقار بنجاح",
      "data": {
          "apartment": { ... }
      }
  }
  ```

## Cars

### Get Cars
- **Method:** `GET`
- **URL:** `/cars`
- **Query Parameters:**
  - `page`: Page number (Default: 1)
  - `per_page`: Items per page (Default: 10)
- **Description:** Get a list of cars.
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم جلب السيارات بنجاح",
      "data": {
          "cars": [ ... ],
          "total": 5,
          "page": 1,
          "per_page": 10,
          "total_pages": 1
      }
  }
  ```

### Get Car Details
- **Method:** `GET`
- **URL:** `/cars/<id>`
- **Description:** Get detailed information about a specific car.
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم جلب تفاصيل السيارة بنجاح",
      "data": {
          "car": { ... }
      }
  }
  ```

## Shares & Investments

### Purchase Apartment Shares
- **Method:** `POST`
- **URL:** `/shares/purchase`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Purchase shares in an apartment directly (Wallet balance must be sufficient).
- **Request Body:**
  ```json
  {
      "apartment_id": 1,
      "num_shares": 5
  }
  ```
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم شراء الحصص بنجاح",
      "data": {
          "new_balance": 45000.0,
          "shares_purchased": 5,
          "total_cost": 5000.0,
          "apartment": { ... }
      }
  }
  ```

### Purchase Car Shares
- **Method:** `POST`
- **URL:** `/cars/purchase`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Purchase shares in a car directly.
- **Request Body:**
  ```json
  {
      "car_id": 1,
      "num_shares": 2
  }
  ```
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم شراء حصص السيارة بنجاح",
      "data": {
          "new_balance": 40000.0,
          "shares_purchased": 2,
          "car": { ... }
      }
  }
  ```

### Get My Apartment Investments
- **Method:** `GET`
- **URL:** `/shares/my-investments`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Get the user's portfolio of apartment investments.
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم جلب الاستثمارات بنجاح",
      "data": {
          "investments": [ ... ],
          "total_invested": 10000.0,
          "monthly_expected_income": 500.0,
          "total_apartments": 2
      }
  }
  ```

### Get My Car Investments
- **Method:** `GET`
- **URL:** `/cars/my-investments`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Get the user's portfolio of car investments.
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم جلب استثمارات السيارات بنجاح",
      "data": {
          "investments": [ ... ]
      }
  }
  ```

## Wallet

### Get Wallet Balance
- **Method:** `GET`
- **URL:** `/wallet/balance`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Get the user's current wallet balance.
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم جلب الرصيد بنجاح",
      "data": {
          "wallet_balance": 5000.0,
          "rewards_balance": 100.0,
          "total_balance": 5100.0
      }
  }
  ```

### Deposit to Wallet
- **Method:** `POST`
- **URL:** `/wallet/deposit`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Add funds to the wallet (Simulation).
- **Request Body:**
  ```json
  {
      "amount": 10000
  }
  ```
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم الإيداع بنجاح",
      "data": {
          "new_balance": 15000.0,
          "amount_deposited": 10000
      }
  }
  ```

### Withdraw from Wallet
- **Method:** `POST`
- **URL:** `/wallet/withdraw`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Withdraw funds from the wallet.
- **Request Body:**
  ```json
  {
      "amount": 5000
  }
  ```
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم السحب بنجاح",
      "data": {
          "new_balance": 10000.0,
          "amount_withdrawn": 5000
      }
  }
  ```

### Get Transactions
- **Method:** `GET`
- **URL:** `/wallet/transactions`
- **Headers:** `Authorization: Bearer <token>`
- **Query Parameters:**
  - `page`: Page number (Default: 1)
  - `per_page`: Items per page (Default: 20)
- **Description:** Get user's transaction history.
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم جلب المعاملات بنجاح",
      "data": {
          "transactions": [ ... ],
          "total": 50,
          "page": 1,
          "per_page": 20,
          "total_pages": 3
      }
  }
  ```

## User Dashboard & Profile

### Get Dashboard
- **Method:** `GET`
- **URL:** `/user/dashboard`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Get aggregated data for the user dashboard.
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم جلب بيانات لوحة التحكم بنجاح",
      "data": {
          "user": { ... },
          "wallet_balance": 5000.0,
          "total_invested": 10000.0,
          "monthly_expected_income": 500.0,
          "apartments_count": 2,
          "total_shares": 10,
          "recent_transactions": [ ... ]
      }
  }
  ```

### Update Profile
- **Method:** `PUT`
- **URL:** `/user/profile`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Update user profile information.
- **Request Body:**
  ```json
  {
      "name": "New Name",
      "phone": "01234567890"
  }
  ```
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم تحديث الملف الشخصي بنجاح",
      "data": {
          "user": { ... }
      }
  }
  ```

## KYC & Investment Requests (Real Investment)

### Submit KYC
- **Method:** `POST`
- **URL:** `/user/kyc`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Submit or update KYC (Know Your Customer) information.
- **Request Body:**
  ```json
  {
      "phone": "01000000000",
      "national_id": "12345678901234",
      "address": "Cairo, Egypt",
      "date_of_birth": "1990-01-01",
      "nationality": "Egyptian",
      "occupation": "Engineer"
  }
  ```
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم تحديث معلومات KYC بنجاح",
      "data": {
          "kyc_completed": true
      }
  }
  ```

### Create Investment Request
- **Method:** `POST`
- **URL:** `/investments/request`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Submit a request to invest (requires admin approval and manual payment verification).
- **Request Body:**
  ```json
  {
      "apartment_id": 1,
      "shares_requested": 10,
      "full_name": "Full Name",
      "phone": "01000000000",
      "national_id": "12345678901234",
      "address": "Cairo, Egypt",
      "date_of_birth": "1990-01-01",
      "nationality": "Egyptian",
      "occupation": "Engineer",
      "referred_by_code": "REF123" // Optional
  }
  ```
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم إرسال طلب الاستثمار بنجاح",
      "data": {
          "request_id": 1,
          "status": "pending",
          "status_arabic": "قيد الانتظار",
          "total_amount": 10000.0
      }
  }
  ```

### Get My Investment Requests
- **Method:** `GET`
- **URL:** `/investments/requests`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Get a list of the user's investment requests.
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم جلب طلبات الاستثمار بنجاح",
      "data": {
          "requests": [ ... ]
      }
  }
  ```

## Admin API

### Get Admin Stats
- **Method:** `GET`
- **URL:** `/admin/stats`
- **Headers:** `Authorization: Bearer <token>` (Admin only)
- **Description:** Get high-level statistics for the admin dashboard.
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم جلب الإحصائيات بنجاح",
      "data": {
          "total_users": 100,
          "total_apartments": 5,
          "total_cars": 3,
          "pending_requests": 2,
          "approved_requests": 10,
          "total_investments": 50,
          "total_platform_value": 5000000.0
      }
  }
  ```

### Get Investment Requests (Admin)
- **Method:** `GET`
- **URL:** `/admin/investment-requests`
- **Headers:** `Authorization: Bearer <token>` (Admin only)
- **Query Parameters:**
  - `status`: Filter by status (Optional)
  - `page`: Page number (Default: 1)
  - `per_page`: Items per page (Default: 20)
- **Description:** Get all investment requests submitted by users.
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم جلب الطلبات بنجاح",
      "data": {
          "requests": [ ... ],
          "total": 10,
          "page": 1,
          "per_page": 20,
          "total_pages": 1
      }
  }
  ```

### Action on Investment Request
- **Method:** `POST`
- **URL:** `/admin/investment-requests/<id>/action`
- **Headers:** `Authorization: Bearer <token>` (Admin only)
- **Description:** Approve or reject an investment request.
- **Request Body:**
  ```json
  {
      "action": "approve", // or "reject"
      "admin_notes": "Approved after verifying payment."
  }
  ```
- **Success Response:**
  ```json
  {
      "success": true,
      "message": "تم تمت الموافقة على الطلب بنجاح",
      "data": {
          "request": {
              "id": 1,
              "status": "approved",
              "status_arabic": "تمت الموافقة"
          }
      }
  }
  ```
