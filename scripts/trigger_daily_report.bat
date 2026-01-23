@echo off
REM Windows 定时任务脚本 - 触发每日报告
REM 这个脚本会通过 GitHub API 触发 daily-report workflow

echo Triggering daily report workflow...

curl -X POST ^
  -H "Accept: application/vnd.github.v3+json" ^
  -H "Authorization: token YOUR_GITHUB_TOKEN_HERE" ^
  https://api.github.com/repos/mattzheng2435-tech/smart-memo-system/dispatches ^
  -d "{\"ref\":\"main\",\"event_type\":\"trigger-daily-report\"}"

echo.
echo Daily report workflow triggered!
echo.
pause
