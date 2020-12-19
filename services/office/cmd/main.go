package main

import (
	"github.com/HackerDom/ructfe2020/internal/manager"
	"github.com/HackerDom/ructfe2020/internal/server"
	"github.com/HackerDom/ructfe2020/internal/storage"
)

func main() {
	users, err := storage.NewPgUsers()
	if err != nil {
		panic(err)
	}
	err = server.RunServer(manager.New(users, nil))
	if err != nil {
		panic(err)
	}
}
