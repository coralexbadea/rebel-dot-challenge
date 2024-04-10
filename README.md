Install dependencies:
```bash
pip install -r requirements.txt 
```
Rename .env-example file to .env and edit it for your variables

Run the app:
```bash
uvicorn app:app 
```

call 127.0.0.1:8000/ask-question endpoint with 
JSON body:
```
{
	"user_question": <Your question here>
}
```
and Bearer Token:
```
api_token_abc123
```

Try those 3 scenarios:
```
{
	"user_question": "Tell me something about the IT industry"
}
```
```
{
	"user_question": "Can I set up two-factor authentication for my account?"
}
```
```
{
	"user_question": "What is 2+2?"
}
```


## Alternatively you can run using Docker
Set your OpenAI key inside Docker-compose.yml
```
docker-compose build
```
```
docker-compose up -d
```
use ```<your-local-IP>:8000/ask-question```
