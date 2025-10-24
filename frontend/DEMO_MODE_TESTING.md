# 🎭 Demo Mode Testing Guide

Demo mode is now enabled! You can test the entire transfer flow without needing the backend.

---

## 🚀 How to Use Demo Mode

### Step 1: Open the Application
Go to: **http://localhost:5173/**

### Step 2: Enable Demo Mode
Look for a button in the **bottom-right corner** that says:
- **"🌐 LIVE"** (Demo mode is OFF - will try to use real backend)
- **"🎭 DEMO"** (Demo mode is ON - using mock data)

**Click the button** to toggle demo mode.

When you enable demo mode:
- ✅ Page will reload automatically
- ✅ You'll see a red "Demo Mode Active" badge
- ✅ All API calls will use mock data instead of real backend

---

## 🧪 Complete Test Flow

### Test 1: Voice Recording & Transcription

1. **Click the blue microphone button** 🎤
2. **Grant microphone permission** (browser will ask)
3. **Click the mic inside the modal**
4. **Speak or wait 5 seconds**
5. **See the transcript appear**: "Send 5000 naira to John"
6. **Click "Continue"**

**Expected Result:**
- ✅ Transcript shows your speech (or default mock text)
- ✅ Bot message: "Searching for John..."
- ✅ Bot message: "Found John Okafor at Zenith Bank."
- ✅ Bot message: "Sending ₦5,000 to John Okafor..."
- ✅ PIN modal opens automatically

---

### Test 2: PIN Modal

After the PIN modal opens:

1. **See the transfer summary:**
   - Recipient: John Okafor
   - Amount: ₦5,000
   - New Balance: ₦40,320

2. **Enter PIN: `1234`** (this is the test PIN)
3. **Click "Verify PIN"**

**Expected Result:**
- ✅ PIN input accepts only 4 digits
- ✅ Show/hide PIN toggle works
- ✅ Correct PIN (1234) proceeds to confirmation
- ✅ Wrong PIN shows error message
- ✅ Loading state shows during verification

**Try Wrong PIN:**
- Enter: `0000`
- See error: "Incorrect PIN. You have 2 attempts remaining."

---

### Test 3: Confirmation Modal

After PIN verification:

1. **Review transfer details:**
   - Recipient name and account
   - Bank name
   - Amount
   - Current and new balance

2. **Click "Confirm Transfer"**

**Expected Result:**
- ✅ Warning banner displays
- ✅ All details are correct
- ✅ Loading state shows "Processing..."
- ✅ Success modal appears with checkmark

---

### Test 4: Success State

After confirming:

1. **See the success checkmark animation** ✓
2. **Review transaction details:**
   - Transaction reference number
   - Completed timestamp
   - New balance

3. **Click "Done"**

**Expected Result:**
- ✅ Success animation plays
- ✅ All details displayed
- ✅ Modal closes on "Done"
- ✅ Conversation updated with success message

---

### Test 5: Conversation History

1. **Scroll down** to see the conversation
2. **Check messages:**
   - Your voice input (user message)
   - Bot responses
   - Timestamps

3. **Click "Clear"** to reset

**Expected Result:**
- ✅ All messages displayed
- ✅ User vs Bot styling different
- ✅ Scrollable when many messages
- ✅ Clear button works

---

### Test 6: Cancel Flow

1. **Start a new transfer** (click mic button)
2. **When PIN modal opens**, click "Cancel"

**Expected Result:**
- ✅ Modal closes
- ✅ Bot message: "Transfer cancelled. No money was sent."
- ✅ No money deducted

---

## 🎨 UI/UX Tests

### Test Animations

**Voice Modal:**
- [ ] Smooth fade-in and slide-up
- [ ] Pulse rings during recording
- [ ] Close button rotates on hover

**PIN Modal:**
- [ ] Slide-up animation
- [ ] PIN input shows/hides
- [ ] Error messages animate in

**Confirmation Modal:**
- [ ] Warning banner displays
- [ ] Success checkmark scales in
- [ ] Done button hover effect

### Test Responsive Design

1. **Resize browser window**
2. **Try mobile view (F12 → Toggle device toolbar)**
3. **Test on actual mobile device**

**Expected:**
- ✅ Modals scale properly
- ✅ Buttons remain touchable
- ✅ Text remains readable
- ✅ Demo toggle visible on mobile

---

## 🐛 Test Error Handling

### Wrong PIN Test

1. Start transfer
2. Enter wrong PIN: `0000`
3. See error message
4. Error persists until correct PIN entered

### Multiple Wrong PINs

1. Enter `0000` - Error shows
2. Enter `1111` - Error shows again
3. Mock limits to 3 attempts

### Network "Errors" (Mock Delays)

All mock services have artificial delays:
- Transcription: 1.5 seconds
- Intent parsing: 0.8 seconds
- Recipient search: 0.6 seconds
- Transfer initiation: 0.8 seconds
- PIN verification: 1 second
- Confirmation: 1.2 seconds

**Loading states should show during these delays.**

---

## 📊 Browser Console Testing

Open DevTools (F12) → Console tab:

### Check for Errors
- ✅ No red errors
- ✅ No CORS errors
- ✅ No 404s

### Check Logs
You should see:
```
Transcript: Send 5000 naira to John
Intent: {intent: "transfer", ...}
```

### Network Tab (F12 → Network)
- ✅ No failed requests (everything mocked)
- ✅ No calls to localhost:8000

---

## 🔄 Switching Between Demo and Live Mode

### Enable Demo Mode:
1. Click **"🌐 LIVE"** button
2. Alert appears: "Demo Mode ENABLED"
3. Click OK
4. Page reloads
5. Button now shows **"🎭 DEMO"**

### Disable Demo Mode:
1. Click **"🎭 DEMO"** button
2. Alert appears: "Demo Mode DISABLED"
3. Click OK
4. Page reloads
5. Button now shows **"🌐 LIVE"**
6. Will try to connect to real backend

---

## 🎯 Test Checklist

Complete this checklist:

**Voice Features:**
- [ ] Microphone permission works
- [ ] Recording starts/stops
- [ ] Transcript appears
- [ ] Mock transcript is correct

**Transfer Flow:**
- [ ] Recipient search works
- [ ] Transfer initiates
- [ ] PIN modal opens
- [ ] PIN validation works
- [ ] Confirmation modal opens
- [ ] Success state shows

**UI/Animations:**
- [ ] All animations smooth
- [ ] No flickering
- [ ] Loading states clear
- [ ] Colors/fonts correct

**Error Handling:**
- [ ] Wrong PIN shows error
- [ ] Cancel works correctly
- [ ] Error messages clear

**Responsive:**
- [ ] Works on desktop
- [ ] Works on mobile view
- [ ] Demo toggle visible
- [ ] Modals scale properly

---

## 💡 Tips

### Test PIN
**Correct PIN:** `1234`
**Wrong PIN:** Any other 4 digits

### Mock Data
- **Recipient:** John Okafor at Zenith Bank
- **Amount:** ₦5,000
- **Starting Balance:** ₦45,320
- **New Balance:** ₦40,320

### Keyboard Shortcuts
- **F12** - Open DevTools
- **Ctrl+Shift+C** - Inspect element
- **Ctrl+Shift+M** - Toggle mobile view

---

## 🚨 Troubleshooting

### Demo Mode Not Working?

1. **Check browser console** - Any errors?
2. **Refresh page** - F5 or Ctrl+R
3. **Clear localStorage:**
   ```javascript
   // In browser console:
   localStorage.clear()
   location.reload()
   ```

### Button Not Appearing?

- Check bottom-right corner
- Try scrolling down
- Look for red "Demo Mode Active" badge

### Stuck in Demo Mode?

```javascript
// In browser console:
localStorage.setItem('DEMO_MODE', 'false')
location.reload()
```

---

## 📝 Feedback

While testing, note:
- Any bugs or glitches
- UI improvements needed
- Confusing interactions
- Performance issues

---

## ✅ After Testing

Once you've tested everything:

1. **Document any issues found**
2. **Take screenshots** if needed
3. **Test with real backend** when available
4. **Remember to remove demo mode before pushing** (see DEMO_MODE_CLEANUP.md)

---

**Happy Testing! 🎉**

All features should work smoothly in demo mode. The full transfer flow from voice input to successful transaction is now testable!
