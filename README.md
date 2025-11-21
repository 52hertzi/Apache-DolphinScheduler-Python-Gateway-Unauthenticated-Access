此漏洞条件还是偏向于内网环境当中，python-gateway的端口是25333，此端口无法访问则无法利用。

官方认为客户环境应当是安全的，不认为是个漏洞～～

分析：
https://52hertzi.com/2025/11/18/Apache-DolphinScheduler-Python-Gateway-未授权访问漏洞分析与复现/

使用方式：

```
python3 python_gateway_poc.py -h

python3 python_gateway_poc.py localhost:12345
```
