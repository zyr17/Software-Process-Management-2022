FROM node:10.24-alpine AS builder
WORKDIR /build
COPY ./ .
RUN npm install && npm run-script build

FROM nginx
COPY --from=builder /build /html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 8080
WORKDIR /html