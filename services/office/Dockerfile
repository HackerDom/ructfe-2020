FROM golang:latest
RUN mkdir /app
ADD . /app/
WORKDIR /app/cmd
RUN go build -o main .
CMD ["/app/cmd/main"]