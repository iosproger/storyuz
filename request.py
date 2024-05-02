import requests

url = "http://127.0.0.1:5000/history"

productnames = ['test', 'test1']
date = '2024-04-30'
userid = 'user1'
prices = [200,300]
quantity = [1,3]

payload = {'productnames': productnames , 'date':date , 'userid':userid ,'prices':prices ,'quantity':quantity  }
headers = {'Content-Type': 'application/json'}

response = requests.put(url, json=payload, headers=headers)

print(response.text)
