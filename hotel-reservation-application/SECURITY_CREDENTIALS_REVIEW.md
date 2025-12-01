# 🔐 SECURITY CREDENTIALS REVIEW - Hotel Reservation Application

**Date:** 2025-11-28  
**Status:** ⚠️ CRITICAL SECURITY ISSUES FOUND  
**Priority:** HIGH - Immediate Action Required

---

## 🚨 **EXECUTIVE SUMMARY**

**Found 8 locations with hardcoded credentials** across the hotel-reservation-application:

| Type | Count | Severity | Risk |
|------|-------|----------|------|
| **JWT Secrets** | 4 locations | 🔴 CRITICAL | Token forgery, unauthorized access |
| **Database Passwords** | 3 locations | 🔴 CRITICAL | Database breach, data theft |
| **Test User Passwords** | 1 location | 🟡 MEDIUM | Account compromise |

**Total Hardcoded Credentials:** 8 locations  
**Security Risk Level:** 🔴 **CRITICAL**

---

## 📋 **DETAILED FINDINGS**

### **1. JWT_SECRET - Hardcoded in 4 Locations**

**Current Value:** `MyApp-Super-Secret-Key-2024-Docker` / `MyApp-Super-Secret-Key-2024`

#### **Location 1: docker-compose.yml (Line 9)**
```yaml
environment:
  - JWT_SECRET=MyApp-Super-Secret-Key-2024-Docker  # ❌ HARDCODED
```
**Service:** nodejs-bff  
**Risk:** Anyone with access to this file can forge JWT tokens

#### **Location 2: docker-compose.yml (Line 31)**
```yaml
environment:
  - JWT_SECRET=MyApp-Super-Secret-Key-2024-Docker  # ❌ HARDCODED
```
**Service:** search-service  
**Risk:** Token verification can be bypassed

#### **Location 3: docker-compose.yml (Line 54)**
```yaml
environment:
  - JWT_SECRET=MyApp-Super-Secret-Key-2024-Docker  # ❌ HARDCODED
```
**Service:** authentication-service  
**Risk:** Attacker can create valid tokens for any user

#### **Location 4: src/backend/services/nodejs-bff/server.js (Line 14)**
```javascript
const JWT_SECRET = process.env.JWT_SECRET || 'MyApp-Super-Secret-Key-2024';  // ❌ HARDCODED FALLBACK
```
**Risk:** If env var is missing, falls back to known secret

#### **Location 5: src/backend/services/search_service/auth.py (Line 8)**
```python
JWT_SECRET = os.getenv("JWT_SECRET", "MyApp-Super-Secret-Key-2024")  # ❌ HARDCODED FALLBACK
```
**Risk:** If env var is missing, falls back to known secret

#### **Location 6: src/backend/services/authentication/src/main/resources/application.yml (Line 21)**
```yaml
jwt:
  secret: ${JWT_SECRET:MyApp-Super-Secret-Key-2024}  # ❌ HARDCODED FALLBACK
```
**Risk:** If env var is missing, falls back to known secret

---

### **2. PostgreSQL Database Credentials - Hardcoded in 3 Locations**

**Current Values:**
- Username: `postgres`
- Password: `password`

#### **Location 1: docker-compose.yml (Lines 52-53)**
```yaml
environment:
  - SPRING_DATASOURCE_USERNAME=postgres  # ❌ HARDCODED
  - SPRING_DATASOURCE_PASSWORD=password  # ❌ HARDCODED
```
**Service:** authentication-service  
**Risk:** Database access compromise

#### **Location 2: docker-compose.yml (Lines 75-76)**
```yaml
environment:
  POSTGRES_USER: postgres      # ❌ HARDCODED
  POSTGRES_PASSWORD: password  # ❌ HARDCODED
```
**Service:** postgres  
**Risk:** Direct database access with admin privileges

#### **Location 3: src/backend/services/authentication/src/main/resources/application.yml (Lines 9-10)**
```yaml
datasource:
  username: postgres  # ❌ HARDCODED
  password: password  # ❌ HARDCODED
```
**Risk:** Fallback credentials if env vars are missing

---

### **3. Test User Passwords - Hardcoded in 1 Location**

**Current Value:** `password123`

#### **Location: scripts/populate_users.py (Lines 13, 21, 29, etc.)**
```python
users_data = [
    {
        'username': 'arjun_singh',
        'email': 'arjun.singh@email.com',
        'password': 'password123',  # ❌ HARDCODED - All 10 test users
        ...
    },
    ...
]
```
**Risk:** All test accounts can be compromised  
**Impact:** 10 user accounts with known password

---

## 🎯 **RECOMMENDED SOLUTION: Environment Variables + .env File**

### **Approach:**
1. ✅ Create `.env` file for local development (NOT committed to Git)
2. ✅ Create `.env.example` file as template (committed to Git)
3. ✅ Update `docker-compose.yml` to use `${VARIABLE}` syntax
4. ✅ Remove all hardcoded fallback values
5. ✅ Add `.env` to `.gitignore`

---

## 📝 **PROPOSED CHANGES**

### **File 1: Create `.env` file (NOT committed)**
```bash
# Database Credentials
POSTGRES_USER=hotel_admin
POSTGRES_PASSWORD=<generate-strong-password>
POSTGRES_DB=hotel_auth_db

# JWT Secret (generate with: openssl rand -base64 32)
JWT_SECRET=<generate-strong-secret>

# Test User Password
TEST_USER_PASSWORD=<generate-strong-password>
```

### **File 2: Update `.env.example` (committed as template)**
```bash
# Database Credentials
POSTGRES_USER=your_db_username
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=hotel_auth_db

# JWT Secret (generate with: openssl rand -base64 32)
JWT_SECRET=your_jwt_secret_here

# Test User Password
TEST_USER_PASSWORD=your_test_password_here
```

### **File 3: Update docker-compose.yml**

**BEFORE (Lines 9, 31, 52-54, 75-76):**
```yaml
- JWT_SECRET=MyApp-Super-Secret-Key-2024-Docker
- SPRING_DATASOURCE_USERNAME=postgres
- SPRING_DATASOURCE_PASSWORD=password
POSTGRES_USER: postgres
POSTGRES_PASSWORD: password
```

**AFTER:**
```yaml
- JWT_SECRET=${JWT_SECRET}
- SPRING_DATASOURCE_USERNAME=${POSTGRES_USER}
- SPRING_DATASOURCE_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_USER: ${POSTGRES_USER}
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

### **File 4: Update server.js (nodejs-bff)**

**BEFORE (Line 14):**
```javascript
const JWT_SECRET = process.env.JWT_SECRET || 'MyApp-Super-Secret-Key-2024';
```

**AFTER:**
```javascript
const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) {
  console.error('FATAL: JWT_SECRET environment variable is not set');
  process.exit(1);
}
```

### **File 5: Update auth.py (search-service)**

**BEFORE (Line 8):**
```python
JWT_SECRET = os.getenv("JWT_SECRET", "MyApp-Super-Secret-Key-2024")
```

**AFTER:**
```python
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("FATAL: JWT_SECRET environment variable is not set")
```

### **File 6: Update application.yml (authentication-service)**

**BEFORE (Lines 9-10, 21):**
```yaml
datasource:
  username: postgres
  password: password
jwt:
  secret: ${JWT_SECRET:MyApp-Super-Secret-Key-2024}
```

**AFTER:**
```yaml
datasource:
  username: ${SPRING_DATASOURCE_USERNAME}
  password: ${SPRING_DATASOURCE_PASSWORD}
jwt:
  secret: ${JWT_SECRET}
```

### **File 7: Update populate_users.py**

**BEFORE (Line 13):**
```python
'password': 'password123',
```

**AFTER:**
```python
'password': os.getenv('TEST_USER_PASSWORD', 'ChangeMe123!'),
```

### **File 8: Update .gitignore**

**ADD:**
```
# Environment variables with secrets
.env
```

---

## 🔒 **SECURITY BENEFITS**

| Before | After | Improvement |
|--------|-------|-------------|
| ❌ Secrets in Git history | ✅ Secrets in .env (not committed) | Prevents credential leaks |
| ❌ Same secrets for all environments | ✅ Different secrets per environment | Limits breach impact |
| ❌ Weak passwords ("password") | ✅ Strong generated passwords | Harder to crack |
| ❌ No validation | ✅ Fails fast if secrets missing | Prevents insecure startup |

---

## 📊 **IMPLEMENTATION CHECKLIST**

- [ ] Create `.env` file with strong secrets
- [ ] Update `.env.example` as template
- [ ] Update `docker-compose.yml` (5 changes)
- [ ] Update `server.js` (nodejs-bff)
- [ ] Update `auth.py` (search-service)
- [ ] Update `application.yml` (authentication-service)
- [ ] Update `populate_users.py`
- [ ] Add `.env` to `.gitignore`
- [ ] Test all services start correctly
- [ ] Verify authentication still works
- [ ] Document secret generation process

---

## 🎯 **NEXT STEPS**

1. **Review this document** - Confirm the approach
2. **Generate strong secrets** - Use `openssl rand -base64 32`
3. **Apply changes** - Update all 8 files
4. **Test thoroughly** - Ensure nothing breaks
5. **Document** - Add README section on environment setup

---

## 💬 **QUESTIONS FOR REVIEW**

1. ✅ Is the `.env` file approach acceptable?
2. ✅ Should we fail fast (exit) if secrets are missing?
3. ✅ Do you want to generate secrets now or later?
4. ✅ Any other credentials we missed?

---

**Ready to implement once you approve!** 🚀


