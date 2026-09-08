FROM ghcr.io/astral-sh/uv:latest AS uv_bin

FROM python:3.13
WORKDIR /usr/local/app

COPY --from=uv_bin /uv /uvx /bin/

# Install the application dependencies
COPY pyproject.toml uv.lock ./
RUN uv pip install --system -r pyproject.toml


# Copy in the source code
COPY src ./src
COPY scripts/load_electricity_data.py ./
COPY data ./data
COPY dashboard.py .
COPY .streamlit ./.streamlit

# set environment variables
ENV ORACLE_PASSWORD="${ORACLE_PASSWORD}"
ENV ORACLE_USER="${ORACLE_USER}"
ENV WALLET_LOCATION="wallet"
ENV ORACLE_DSN="${ORACLE_DSN}"
ENV ENTSOE_API_KEY="${ENTSOE_API_KEY}"
ENV COUNTRY_CODE="${COUNTRY_CODE}"
ENV WALLET_ENCRIPTING_PASSWORD="${WALLET_ENCRIPTING_PASSWORD}"