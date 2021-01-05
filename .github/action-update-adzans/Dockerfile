FROM python:3.8-slim

RUN pip install --no-cache-dir requests
RUN pip install --no-cache-dir lxml

COPY entrypoint /usr/local/bin/entrypoint
COPY parser.py /tmp/parser.py

RUN chmod +x /usr/local/bin/entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint"]