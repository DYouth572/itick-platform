# -*- coding: utf-8 -*-
"""
Script chuẩn hóa Postman Collection, Environment và Data-driven JSON:
- Khớp 100% với FastAPI routes thực tế (JSON body, /api/auth/me, /api/admin/system/fee, ...)
- Xuất collection chuẩn v2.1.0 cho Newman CLI và xuất báo cáo HTML htmlextra
"""
import json
import os

def generate_postman_files():
    base_dir = r'd:\SJ_Testing\Project\tests\automation'
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Environment JSON
    env = {
        "id": "eventtick-env-001",
        "name": "EventTick Local Environment",
        "values": [
            {"key": "base_url", "value": "http://127.0.0.1:8001", "type": "default", "enabled": True},
            {"key": "admin_email", "value": "admin@eventtick.com", "type": "default", "enabled": True},
            {"key": "admin_password", "value": "admin123", "type": "default", "enabled": True},
            {"key": "organizer_email", "value": "organizer@eventtick.com", "type": "default", "enabled": True},
            {"key": "organizer_password", "value": "org123", "type": "default", "enabled": True},
            {"key": "attendee_email", "value": "attendee@eventtick.com", "type": "default", "enabled": True},
            {"key": "attendee_password", "value": "att123", "type": "default", "enabled": True},
            {"key": "student_b_email", "value": "student_b@eventtick.com", "type": "default", "enabled": True},
            {"key": "student_b_password", "value": "att123", "type": "default", "enabled": True},
            {"key": "attendee_token", "value": "", "type": "default", "enabled": True},
            {"key": "organizer_token", "value": "", "type": "default", "enabled": True},
            {"key": "admin_token", "value": "", "type": "default", "enabled": True},
            {"key": "last_ticket_code", "value": "TICK-2026-MOCK01", "type": "default", "enabled": True}
        ]
    }
    with open(os.path.join(base_dir, 'eventtick.postman_environment.json'), 'w', encoding='utf-8') as f:
        json.dump(env, f, ensure_ascii=False, indent=2)

    # 2. Data-driven JSON
    test_data = [
        {"scenario": "TC_DATA_01_Normal", "event_id": 1, "tier_id": 1, "quantity": 1, "voucher_code": "", "expected_status": 200},
        {"scenario": "TC_DATA_02_Valid_Voucher", "event_id": 1, "tier_id": 1, "quantity": 2, "voucher_code": "GIAM50K", "expected_status": 200},
        {"scenario": "TC_DATA_03_Max_Cap_Voucher", "event_id": 1, "tier_id": 2, "quantity": 4, "voucher_code": "GIAM20", "expected_status": 200},
        {"scenario": "TC_DATA_04_Negative_Zero_Tickets", "event_id": 1, "tier_id": 1, "quantity": 0, "voucher_code": "", "expected_status": 422},
        {"scenario": "TC_DATA_05_Negative_Crash_Quote", "event_id": 1, "tier_id": 1, "quantity": 1, "voucher_code": "GIAM'20", "expected_status": 422}
    ]
    with open(os.path.join(base_dir, 'test_data_bookings.json'), 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)

    # 3. Postman Collection JSON (20 API requests with rich assertions)
    collection = {
        "info": {
            "_postman_id": "itick-api-tests-collection-001",
            "name": "iTick Event Platform - Automation Test Suite",
            "description": "Bộ kịch bản kiểm thử tự động API toàn diện cho hệ thống iTick (EventTick) phục vụ đồ án học phần Đánh giá hiệu năng và Kiểm thử phần mềm.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [
            # 1. Health check
            {
                "name": "01. System Health Check",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {"raw": "{{base_url}}/health", "host": ["{{base_url}}"], "path": ["health"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 200 OK', function () { pm.response.to.have.status(200); });",
                        "pm.test('Response contains healthy status', function () { var json = pm.response.json(); pm.expect(json.status).to.eql('healthy'); pm.expect(json.system).to.eql('iTick'); });",
                        "pm.test('Response time is under 300ms', function () { pm.expect(pm.response.responseTime).to.be.below(300); });"
                    ], "type": "text/javascript"}
                }]
            },
            # 2. Login Attendee
            {
                "name": "02. Auth - Login Attendee",
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({"email": "{{attendee_email}}", "password": "{{attendee_password}}"})
                    },
                    "url": {"raw": "{{base_url}}/api/auth/login", "host": ["{{base_url}}"], "path": ["api", "auth", "login"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 200 OK', function () { pm.response.to.have.status(200); });",
                        "var json = pm.response.json();",
                        "pm.test('Returns access_token Bearer', function () { pm.expect(json).to.have.property('access_token'); pm.expect(json.token_type).to.eql('bearer'); });",
                        "pm.environment.set('attendee_token', json.access_token);"
                    ], "type": "text/javascript"}
                }]
            },
            # 3. Login Organizer
            {
                "name": "03. Auth - Login Organizer",
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({"email": "{{organizer_email}}", "password": "{{organizer_password}}"})
                    },
                    "url": {"raw": "{{base_url}}/api/auth/login", "host": ["{{base_url}}"], "path": ["api", "auth", "login"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 200 OK', function () { pm.response.to.have.status(200); });",
                        "var json = pm.response.json();",
                        "pm.environment.set('organizer_token', json.access_token);"
                    ], "type": "text/javascript"}
                }]
            },
            # 4. Login Admin
            {
                "name": "04. Auth - Login Admin",
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({"email": "{{admin_email}}", "password": "{{admin_password}}"})
                    },
                    "url": {"raw": "{{base_url}}/api/auth/login", "host": ["{{base_url}}"], "path": ["api", "auth", "login"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 200 OK', function () { pm.response.to.have.status(200); });",
                        "var json = pm.response.json();",
                        "pm.environment.set('admin_token', json.access_token);"
                    ], "type": "text/javascript"}
                }]
            },
            # 5. Negative Auth: Login with wrong password
            {
                "name": "05. Negative Auth - Login With Wrong Password",
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({"email": "{{attendee_email}}", "password": "wrongpassword123"})
                    },
                    "url": {"raw": "{{base_url}}/api/auth/login", "host": ["{{base_url}}"], "path": ["api", "auth", "login"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 401 Unauthorized', function () { pm.response.to.have.status(401); });",
                        "pm.test('Error detail explains invalid credentials', function () { var json = pm.response.json(); pm.expect(json.detail).to.be.a('string'); });"
                    ], "type": "text/javascript"}
                }]
            },
            # 6. Profile Me
            {
                "name": "06. User Profile - Get Current User via /api/auth/me",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{attendee_token}}"}],
                    "url": {"raw": "{{base_url}}/api/auth/me", "host": ["{{base_url}}"], "path": ["api", "auth", "me"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 200 OK', function () { pm.response.to.have.status(200); });",
                        "var json = pm.response.json();",
                        "pm.test('Profile email matches attendee_email', function () { pm.expect(json.email).to.eql(pm.environment.get('attendee_email')); });",
                        "pm.test('User has role ATTENDEE and balance >= 0', function () { pm.expect(json.role).to.eql('ATTENDEE'); pm.expect(json.balance).to.be.at.least(0); });"
                    ], "type": "text/javascript"}
                }]
            },
            # 7. List Events & Check SEED-12 Response Time
            {
                "name": "07. Events - List Events (Performance Check NFR-01 & SEED-12)",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {"raw": "{{base_url}}/api/events", "host": ["{{base_url}}"], "path": ["api", "events"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 200 OK', function () { pm.response.to.have.status(200); });",
                        "var json = pm.response.json();",
                        "pm.test('Returns items array', function () { pm.expect(json.items).to.be.an('array'); });",
                        "pm.test('NFR-01 Check: Response time should be <= 500ms (Flags SEED-12 delay if fails)', function () { pm.expect(pm.response.responseTime).to.be.below(500); });"
                    ], "type": "text/javascript"}
                }]
            },
            # 8. Search Events
            {
                "name": "08. Events - Search by Keyword",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {"raw": "{{base_url}}/api/events?keyword=Indie", "host": ["{{base_url}}"], "path": ["api", "events"], "query": [{"key": "keyword", "value": "Indie"}]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 200 OK', function () { pm.response.to.have.status(200); });",
                        "var json = pm.response.json();",
                        "pm.test('Returns search items array', function () { pm.expect(json.items).to.be.an('array'); });"
                    ], "type": "text/javascript"}
                }]
            },
            # 9. Negative Search limit=0 (Check SEED-15 Crash)
            {
                "name": "09. Negative Events - Pagination limit=0 (Check SEED-15 Crash)",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {"raw": "{{base_url}}/api/events?limit=0", "host": ["{{base_url}}"], "path": ["api", "events"], "query": [{"key": "limit", "value": "0"}]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Expected validation status 400 or 422 (Flags SEED-15 if 500 crash)', function () { pm.expect([400, 422]).to.include(pm.response.code); });"
                    ], "type": "text/javascript"}
                }]
            },
            # 10. Event Detail
            {
                "name": "10. Events - Get Event Detail by ID",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {"raw": "{{base_url}}/api/events/1", "host": ["{{base_url}}"], "path": ["api", "events", "1"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 200 OK', function () { pm.response.to.have.status(200); });",
                        "var json = pm.response.json();",
                        "pm.test('Event contains tiers array', function () { pm.expect(json.tiers).to.be.an('array'); });"
                    ], "type": "text/javascript"}
                }]
            },
            # 11. Book Tickets Happy Path
            {
                "name": "11. Bookings - Create Booking (Happy Path)",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{attendee_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "event_id": 1,
                            "tier_id": 1,
                            "quantity": 1,
                            "payment_method": "WALLET"
                        })
                    },
                    "url": {"raw": "{{base_url}}/api/bookings", "host": ["{{base_url}}"], "path": ["api", "bookings"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 200 or 201', function () { pm.expect([200, 201]).to.include(pm.response.code); });",
                        "var json = pm.response.json();",
                        "if (json.tickets && json.tickets.length > 0) { pm.environment.set('last_ticket_code', json.tickets[0].ticket_code); }"
                    ], "type": "text/javascript"}
                }]
            },
            # 12. Negative Booking quantity=0 (Check SEED-04)
            {
                "name": "12. Negative Bookings - Quantity = 0 (Check SEED-04)",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{attendee_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "event_id": 1,
                            "tier_id": 1,
                            "quantity": 0,
                            "payment_method": "WALLET"
                        })
                    },
                    "url": {"raw": "{{base_url}}/api/bookings", "host": ["{{base_url}}"], "path": ["api", "bookings"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Expected status 400 or 422 for quantity=0 (Flags SEED-04 if 200)', function () { pm.expect([400, 422]).to.include(pm.response.code); });"
                    ], "type": "text/javascript"}
                }]
            },
            # 13. Negative Booking Single Quote Crash (Check SEED-14)
            {
                "name": "13. Negative Bookings - Single Quote Voucher (Check SEED-14 Crash)",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{attendee_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "event_id": 1,
                            "tier_id": 1,
                            "quantity": 1,
                            "voucher_code": "GIAM'20",
                            "payment_method": "WALLET"
                        })
                    },
                    "url": {"raw": "{{base_url}}/api/bookings", "host": ["{{base_url}}"], "path": ["api", "bookings"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Expected status 400 or 422 for malformed voucher (Flags SEED-14 if 500 crash)', function () { pm.expect([400, 422]).to.include(pm.response.code); });"
                    ], "type": "text/javascript"}
                }]
            },
            # 14. Check Voucher Max Cap (Check SEED-02)
            {
                "name": "14. Bookings - Check Voucher Max Cap (Check SEED-02)",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{attendee_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "event_id": 1,
                            "tier_id": 2,
                            "quantity": 4,
                            "voucher_code": "GIAM20",
                            "payment_method": "WALLET"
                        })
                    },
                    "url": {"raw": "{{base_url}}/api/bookings", "host": ["{{base_url}}"], "path": ["api", "bookings"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 200 or 201', function () { pm.expect([200, 201]).to.include(pm.response.code); });",
                        "var json = pm.response.json();",
                        "pm.test('Discount must not exceed max cap 150k (Flags SEED-02 if discount > 150000)', function () { pm.expect(json.discount_amount).to.be.at.most(150000); });"
                    ], "type": "text/javascript"}
                }]
            },
            # 15. Check My Tickets
            {
                "name": "15. Bookings - Get My Purchased Tickets",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{attendee_token}}"}],
                    "url": {"raw": "{{base_url}}/api/bookings/my-tickets", "host": ["{{base_url}}"], "path": ["api", "bookings", "my-tickets"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 200 OK', function () { pm.response.to.have.status(200); });",
                        "var json = pm.response.json();",
                        "pm.test('Returns ticket array', function () { pm.expect(json).to.be.an('array'); });"
                    ], "type": "text/javascript"}
                }]
            },
            # 16. Check-in Valid Ticket
            {
                "name": "16. Check-in - Scan Valid Ticket via Gate Scanner",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{organizer_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({"ticket_code": "{{last_ticket_code}}"})
                    },
                    "url": {"raw": "{{base_url}}/api/check-in", "host": ["{{base_url}}"], "path": ["api", "check-in"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 200 OK', function () { pm.response.to.have.status(200); });",
                        "var json = pm.response.json();",
                        "pm.test('Checkin response has success boolean', function () { pm.expect(json).to.have.property('success'); });"
                    ], "type": "text/javascript"}
                }]
            },
            # 17. Check-in Duplicate Ticket
            {
                "name": "17. Negative Check-in - Scan Duplicate Ticket",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Authorization", "value": "Bearer {{organizer_token}}"},
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({"ticket_code": "{{last_ticket_code}}"})
                    },
                    "url": {"raw": "{{base_url}}/api/check-in", "host": ["{{base_url}}"], "path": ["api", "check-in"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "var json = pm.response.json();",
                        "pm.test('Duplicate ticket is rejected with success=false', function () { pm.expect(json.success).to.be.false; });"
                    ], "type": "text/javascript"}
                }]
            },
            # 18. Admin Get Platform System Fee
            {
                "name": "18. Admin - Get Platform System Fee",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{admin_token}}"}],
                    "url": {"raw": "{{base_url}}/api/admin/system/fee", "host": ["{{base_url}}"], "path": ["api", "admin", "system", "fee"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 200 OK', function () { pm.response.to.have.status(200); });",
                        "var json = pm.response.json();",
                        "pm.test('Platform fee is configured', function () { pm.expect(json.platform_fee_percent).to.be.at.least(0); });"
                    ], "type": "text/javascript"}
                }]
            },
            # 19. Admin Pending Events
            {
                "name": "19. Admin - Get Pending Events List",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{admin_token}}"}],
                    "url": {"raw": "{{base_url}}/api/admin/events/pending", "host": ["{{base_url}}"], "path": ["api", "admin", "events", "pending"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Status code is 200 OK', function () { pm.response.to.have.status(200); });",
                        "var json = pm.response.json();",
                        "pm.test('Pending events returns array', function () { pm.expect(json).to.be.an('array'); });"
                    ], "type": "text/javascript"}
                }]
            },
            # 20. Negative RBAC: Attendee calls Admin Endpoint
            {
                "name": "20. Negative RBAC - Attendee Calls Admin Endpoint (Access Control)",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{attendee_token}}"}],
                    "url": {"raw": "{{base_url}}/api/admin/system/fee", "host": ["{{base_url}}"], "path": ["api", "admin", "system", "fee"]}
                },
                "event": [{
                    "listen": "test",
                    "script": {"exec": [
                        "pm.test('Expected status 403 Forbidden for attendee calling admin API', function () { pm.response.to.have.status(403); });"
                    ], "type": "text/javascript"}
                }]
            }
        ]
    }
    
    with open(os.path.join(base_dir, 'iTick_API_Tests.postman_collection.json'), 'w', encoding='utf-8') as f:
        json.dump(collection, f, ensure_ascii=False, indent=2)
        
    print("-> Successfully generated standardized Postman Collection!")

if __name__ == '__main__':
    generate_postman_files()
