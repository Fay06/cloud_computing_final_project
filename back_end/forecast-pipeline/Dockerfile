FROM public.ecr.aws/lambda/python:3.10-x86_64

COPY requirements.txt ./

RUN  pip3 install -r requirements.txt

COPY lambda_function.py ./

CMD ["lambda_function.lambda_handler"]
