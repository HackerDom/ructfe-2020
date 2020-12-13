package main

import (
	"github.com/HackerDom/ructfe2020/internal/manager"
	"github.com/HackerDom/ructfe2020/internal/server"
	"github.com/HackerDom/ructfe2020/internal/storage"
)

func main() {
	err := server.RunServer(manager.New(storage.NewEtcdUsers()))
	if err != nil {
		panic(err)
	}
}
