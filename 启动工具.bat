@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (set "PYCMD=py -3") else (set "PYCMD=python")
:menu
cls
echo Creator Idea Vault - 本地选题库
echo 1. 导入 examples\sources.csv
echo 2. 导出选题报告和Notion CSV
echo 3. 查看素材统计
echo 4. 运行测试
echo 0. 退出
set /p op=选择：
if "%op%"=="1" %PYCMD% -m creator_idea_vault import --file examples/sources.csv
if "%op%"=="2" %PYCMD% -m creator_idea_vault export --output reports
if "%op%"=="3" %PYCMD% -m creator_idea_vault stats
if "%op%"=="4" %PYCMD% -m unittest discover -s tests -v
if "%op%"=="0" exit /b 0
echo.
pause
goto menu
