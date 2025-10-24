# Demo Mode Cleanup Guide

## ⚠️ IMPORTANT: Remove Before Production/Push

This document lists all demo mode files and code that must be removed before pushing to production.

---

## 📁 Files to DELETE Entirely

Delete these files completely:

```bash
# From frontend/src/
rm frontend/src/services/mockService.js
rm -rf frontend/src/components/DemoToggle/
rm frontend/DEMO_MODE_CLEANUP.md  # This file
```

---

## ✏️ Code to REMOVE from Existing Files

### 1. `frontend/src/App.jsx`

**Remove this import:**
```javascript
import { DemoToggle } from './components/DemoToggle' // TODO: Remove before production
```

**Remove this component:**
```javascript
{/* TODO: Remove DemoToggle before production */}
<DemoToggle />
```

---

### 2. `frontend/src/services/voiceService.js`

**Remove this import:**
```javascript
import { mockVoiceService } from './mockService'; // TODO: Remove before production
```

**Remove this function:**
```javascript
// TODO: Remove this function before production
const isDemoMode = () => localStorage.getItem('DEMO_MODE') === 'true';
```

**Remove all these checks (3 locations):**
```javascript
// TODO: Remove demo mode check before production
if (isDemoMode()) return mockVoiceService.transcribeAudio(audioBlob, sessionId);

// TODO: Remove demo mode check before production
if (isDemoMode()) return mockVoiceService.parseIntent(transcript, sessionId);

// TODO: Remove demo mode check before production
if (isDemoMode()) return mockVoiceService.getSession(sessionId);
```

---

### 3. `frontend/src/services/transferService.js`

**Remove this import:**
```javascript
import { mockTransferService } from './mockService'; // TODO: Remove before production
```

**Remove this function:**
```javascript
// TODO: Remove this function before production
const isDemoMode = () => localStorage.getItem('DEMO_MODE') === 'true';
```

**Remove all these checks (5 locations):**
```javascript
// TODO: Remove demo mode check before production
if (isDemoMode()) return mockTransferService.searchRecipients(name, limit);

// TODO: Remove demo mode check before production
if (isDemoMode()) return mockTransferService.initiateTransfer(recipientId, amount, sessionId);

// TODO: Remove demo mode check before production
if (isDemoMode()) return mockTransferService.verifyPin(transferId, pin);

// TODO: Remove demo mode check before production
if (isDemoMode()) return mockTransferService.confirmTransfer(transferId);

// TODO: Remove demo mode check before production
if (isDemoMode()) return mockTransferService.cancelTransfer(transferId);
```

---

## 🔍 Quick Search Commands

Find all demo mode code to remove:

```bash
# Search for TODO comments related to demo mode
grep -r "TODO: Remove before production" frontend/src/

# Search for DEMO_MODE references
grep -r "DEMO_MODE" frontend/src/

# Search for mockService imports
grep -r "mockService" frontend/src/

# Search for DemoToggle references
grep -r "DemoToggle" frontend/src/
```

---

## ✅ Verification Checklist

After cleanup, verify:

- [ ] No `mockService.js` file exists
- [ ] No `DemoToggle/` directory exists
- [ ] No imports of `mockService` in any file
- [ ] No imports of `DemoToggle` in App.jsx
- [ ] No `isDemoMode()` function in any service
- [ ] No demo mode checks in voiceService.js
- [ ] No demo mode checks in transferService.js
- [ ] No `<DemoToggle />` component in App.jsx
- [ ] Run `npm run build` successfully
- [ ] No console warnings about demo mode

---

## 🚀 Quick Cleanup Script

Run this from `Echo-Bank/frontend/` directory:

```bash
# Delete demo files
rm src/services/mockService.js
rm -rf src/components/DemoToggle/
rm DEMO_MODE_CLEANUP.md

# Then manually edit these files to remove demo code:
# - src/App.jsx
# - src/services/voiceService.js
# - src/services/transferService.js
```

Or use this one-liner to see what needs manual editing:

```bash
grep -n "TODO: Remove" src/**/*.js src/**/*.jsx
```

---

## 📋 Final Production Check

Before pushing to main branch:

```bash
# 1. Search for any remaining demo code
grep -r "DEMO" frontend/src/

# 2. Search for TODO comments
grep -r "TODO: Remove" frontend/src/

# 3. Build the project (should have no errors)
npm run build

# 4. Test with real backend
# Make sure DEMO_MODE is off and test with actual API
```

---

## 🎯 Summary

**Total files to delete:** 3 files
**Total files to edit:** 3 files
**Estimated cleanup time:** 5 minutes

All demo mode code is clearly marked with:
- `// TODO: Remove before production`
- Comments mentioning "demo mode"
- Files in `DemoToggle/` directory
- `mockService.js` file

---

**After cleanup, your code will be production-ready and only use real API calls!**
