@echo off
REM Fix corrupted aiohttp installation
echo Fixing corrupted aiohttp installation...

REM Remove corrupted aiohttp
uv pip uninstall -y aiohttp aiosignal frozenlist multidict yarl

REM Reinstall aiohttp and dependencies
uv pip install aiohttp>=3.9.0

echo Done! Try running the server again.
