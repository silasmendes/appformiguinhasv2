```
$env:PLAYWRIGHT_HEADLESS = "0"
$env:PLAYWRIGHT_SLOW_MO = "300"      # optional, slows actions so you can watch
# optional inspector:
# $env:PWDEBUG = "1"

py -m pytest tests/test_playwright_atendimento.py -k fluxo_atendimento_end_to_end -vv
```
