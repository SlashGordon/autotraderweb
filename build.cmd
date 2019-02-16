rem @echo off
for /f "delims=" %%A in ('npm bin') do set "NPMBIN=%%A"
SET PATH=%PATH%;%NPMBIN%
CMD /C npm install
webpack --config webpack.config.js --progress --colors
