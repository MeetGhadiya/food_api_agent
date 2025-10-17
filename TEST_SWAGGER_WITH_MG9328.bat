@echo off
cls
echo.
echo ====================================================================
echo   COMPLETE SWAGGER AUTH TEST FOR MG9328
echo ====================================================================
echo.
echo This script will:
echo  1. Login with your credentials (MG9328 / Meet7805)
echo  2. Show you the Bearer token  
echo  3. Open Swagger UI
echo  4. Give you instructions to authorize
echo.
echo ====================================================================
echo.
pause

echo.
echo [1/4] Testing login...
echo.

python -c "import requests, json; r = requests.post('http://localhost:8000/api/auth/login', json={'username_or_email': 'MG9328', 'password': 'Meet7805'}); print('Status:', r.status_code); data = r.json(); print(json.dumps(data, indent=2)); token = data.get('token', ''); print('\n' + '='*70); print('YOUR BEARER TOKEN:'); print('='*70); print('Bearer', token[:80] + '...'); print('='*70); open('temp_token.txt', 'w').write('Bearer ' + token)"

echo.
echo ====================================================================
echo   TOKEN SAVED TO: temp_token.txt
echo ====================================================================
echo.
echo [2/4] Opening Swagger UI...
start http://localhost:8000/docs

echo.
echo Waiting for browser to open...
timeout /t 3 /nobreak > nul

echo.
echo ====================================================================
echo   INSTRUCTIONS TO AUTHORIZE IN SWAGGER:
echo ====================================================================
echo.
echo 1. In the Swagger page that just opened:
echo    - Look for the "Authorize" button (green lock icon, top-right)
echo.
echo 2. Click "Authorize"
echo.
echo 3. You should see a SIMPLE dialog with:
echo    - Title: "HTTPBearer (http, Bearer)"
echo    - ONE input field labeled "Value"
echo.
echo 4. Open temp_token.txt file (opening now...)
echo.
timeout /t 2 /nobreak > nul
start notepad temp_token.txt

echo.
echo 5. Copy the ENTIRE token from temp_token.txt
echo    (including the word "Bearer")
echo.
echo 6. Paste it into the "Value" field in Swagger
echo.
echo 7. Click "Authorize" button
echo.
echo 8. Click "Close"
echo.
echo 9. The lock icon should now be CLOSED (locked)
echo.
echo 10. Test with: GET /users/me
echo.
echo ====================================================================
echo   TROUBLESHOOTING:
echo ====================================================================
echo.
echo If you see OAuth2 dialog with multiple fields (username, password, 
echo client_id, client_secret):
echo.
echo  Solution: Hard refresh the page (Ctrl + Shift + R)
echo.
echo If you get 401 Unauthorized:
echo  - Make sure you copied "Bearer " (with space) before the token
echo  - Token format: Bearer eyJhbGci...
echo.
echo ====================================================================
echo.
pause
