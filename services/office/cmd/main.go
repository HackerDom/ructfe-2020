package main

import (
	"github.com/HackerDom/ructfe2020/internal/manager"
	"github.com/HackerDom/ructfe2020/internal/server"
	"github.com/HackerDom/ructfe2020/internal/storage"
)

func main() {
	s, err := storage.NewPgUsers()
	if err != nil {
		panic(err)
	}
	err = server.RunServer(manager.New(s))
	if err != nil {
		panic(err)
	}
}
