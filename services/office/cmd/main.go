package main

import (
	"github.com/HackerDom/ructfe2020/internal/manager"
	"github.com/HackerDom/ructfe2020/internal/server"
	"github.com/HackerDom/ructfe2020/internal/storage/docs"
	"github.com/HackerDom/ructfe2020/internal/storage/users"
)

func main() {
	usersStorage := users.NewInMemory()
	docsStorage := docs.NewInMemory()
	err := server.RunServer(manager.New(usersStorage, docsStorage))
	if err != nil {
		panic(err)
	}
}
