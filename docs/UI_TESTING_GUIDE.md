# UI Testing Guide for MASS Platform

**Date:** 2025-11-12
**Status:** Backend-only project (no frontend yet)
**Purpose:** Guide for testing UI once built + testing backend API for UI integration

---

## Current Project Status

### ✅ What We Have
- **Backend API** - FastAPI with REST endpoints
- **API Documentation** - Swagger UI at `/docs`
- **Authentication** - OAuth 2.0 + JWT
- **Database** - PostgreSQL with async SQLAlchemy
- **Transcription Service** - Google Cloud Speech-to-Text
- **Health Checks** - Kubernetes-ready probes

### ❌ What We DON'T Have
- **Frontend Application** - Not built yet
- **UI Components** - No React/Vue/Angular code
- **Client-Side Code** - No JavaScript/TypeScript UI logic
- **Web Pages** - No HTML templates (API-only)

---

## Part 1: Testing the Backend API (For Future UI)

Since the frontend doesn't exist yet, we need to ensure the backend API is ready for UI integration.

### 1.1 Manual API Testing with Swagger UI

**Access:** http://localhost:8000/docs (when backend running)

**What to Test:**
```bash
# Start the backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Open browser to: http://localhost:8000/docs
```

**Test Each Endpoint:**

#### Health Checks
```http
GET /api/v1/health
GET /api/v1/health/detailed
GET /api/v1/readiness
GET /api/v1/liveness
```

#### Authentication Flow
```http
# 1. Login
POST /api/v1/auth/login
Body: {
  "username": "test@example.com",
  "password": "testpassword"
}

# 2. Get Current User
GET /api/v1/auth/me
Headers: { "Authorization": "Bearer <token>" }

# 3. Refresh Token
POST /api/v1/auth/refresh
Body: { "refresh_token": "<refresh_token>" }

# 4. Logout
POST /api/v1/auth/logout
Headers: { "Authorization": "Bearer <token>" }
```

#### Audio Transcription Flow
```http
# 1. Upload Audio File
POST /api/v1/audio/upload
Headers: { "Authorization": "Bearer <token>" }
Body: multipart/form-data
  - file: <audio.wav>
  - student_id: "student-123"
  - source_type: "classroom"

# 2. Start Transcription
POST /api/v1/audio/{audio_file_id}/transcribe
Headers: { "Authorization": "Bearer <token>" }

# 3. Check Status
GET /api/v1/audio/{audio_file_id}/status
Headers: { "Authorization": "Bearer <token>" }

# 4. Get Transcript
GET /api/v1/audio/{audio_file_id}/transcript
Headers: { "Authorization": "Bearer <token>" }

# 5. List Student Audio
GET /api/v1/student/{student_id}/audio
Headers: { "Authorization": "Bearer <token>" }
```

### 1.2 Testing with cURL

**Authentication Test:**
```bash
# Login and get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword" \
  | jq -r '.access_token')

# Use token for authenticated request
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

**File Upload Test:**
```bash
# Upload audio file
curl -X POST "http://localhost:8000/api/v1/audio/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_audio.wav" \
  -F "student_id=student-123" \
  -F "source_type=classroom"
```

### 1.3 Testing with Postman/Insomnia

**Setup:**
1. Import OpenAPI spec from `http://localhost:8000/openapi.json`
2. Create environment variables:
   - `BASE_URL`: `http://localhost:8000`
   - `TOKEN`: (set after login)

**Test Collections:**

```javascript
// Collection: Authentication
// 1. Login (save token to environment)
POST {{BASE_URL}}/api/v1/auth/login
Body: form-data
  username: test@example.com
  password: testpassword

// Post-response script:
pm.environment.set("TOKEN", pm.response.json().access_token);

// 2. Get Me (uses saved token)
GET {{BASE_URL}}/api/v1/auth/me
Headers:
  Authorization: Bearer {{TOKEN}}
```

### 1.4 Automated API Tests (Already Implemented)

**Run Backend Tests:**
```bash
cd backend
source venv/bin/activate
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Specific endpoint tests
pytest tests/test_health.py -v
pytest tests/test_transcription.py -v
```

---

## Part 2: When Frontend Gets Built

### 2.1 Frontend Framework Testing Strategies

#### Option A: React + TypeScript
**Recommended Stack:**
- **Testing Library:** React Testing Library
- **E2E Testing:** Playwright or Cypress
- **Component Testing:** Vitest or Jest
- **API Mocking:** MSW (Mock Service Worker)

**Example Tests:**
```typescript
// components/__tests__/LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginForm } from '../LoginForm';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.post('/api/v1/auth/login', (req, res, ctx) => {
    return res(ctx.json({
      access_token: 'mock-token',
      token_type: 'bearer'
    }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('login form submits credentials', async () => {
  render(<LoginForm />);

  // Fill form
  fireEvent.change(screen.getByLabelText(/email/i), {
    target: { value: 'test@example.com' }
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: 'password123' }
  });

  // Submit
  fireEvent.click(screen.getByRole('button', { name: /login/i }));

  // Verify success
  await waitFor(() => {
    expect(screen.getByText(/welcome/i)).toBeInTheDocument();
  });
});
```

**E2E Test Example:**
```typescript
// e2e/auth.spec.ts (Playwright)
import { test, expect } from '@playwright/test';

test('complete login flow', async ({ page }) => {
  await page.goto('http://localhost:3000/login');

  // Fill login form
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'testpassword');
  await page.click('button[type="submit"]');

  // Wait for redirect to dashboard
  await expect(page).toHaveURL(/dashboard/);

  // Verify authenticated state
  await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
});

test('audio upload and transcription', async ({ page }) => {
  // Login first
  await loginAsTeacher(page);

  // Navigate to upload
  await page.goto('http://localhost:3000/audio/upload');

  // Upload file
  await page.setInputFiles('[type="file"]', './fixtures/test-audio.wav');
  await page.selectOption('[name="student"]', 'student-123');
  await page.click('button[type="submit"]');

  // Wait for transcription
  await expect(page.locator('.transcription-status')).toHaveText('Processing', { timeout: 5000 });
  await expect(page.locator('.transcription-status')).toHaveText('Completed', { timeout: 60000 });

  // Verify transcript visible
  await expect(page.locator('.transcript-text')).toBeVisible();
});
```

#### Option B: Vue.js + TypeScript
**Recommended Stack:**
- **Testing Library:** Vue Test Utils
- **E2E Testing:** Playwright or Cypress
- **Component Testing:** Vitest
- **API Mocking:** MSW

**Example Test:**
```typescript
// components/__tests__/LoginForm.spec.ts
import { mount } from '@vue/test-utils';
import LoginForm from '../LoginForm.vue';
import { setupServer } from 'msw/node';
import { rest } from 'msw';

const server = setupServer(
  rest.post('/api/v1/auth/login', (req, res, ctx) => {
    return res(ctx.json({ access_token: 'mock-token' }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('LoginForm', () => {
  it('submits login credentials', async () => {
    const wrapper = mount(LoginForm);

    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.find('input[type="password"]').setValue('password123');
    await wrapper.find('form').trigger('submit');

    await wrapper.vm.$nextTick();

    expect(wrapper.emitted('login-success')).toBeTruthy();
  });
});
```

#### Option C: Next.js (React with SSR)
**Recommended Stack:**
- **Testing Library:** React Testing Library
- **E2E Testing:** Playwright
- **API Routes Testing:** Next.js API route testing
- **Component Testing:** Jest

**Example Test:**
```typescript
// __tests__/pages/login.test.tsx
import { render, screen } from '@testing-library/react';
import LoginPage from '../../pages/login';

test('login page renders', () => {
  render(<LoginPage />);
  expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument();
});

// __tests__/api/auth.test.ts
import { createMocks } from 'node-mocks-http';
import handler from '../../pages/api/auth/login';

test('login API returns token', async () => {
  const { req, res } = createMocks({
    method: 'POST',
    body: {
      email: 'test@example.com',
      password: 'testpassword'
    }
  });

  await handler(req, res);

  expect(res._getStatusCode()).toBe(200);
  expect(JSON.parse(res._getData())).toHaveProperty('access_token');
});
```

---

## Part 3: UI Testing Checklist

### 3.1 Unit Tests (Component Level)

**What to Test:**
- ✅ **Component Rendering**
  - Components render without crashing
  - Correct props passed and rendered
  - Conditional rendering works
  - Error states display correctly

- ✅ **User Interactions**
  - Click handlers fire
  - Form inputs update state
  - Form validation works
  - Submit handlers called with correct data

- ✅ **State Management**
  - Local component state updates
  - Global state (Redux/Zustand) updates
  - Context providers work
  - State resets on unmount

**Example Checklist:**
```typescript
describe('AudioUploadForm', () => {
  test('renders upload form');
  test('validates file type (audio only)');
  test('validates file size (< 100MB)');
  test('shows student selector');
  test('disables submit when invalid');
  test('calls onUpload with correct data');
  test('shows upload progress');
  test('handles upload errors');
  test('resets form after success');
});
```

### 3.2 Integration Tests (Feature Level)

**What to Test:**
- ✅ **Multi-Component Flows**
  - Login → Dashboard navigation
  - Audio upload → Transcription → Results
  - Student selection → Assessment view
  - Data fetching and display

- ✅ **API Integration**
  - Successful API calls
  - Error handling (404, 500, timeout)
  - Loading states
  - Authentication headers sent
  - Token refresh on 401

**Example Checklist:**
```typescript
describe('Audio Transcription Flow', () => {
  test('teacher logs in');
  test('navigates to audio upload');
  test('selects student from dropdown');
  test('uploads audio file');
  test('shows upload progress');
  test('redirects to transcription page');
  test('polls for transcription status');
  test('displays completed transcript');
  test('shows word-level timestamps');
  test('allows saving notes');
});
```

### 3.3 E2E Tests (User Journey Level)

**What to Test:**
- ✅ **Complete User Journeys**
  - Teacher onboarding flow
  - Student assessment workflow
  - Audio recording and transcription
  - Report generation
  - Admin configuration

- ✅ **Cross-Browser Testing**
  - Chrome
  - Firefox
  - Safari
  - Edge
  - Mobile browsers (iOS Safari, Chrome Mobile)

- ✅ **Responsive Design**
  - Desktop (1920x1080, 1366x768)
  - Tablet (iPad, Android tablets)
  - Mobile (iPhone, Android phones)

**Example E2E Checklist:**
```typescript
describe('Teacher Assessment Workflow', () => {
  test('teacher logs in with valid credentials');
  test('dashboard shows student list');
  test('teacher selects student');
  test('uploads classroom audio recording');
  test('transcription completes successfully');
  test('linguistic features extracted');
  test('behavioral features calculated');
  test('skill assessment generated');
  test('teacher reviews assessment');
  test('teacher adds notes and evidence');
  test('teacher saves final assessment');
  test('report available for download');
});
```

### 3.4 Accessibility Tests

**What to Test:**
- ✅ **WCAG 2.1 Compliance**
  - Keyboard navigation works
  - Screen reader compatible (ARIA labels)
  - Color contrast sufficient (4.5:1 for text)
  - Focus indicators visible
  - Form labels associated with inputs

**Tools:**
- **axe-core** - Automated accessibility testing
- **pa11y** - CLI accessibility testing
- **Lighthouse** - Chrome DevTools audit

**Example Test:**
```typescript
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('login page has no accessibility violations', async () => {
  const { container } = render(<LoginPage />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### 3.5 Performance Tests

**What to Test:**
- ✅ **Load Times**
  - First Contentful Paint (FCP) < 1.8s
  - Largest Contentful Paint (LCP) < 2.5s
  - Time to Interactive (TTI) < 3.8s
  - Cumulative Layout Shift (CLS) < 0.1

- ✅ **Runtime Performance**
  - Smooth scrolling (60fps)
  - Fast interactions (< 100ms)
  - Efficient re-renders
  - Memory leaks detected

**Tools:**
- **Lighthouse CI** - Automated performance testing
- **WebPageTest** - Real browser testing
- **Chrome DevTools Performance** - Profiling

**Example Test:**
```typescript
// lighthouse-ci.js
module.exports = {
  ci: {
    collect: {
      startServerCommand: 'npm start',
      url: ['http://localhost:3000'],
      numberOfRuns: 3
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'first-contentful-paint': ['error', { maxNumericValue: 1800 }],
        'interactive': ['error', { maxNumericValue: 3800 }]
      }
    }
  }
};
```

---

## Part 4: API Contract Testing (For UI Integration)

### 4.1 OpenAPI/Swagger Validation

**Ensure API matches contract:**
```bash
# Install swagger-cli
npm install -g @apidevtools/swagger-cli

# Validate OpenAPI spec
swagger-cli validate http://localhost:8000/openapi.json

# Generate TypeScript types from OpenAPI
npm install -g openapi-typescript
openapi-typescript http://localhost:8000/openapi.json --output api-types.ts
```

### 4.2 Mock Server for Frontend Development

**Use MSW (Mock Service Worker):**
```typescript
// mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  // Auth endpoints
  rest.post('/api/v1/auth/login', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        access_token: 'mock-jwt-token',
        refresh_token: 'mock-refresh-token',
        token_type: 'bearer',
        expires_in: 3600
      })
    );
  }),

  // Audio upload
  rest.post('/api/v1/audio/upload', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 'audio-123',
        student_id: 'student-456',
        storage_path: 'gs://bucket/audio-123.wav',
        transcription_status: 'pending'
      })
    );
  }),

  // Get transcript
  rest.get('/api/v1/audio/:id/transcript', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: 'transcript-123',
        audio_file_id: req.params.id,
        text: 'This is a mock transcript for testing.',
        word_count: 7,
        confidence_score: 0.95,
        language_code: 'en-US'
      })
    );
  })
];

// mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

**Use in tests:**
```typescript
// setupTests.ts
import { server } from './mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### 4.3 Contract Testing with Pact

**Ensure UI and API agree on contract:**
```typescript
// pact/audio.pact.spec.ts
import { PactV3 } from '@pact-foundation/pact';
import { api } from '../src/api';

const provider = new PactV3({
  consumer: 'mass-frontend',
  provider: 'mass-backend',
  dir: './pacts'
});

describe('Audio Upload Contract', () => {
  test('uploads audio file successfully', async () => {
    await provider
      .given('student exists')
      .uponReceiving('audio upload request')
      .withRequest({
        method: 'POST',
        path: '/api/v1/audio/upload',
        headers: {
          'Authorization': 'Bearer token',
          'Content-Type': 'multipart/form-data'
        },
        body: {
          student_id: 'student-123',
          source_type: 'classroom'
        }
      })
      .willRespondWith({
        status: 201,
        headers: { 'Content-Type': 'application/json' },
        body: {
          id: 'audio-123',
          student_id: 'student-123',
          transcription_status: 'pending'
        }
      });

    await provider.executeTest(async () => {
      const result = await api.uploadAudio(file, 'student-123');
      expect(result.id).toBe('audio-123');
    });
  });
});
```

---

## Part 5: Testing Tools & Setup

### 5.1 Recommended Testing Stack

#### Frontend Testing
```json
{
  "devDependencies": {
    // Unit Testing
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.1.0",
    "@testing-library/user-event": "^14.5.0",
    "vitest": "^1.0.0",

    // E2E Testing
    "@playwright/test": "^1.40.0",

    // API Mocking
    "msw": "^2.0.0",

    // Accessibility
    "jest-axe": "^8.0.0",
    "axe-core": "^4.8.0",

    // Contract Testing
    "@pact-foundation/pact": "^12.0.0"
  }
}
```

#### Backend API Testing (Already Set Up)
```txt
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0
```

### 5.2 CI/CD Integration

**GitHub Actions Example:**
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: npm ci
      - name: Run unit tests
        run: npm run test:unit
      - name: Run E2E tests
        run: npm run test:e2e
      - name: Upload Playwright report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## Part 6: Current API Testing Status

Since there's no UI yet, here's what we CAN test right now:

### ✅ Already Tested (Backend)
- Health check endpoints (4 tests)
- CORS middleware (2 tests)
- Request middleware (4 tests)
- Transcription service unit tests (6 tests)
- API documentation endpoints (4 tests)

### ⏳ Needs Testing (Backend for Future UI)
- Authentication endpoints (0 tests) ⚠️
- Audio upload endpoint
- Transcription status polling
- Student data endpoints
- Teacher data endpoints
- Skills assessment endpoints
- Telemetry ingestion endpoints

### 🔨 How to Test Now (Manual)

**1. Start Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**2. Test with Swagger UI:**
```
Open: http://localhost:8000/docs
Click "Try it out" on each endpoint
Verify responses match expected format
```

**3. Test with cURL:**
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Login (mock auth)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword"
```

---

## Part 7: Recommended Frontend Architecture

When building the UI, consider this testing-friendly architecture:

### 7.1 Component Structure
```
src/
├── components/
│   ├── atoms/           # Small, reusable components (Button, Input)
│   ├── molecules/       # Combinations (FormField, SearchBar)
│   ├── organisms/       # Complex components (LoginForm, AudioPlayer)
│   └── templates/       # Page layouts
├── pages/              # Route components
├── hooks/              # Custom React hooks
├── api/                # API client functions
├── stores/             # State management (Zustand/Redux)
├── types/              # TypeScript types (from OpenAPI)
└── __tests__/          # Test files mirroring structure
```

### 7.2 API Client Layer
```typescript
// api/client.ts
import axios from 'axios';

const client = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor for auth token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token refresh
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Attempt token refresh
      await refreshToken();
      return client.request(error.config);
    }
    return Promise.reject(error);
  }
);

export default client;
```

---

## Part 8: Testing Priorities

### When Frontend Gets Built

#### Phase 1: Foundation (Week 1)
1. ✅ Set up testing infrastructure (Playwright, Vitest, MSW)
2. ✅ Create API mocks for development
3. ✅ Write component unit tests for authentication
4. ✅ E2E test for login flow

#### Phase 2: Core Features (Week 2-3)
5. ✅ Audio upload component tests
6. ✅ Transcription display tests
7. ✅ Student management tests
8. ✅ E2E test for audio → transcription flow

#### Phase 3: Integration (Week 4)
9. ✅ Integration tests with real API
10. ✅ Contract tests (Pact)
11. ✅ Accessibility audit
12. ✅ Performance testing

---

## Summary

### Right Now (No UI)
✅ **Test backend API thoroughly**
- Write authentication endpoint tests
- Test all API endpoints with pytest
- Manual testing with Swagger UI
- Prepare OpenAPI spec for frontend

### When Frontend Built
✅ **Follow testing pyramid:**
- 70% Unit tests (components, hooks)
- 20% Integration tests (features, API)
- 10% E2E tests (user journeys)

✅ **Use proper tooling:**
- React Testing Library for components
- Playwright for E2E
- MSW for API mocking
- Lighthouse for performance

✅ **Test what matters:**
- User can log in
- User can upload audio
- Transcription works end-to-end
- Students can be managed
- Reports can be generated

---

## Resources

### Documentation
- [React Testing Library](https://testing-library.com/react)
- [Playwright](https://playwright.dev)
- [MSW](https://mswjs.io)
- [Vitest](https://vitest.dev)
- [Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)

### Backend Testing (Current)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Documentation](https://docs.pytest.org)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)

---

**Next Steps:**
1. ✅ Continue testing backend API (authentication tests priority)
2. ⏳ Build frontend application
3. ⏳ Implement frontend testing strategy
4. ⏳ Set up CI/CD pipeline for both frontend and backend tests
