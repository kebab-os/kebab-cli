cd ~
if (!(Test-Path .kebab)) { mkdir .kebab }
cd .kebab
curl.exe -L https://github.com/kebab-os/kebab-cli/archive/refs/heads/main.zip -o kebab-cli.zip
Expand-Archive -Path kebab-cli.zip -DestinationPath . -Force
cd kebab-cli-main
pip install pygame requests html2image
