import requests

url = "http://127.0.0.1:5000/history"

productnames = ['test', 'test1','test2']
date = '2024-04-30'
userid = 'user1'
prices = [200,300,100]

payload = {'productnames': productnames , 'date':date , 'userid':userid ,'prices':prices }
headers = {'Content-Type': 'application/json'}

response = requests.put(url, json=payload, headers=headers)

print(response.text)
