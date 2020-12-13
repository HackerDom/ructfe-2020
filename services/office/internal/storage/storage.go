package storage

import (
	"time"
)

const (
	Addr = "[::]"
	Port = "2379"
)

type Users interface {
	List() ([]string, error)
	Register(string) error
}

var (
	dialTimeout    = 2 * time.Second
	requestTimeout = 10 * time.Second
)

