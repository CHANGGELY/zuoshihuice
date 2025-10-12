@echo off
setlocal
echo 正在部署项目到Vercel...
set SCRIPT_DIR=%~dp0
pushd "%SCRIPT_DIR%..\apps\liangzhi-huice"
echo 当前目录: %cd%
echo 开始构建项目...
npm run build
if %errorlevel% neq 0 (
    echo 构建失败！
    pause
    exit /b 1
)
echo 构建成功，开始部署...
npx vercel --prod
echo 部署完成！
pause
popd
endlocal
