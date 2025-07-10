ARG BUILD_ENV=production

ARG OKTA_DOMAIN
ARG OKTA_CLIENT_ID
ARG OKTA_LOGIN_REDIRECT
ARG API_URL

FROM node:22-alpine AS base_image

FROM base_image AS development_builder

ONBUILD COPY ./.certs/netskope-cert-bundle.pem /etc/ssl/certs/netskope-cert-bundle.pem
ONBUILD ENV SSL_CERT_FILE=/etc/ssl/certs/netskope-cert-bundle.pem
ONBUILD ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/netskope-cert-bundle.pem
ONBUILD ENV CURL_CA_BUNDLE=/etc/ssl/certs/netskope-cert-bundle.pem
ONBUILD ENV NODE_EXTRA_CA_CERTS=/etc/ssl/certs/netskope-cert-bundle.pem

FROM base_image AS production_builder

FROM ${BUILD_ENV}_builder AS builder
ARG OKTA_DOMAIN
ARG OKTA_CLIENT_ID
ARG OKTA_LOGIN_REDIRECT
ARG API_URL
ENV VITE_OKTA_DOMAIN=${OKTA_DOMAIN}
ENV VITE_OKTA_CLIENT_ID=${OKTA_CLIENT_ID}
ENV VITE_OKTA_LOGIN_REDIRECT=${OKTA_LOGIN_REDIRECT}
ENV VITE_API_URL=${API_URL}
WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .
RUN yarn build


FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 5173
CMD ["nginx", "-g", "daemon off;"]