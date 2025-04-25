@echo off
setlocal enabledelayedexpansion

REM ========================
REM 主流程：参数判断入口
REM ========================
if "%1"=="start" (
    goto START
) else if "%1"=="stop" (
    goto STOP
) else if "%1"=="status" (
    goto STATUS
) else if "%1"=="restart" (
    goto RESTART
) else (
    echo Usage: %0 ^<start^|stop^|status^|restart^>
    exit /b 1
)

REM ========================
REM 变量配置区
REM ========================
:INIT
set "DAEMON_PATH=src\daemon_process.py"
set "DAEMON_NAME=DaemonProcess"
set "LOG_FILE=logs\%DAEMON_NAME%.log"
set "PID_FILE=run\%DAEMON_NAME%.pid"

if not exist logs mkdir logs
if not exist run mkdir run
goto :EOF

REM ========================
REM 启动守护进程
REM ========================
:START
call :INIT
echo Starting %DAEMON_NAME%...

REM 启动 Python 守护进程
start "" /B powershell -Command "python %DAEMON_PATH% | Out-File -FilePath %LOG_FILE% -Encoding utf8"

REM 等待 Python 进程启动几秒钟
timeout /t 3 /nobreak >nul

REM 获取最新启动的 python.exe 的 PID 并保存（仅适用于本项目下只有一个 python 守护进程的情况）
for /f "tokens=2 delims=," %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV /NH') do (
    echo %%~a > "%PID_FILE%"
    goto AfterStart
)

:AfterStart
echo %DAEMON_NAME% started.
goto :EOF




REM ========================
REM 停止守护进程
REM ========================
:STOP
call :INIT
if exist "%PID_FILE%" (
    set /p PID=<%PID_FILE%
    echo Stopping %DAEMON_NAME%...

    REM 查找并结束与日志文件相关的 PowerShell 进程
    D:\soft\tools\Handle\handle.exe "%LOG_FILE%" /accepteula > temp_handles.txt
    for /f "tokens=2 delims=," %%a in (temp_handles.txt) do (
        taskkill /PID %%a /F >nul 2>&1
    )
    del temp_handles.txt

    REM 结束 python 守护进程
    taskkill /PID !PID! /F >nul 2>&1
    del "%PID_FILE%" >nul 2>&1
    echo %DAEMON_NAME% stopped.
) else (
    echo %DAEMON_NAME% is not running.
)
goto :EOF


REM ========================
REM 查看状态
REM ========================
:STATUS
call :INIT
if exist "%PID_FILE%" (
    set /p PID=<%PID_FILE%
    if not defined PID (
        echo PID file is empty or unreadable.
        goto :EOF
    )
    echo Checking status of PID !PID!...

    tasklist /FI "PID eq !PID!" | findstr "!PID!" >nul
    if !errorlevel! == 0 (
        echo %DAEMON_NAME% is running. PID=!PID!
    ) else (
        echo %DAEMON_NAME% is not running.
    )
) else (
    echo %DAEMON_NAME% is not running.
)
goto :EOF


REM ========================
REM 重启
REM ========================
:RESTART
call :STOP
call :START
goto :EOF
