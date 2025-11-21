此漏洞条件还是偏向于内网环境当中，python-gateway的端口是25333，此端口无法访问则无法利用。

官方认为客户环境应当是安全的，不认为是个漏洞～～

使用方式：

```
python3 python_gateway_poc.py -h

python3 python_gateway_poc.py localhost:12345
```
