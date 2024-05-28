FROM public.ecr.aws/lambda/python:3.10

COPY app.py requirements.txt ./
COPY lib ./lib

RUN python3.10 -m pip install -r requirements.txt -t .

CMD ["app.lambda_handler"]
