package storage

import (
	pb "github.com/HackerDom/ructfe2020/proto"
	"time"
)

const (
	Addr = "[::]"
	Port = "2379"
)

type Users interface {
	List() ([]*pb.User, error)
	Insert(user *pb.User) error
}

var (
	dialTimeout    = 2 * time.Second
	requestTimeout = 10 * time.Second
)

