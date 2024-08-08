import requests
import json

url = "http://localhost:8000/print"

payload = json.dumps({
  "products": [
    {
      "name": "لته",
      "quantity": 1,
      "price": 80
    }
  ],
  "total": 80,
  "table": 12,
  "factor": 1
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
