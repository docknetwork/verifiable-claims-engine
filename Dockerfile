FROM python:3.7
ARG DEV=1
#ENV PYTHONDONTWRITEBYTECODE=1
#ENV ETH_PUBLIC_KEY=<PLEASE CONFIGURE ME>
#ENV ETH_PRIVATE_KEY=<PLEASE CONFIGURE ME>
#ENV ETH_KEY_CREATED_AT=<PLEASE CONFIGURE ME>
#ENV ETH_NODE_URL_ROPSTEN=<PLEASE CONFIGURE ME>
#ENV ETH_NODE_URL_MAINNET=<PLEASE CONFIGURE ME>

EXPOSE 80
WORKDIR /app
CMD ["uwsgi", "uwsgi.ini"]

ADD . /app
RUN pip install -r requirements.txt
RUN if [ $DEV -eq "1" ]; then \
        pip install -r requirements-dev.txt; \
    fi

RUN cd /app/blockcerts/tools && pip install .
RUN cd /app/blockcerts/issuer && pip install . && python setup.py experimental --blockchain=ethereum

