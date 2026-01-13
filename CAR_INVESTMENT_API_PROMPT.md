# Car Investment Request API - Flutter Integration Guide

## Overview

This document provides the API specifications for implementing car investment requests with KYC data in the Flutter mobile app. The car investment flow mirrors the apartment investment flow but uses car-specific endpoints.

---

## Base URL

```
http://127.0.0.1:5000/api/v1
```

For production, replace with your production server URL.

---

## Authentication

All endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## API Endpoints

### 1. Create Car Investment Request

Creates a new investment request for a car with KYC documents.

**Endpoint:** `POST /cars/investment-request`

**Content-Type:** `multipart/form-data`

#### Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `car_id` | int | Yes | ID of the car to invest in |
| `shares_requested` | int | Yes | Number of shares to purchase |
| `full_name` | string | Yes | Full legal name (Arabic/English) |
| `phone` | string | Yes | Phone number with country code |
| `national_id` | string | Yes | National ID / Passport number |
| `address` | string | Yes | Full residential address |
| `date_of_birth` | string | Yes | Date of birth (format: YYYY-MM-DD) |
| `nationality` | string | Yes | Nationality |
| `occupation` | string | Yes | Current occupation |
| `referred_by_code` | string | No | Referral code (if referred by another investor) |
| `id_document_front` | file | Yes | Front side of ID document (image/pdf) |
| `id_document_back` | file | Yes | Back side of ID document (image/pdf) |
| `proof_of_address` | file | Yes | Proof of address document (image/pdf) |

#### Success Response (201 Created)

```json
{
    "success": true,
    "message": "تم إرسال طلب الاستثمار في السيارة بنجاح",
    "data": {
        "request_id": 1,
        "car_id": 7,
        "car_title": "تويوتا كامري 2024",
        "shares_requested": 2,
        "total_amount": 4800.0,
        "status": "pending",
        "status_arabic": "قيد الانتظار",
        "date_submitted": "2025-12-11T10:30:00"
    }
}
```

#### Error Responses

**Missing Fields (400)**
```json
{
    "success": false,
    "error": {
        "code": "MISSING_FIELDS",
        "message": "الحقل full_name مطلوب"
    }
}
```

**Missing Files (400)**
```json
{
    "success": false,
    "error": {
        "code": "MISSING_FILES",
        "message": "الملف id_document_front مطلوب"
    }
}
```

**Car Not Found (404)**
```json
{
    "success": false,
    "error": {
        "code": "CAR_NOT_FOUND",
        "message": "السيارة غير موجودة"
    }
}
```

**Insufficient Shares (400)**
```json
{
    "success": false,
    "error": {
        "code": "INSUFFICIENT_SHARES",
        "message": "عدد الحصص المطلوبة (5) غير متاح. المتاح: 3"
    }
}
```

**Duplicate Request (400)**
```json
{
    "success": false,
    "error": {
        "code": "DUPLICATE_REQUEST",
        "message": "لديك طلب استثمار قيد الانتظار لهذه السيارة"
    }
}
```

---

### 2. Get User's Car Investment Requests

Retrieves all car investment requests for the authenticated user.

**Endpoint:** `GET /cars/investment-requests`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status: `pending`, `under_review`, `approved`, `rejected`, `documents_missing` |

#### Success Response (200 OK)

```json
{
    "success": true,
    "message": "تم جلب طلبات استثمار السيارات بنجاح",
    "data": {
        "requests": [
            {
                "id": 1,
                "car_id": 7,
                "car_title": "تويوتا كامري 2024",
                "car_image": "cars/toyota_camry.jpg",
                "shares_requested": 2,
                "total_amount": 4800.0,
                "status": "pending",
                "status_arabic": "قيد الانتظار",
                "date_submitted": "2025-12-11T10:30:00",
                "date_reviewed": null,
                "admin_notes": null,
                "missing_documents": null,
                "contract_pdf": null
            },
            {
                "id": 2,
                "car_id": 5,
                "car_title": "هوندا أكورد 2024",
                "car_image": "cars/honda_accord.jpg",
                "shares_requested": 1,
                "total_amount": 2400.0,
                "status": "approved",
                "status_arabic": "تمت الموافقة",
                "date_submitted": "2025-12-10T15:00:00",
                "date_reviewed": "2025-12-11T09:00:00",
                "admin_notes": null,
                "missing_documents": null,
                "contract_pdf": "contracts/car_contract_2.pdf"
            }
        ]
    }
}
```

---

### 3. Get Car Investment Request Details

Retrieves detailed information about a specific investment request.

**Endpoint:** `GET /cars/investment-requests/{request_id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request_id` | int | Yes | ID of the investment request |

#### Success Response (200 OK)

```json
{
    "success": true,
    "message": "تم جلب تفاصيل طلب الاستثمار بنجاح",
    "data": {
        "id": 1,
        "car_id": 7,
        "car_title": "تويوتا كامري 2024",
        "car_image": "cars/toyota_camry.jpg",
        "car_location": "القاهرة، مصر",
        "shares_requested": 2,
        "share_price": 2400.0,
        "total_amount": 4800.0,
        "monthly_income": 200.0,
        "status": "pending",
        "status_arabic": "قيد الانتظار",
        "date_submitted": "2025-12-11T10:30:00",
        "date_reviewed": null,
        "admin_notes": null,
        "missing_documents": null,
        "contract_pdf": null,
        "kyc_data": {
            "full_name": "محمد أحمد علي",
            "phone": "+201234567890",
            "national_id": "29901011234567",
            "address": "123 شارع التحرير، القاهرة، مصر",
            "date_of_birth": "1999-01-01",
            "nationality": "مصري",
            "occupation": "مهندس برمجيات"
        }
    }
}
```

#### Error Response (404 Not Found)

```json
{
    "success": false,
    "error": {
        "code": "REQUEST_NOT_FOUND",
        "message": "طلب الاستثمار غير موجود"
    }
}
```

---

## Request Status Values

| Status | Arabic | Description |
|--------|--------|-------------|
| `pending` | قيد الانتظار | Request submitted, awaiting review |
| `under_review` | قيد المراجعة | Admin is reviewing the request |
| `approved` | تمت الموافقة | Request approved, shares allocated |
| `rejected` | مرفوض | Request rejected (check admin_notes) |
| `documents_missing` | مستندات ناقصة | Some documents need to be resubmitted |

---

## Flutter Implementation Example

### 1. Model Class

```dart
class CarInvestmentRequest {
  final int id;
  final int carId;
  final String? carTitle;
  final String? carImage;
  final int sharesRequested;
  final double totalAmount;
  final String status;
  final String statusArabic;
  final DateTime? dateSubmitted;
  final DateTime? dateReviewed;
  final String? adminNotes;
  final String? missingDocuments;
  final String? contractPdf;

  CarInvestmentRequest({
    required this.id,
    required this.carId,
    this.carTitle,
    this.carImage,
    required this.sharesRequested,
    required this.totalAmount,
    required this.status,
    required this.statusArabic,
    this.dateSubmitted,
    this.dateReviewed,
    this.adminNotes,
    this.missingDocuments,
    this.contractPdf,
  });

  factory CarInvestmentRequest.fromJson(Map<String, dynamic> json) {
    return CarInvestmentRequest(
      id: json['id'],
      carId: json['car_id'],
      carTitle: json['car_title'],
      carImage: json['car_image'],
      sharesRequested: json['shares_requested'],
      totalAmount: (json['total_amount'] as num).toDouble(),
      status: json['status'],
      statusArabic: json['status_arabic'],
      dateSubmitted: json['date_submitted'] != null 
          ? DateTime.parse(json['date_submitted']) 
          : null,
      dateReviewed: json['date_reviewed'] != null 
          ? DateTime.parse(json['date_reviewed']) 
          : null,
      adminNotes: json['admin_notes'],
      missingDocuments: json['missing_documents'],
      contractPdf: json['contract_pdf'],
    );
  }
}
```

### 2. API Service

```dart
import 'dart:io';
import 'package:dio/dio.dart';

class CarInvestmentService {
  final Dio _dio;
  final String baseUrl = 'http://127.0.0.1:5000/api/v1';

  CarInvestmentService(this._dio);

  Future<Map<String, dynamic>> createCarInvestmentRequest({
    required int carId,
    required int sharesRequested,
    required String fullName,
    required String phone,
    required String nationalId,
    required String address,
    required String dateOfBirth,
    required String nationality,
    required String occupation,
    required File idDocumentFront,
    required File idDocumentBack,
    required File proofOfAddress,
    String? referredByCode,
  }) async {
    try {
      FormData formData = FormData.fromMap({
        'car_id': carId,
        'shares_requested': sharesRequested,
        'full_name': fullName,
        'phone': phone,
        'national_id': nationalId,
        'address': address,
        'date_of_birth': dateOfBirth,
        'nationality': nationality,
        'occupation': occupation,
        if (referredByCode != null) 'referred_by_code': referredByCode,
        'id_document_front': await MultipartFile.fromFile(
          idDocumentFront.path,
          filename: idDocumentFront.path.split('/').last,
        ),
        'id_document_back': await MultipartFile.fromFile(
          idDocumentBack.path,
          filename: idDocumentBack.path.split('/').last,
        ),
        'proof_of_address': await MultipartFile.fromFile(
          proofOfAddress.path,
          filename: proofOfAddress.path.split('/').last,
        ),
      });

      final response = await _dio.post(
        '$baseUrl/cars/investment-request',
        data: formData,
      );

      return response.data;
    } on DioException catch (e) {
      throw e.response?.data ?? {'error': {'message': 'حدث خطأ في الاتصال'}};
    }
  }

  Future<List<CarInvestmentRequest>> getCarInvestmentRequests({
    String? status,
  }) async {
    try {
      final response = await _dio.get(
        '$baseUrl/cars/investment-requests',
        queryParameters: status != null ? {'status': status} : null,
      );

      if (response.data['success']) {
        final List<dynamic> requestsJson = response.data['data']['requests'];
        return requestsJson
            .map((json) => CarInvestmentRequest.fromJson(json))
            .toList();
      }
      throw response.data['error']['message'];
    } on DioException catch (e) {
      throw e.response?.data?['error']?['message'] ?? 'حدث خطأ في الاتصال';
    }
  }

  Future<Map<String, dynamic>> getCarInvestmentRequestDetails(int requestId) async {
    try {
      final response = await _dio.get(
        '$baseUrl/cars/investment-requests/$requestId',
      );

      return response.data;
    } on DioException catch (e) {
      throw e.response?.data ?? {'error': {'message': 'حدث خطأ في الاتصال'}};
    }
  }
}
```

### 3. KYC Form Widget Example

```dart
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

class CarKycFormScreen extends StatefulWidget {
  final int carId;
  final int sharesRequested;

  const CarKycFormScreen({
    Key? key,
    required this.carId,
    required this.sharesRequested,
  }) : super(key: key);

  @override
  State<CarKycFormScreen> createState() => _CarKycFormScreenState();
}

class _CarKycFormScreenState extends State<CarKycFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _fullNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _nationalIdController = TextEditingController();
  final _addressController = TextEditingController();
  final _dateOfBirthController = TextEditingController();
  final _nationalityController = TextEditingController();
  final _occupationController = TextEditingController();
  final _referralCodeController = TextEditingController();

  File? _idFront;
  File? _idBack;
  File? _proofOfAddress;
  bool _isLoading = false;

  final ImagePicker _picker = ImagePicker();

  Future<void> _pickImage(String type) async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    if (image != null) {
      setState(() {
        switch (type) {
          case 'front':
            _idFront = File(image.path);
            break;
          case 'back':
            _idBack = File(image.path);
            break;
          case 'address':
            _proofOfAddress = File(image.path);
            break;
        }
      });
    }
  }

  Future<void> _submitRequest() async {
    if (!_formKey.currentState!.validate()) return;
    if (_idFront == null || _idBack == null || _proofOfAddress == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('يرجى تحميل جميع المستندات المطلوبة')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final service = CarInvestmentService(/* your dio instance */);
      final result = await service.createCarInvestmentRequest(
        carId: widget.carId,
        sharesRequested: widget.sharesRequested,
        fullName: _fullNameController.text,
        phone: _phoneController.text,
        nationalId: _nationalIdController.text,
        address: _addressController.text,
        dateOfBirth: _dateOfBirthController.text,
        nationality: _nationalityController.text,
        occupation: _occupationController.text,
        idDocumentFront: _idFront!,
        idDocumentBack: _idBack!,
        proofOfAddress: _proofOfAddress!,
        referredByCode: _referralCodeController.text.isNotEmpty
            ? _referralCodeController.text
            : null,
      );

      if (result['success']) {
        // Navigate to success screen
        Navigator.pushReplacementNamed(
          context,
          '/car-investment-success',
          arguments: result['data'],
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('طلب استثمار في سيارة'),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Personal Information Section
            const Text(
              'المعلومات الشخصية',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            
            TextFormField(
              controller: _fullNameController,
              decoration: const InputDecoration(
                labelText: 'الاسم الكامل',
                border: OutlineInputBorder(),
              ),
              validator: (v) => v?.isEmpty ?? true ? 'مطلوب' : null,
            ),
            const SizedBox(height: 12),

            TextFormField(
              controller: _phoneController,
              decoration: const InputDecoration(
                labelText: 'رقم الهاتف',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.phone,
              validator: (v) => v?.isEmpty ?? true ? 'مطلوب' : null,
            ),
            const SizedBox(height: 12),

            TextFormField(
              controller: _nationalIdController,
              decoration: const InputDecoration(
                labelText: 'رقم الهوية / جواز السفر',
                border: OutlineInputBorder(),
              ),
              validator: (v) => v?.isEmpty ?? true ? 'مطلوب' : null,
            ),
            const SizedBox(height: 12),

            TextFormField(
              controller: _addressController,
              decoration: const InputDecoration(
                labelText: 'العنوان',
                border: OutlineInputBorder(),
              ),
              maxLines: 2,
              validator: (v) => v?.isEmpty ?? true ? 'مطلوب' : null,
            ),
            const SizedBox(height: 12),

            TextFormField(
              controller: _dateOfBirthController,
              decoration: const InputDecoration(
                labelText: 'تاريخ الميلاد (YYYY-MM-DD)',
                border: OutlineInputBorder(),
              ),
              validator: (v) => v?.isEmpty ?? true ? 'مطلوب' : null,
            ),
            const SizedBox(height: 12),

            TextFormField(
              controller: _nationalityController,
              decoration: const InputDecoration(
                labelText: 'الجنسية',
                border: OutlineInputBorder(),
              ),
              validator: (v) => v?.isEmpty ?? true ? 'مطلوب' : null,
            ),
            const SizedBox(height: 12),

            TextFormField(
              controller: _occupationController,
              decoration: const InputDecoration(
                labelText: 'المهنة',
                border: OutlineInputBorder(),
              ),
              validator: (v) => v?.isEmpty ?? true ? 'مطلوب' : null,
            ),
            const SizedBox(height: 12),

            TextFormField(
              controller: _referralCodeController,
              decoration: const InputDecoration(
                labelText: 'كود الإحالة (اختياري)',
                border: OutlineInputBorder(),
              ),
            ),

            const SizedBox(height: 24),
            const Text(
              'المستندات المطلوبة',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

            // Document Upload Buttons
            _buildDocumentUploader(
              'الهوية - الوجه الأمامي',
              _idFront,
              () => _pickImage('front'),
            ),
            const SizedBox(height: 12),

            _buildDocumentUploader(
              'الهوية - الوجه الخلفي',
              _idBack,
              () => _pickImage('back'),
            ),
            const SizedBox(height: 12),

            _buildDocumentUploader(
              'إثبات العنوان',
              _proofOfAddress,
              () => _pickImage('address'),
            ),

            const SizedBox(height: 32),

            ElevatedButton(
              onPressed: _isLoading ? null : _submitRequest,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _isLoading
                  ? const CircularProgressIndicator()
                  : const Text('إرسال الطلب'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDocumentUploader(String label, File? file, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(
            color: file != null ? Colors.green : Colors.grey,
          ),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Icon(
              file != null ? Icons.check_circle : Icons.upload_file,
              color: file != null ? Colors.green : Colors.grey,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                file != null ? 'تم التحميل: ${file.path.split('/').last}' : label,
                style: TextStyle(
                  color: file != null ? Colors.green : Colors.black87,
                ),
              ),
            ),
            if (file != null)
              IconButton(
                icon: const Icon(Icons.close),
                onPressed: () {
                  setState(() {
                    if (label.contains('الأمامي')) _idFront = null;
                    if (label.contains('الخلفي')) _idBack = null;
                    if (label.contains('العنوان')) _proofOfAddress = null;
                  });
                },
              ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _fullNameController.dispose();
    _phoneController.dispose();
    _nationalIdController.dispose();
    _addressController.dispose();
    _dateOfBirthController.dispose();
    _nationalityController.dispose();
    _occupationController.dispose();
    _referralCodeController.dispose();
    super.dispose();
  }
}
```

---

## Notes for Flutter Developer

1. **File Size Limits**: Ensure uploaded images are compressed before sending (recommended max 5MB per file).

2. **Supported File Formats**: The API accepts common image formats (JPG, PNG) and PDF files.

3. **Date Format**: Always send dates in `YYYY-MM-DD` format.

4. **Phone Number**: Include country code (e.g., `+201234567890`).

5. **Error Handling**: Always check `success` field in response and display appropriate error messages from `error.message`.

6. **Loading States**: Show loading indicators during API calls as file uploads may take time.

7. **Offline Support**: Consider caching the form data locally in case of network failures.

8. **Status Polling**: After submission, you may want to periodically poll the request status to show updates to the user.

---

## Related Endpoints (Already Implemented)

- `GET /cars` - List all available cars
- `GET /cars/{car_id}` - Get car details
- `GET /investments/my-investments` - Get user's approved investments (includes both apartments and cars)

---

## Testing

Use the test user credentials:
- Email: `ib.rahim@ibrahim.com`
- Password: `User@123`

Or create a new user through the registration endpoint.
