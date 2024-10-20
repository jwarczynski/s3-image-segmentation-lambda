ARG PYTHON_VERSION=3.11
FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}

COPY requirements.txt ./

# Install the specified packages
RUN python -m pip install --no-cache-dir -r requirements.txt --target ${LAMBDA_TASK_ROOT} && \
    rm -rf /root/.cache/pip

#RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
#    && rm -rf /root/.cache/pip

COPY download_weights.py ${LAMBDA_TASK_ROOT}

RUN python ${LAMBDA_TASK_ROOT}/download_weights.py

# Copy function code
COPY src/ ${LAMBDA_TASK_ROOT}/

EXPOSE 8080

CMD ["lambda_function.lambda_handler"]
