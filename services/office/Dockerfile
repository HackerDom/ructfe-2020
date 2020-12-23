FROM golang:latest

ENV GO111MODULE=on

RUN mkdir /app
WORKDIR /app/

# cache modules
COPY go.mod .
COPY go.sum .
RUN go mod download

COPY . .

RUN CGOENABLED=0 go build -o service ./cmd
CMD ["/app/service"]