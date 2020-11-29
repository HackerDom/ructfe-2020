package main

import "github.com/HackerDom/ructfe2020/internal/server"

func main() {
	err := server.RunServer()
	if err != nil {
		panic(err)
	}
}
