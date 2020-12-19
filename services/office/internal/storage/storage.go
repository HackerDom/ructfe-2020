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

type Documents interface {
	List() ([]*pb.Document, error)
	Insert(document *pb.Document) error
	Delete(docID string) error
	Get(name string) (*pb.Document, error)
}

var (
	dialTimeout    = 2 * time.Second
	requestTimeout = 10 * time.Second
)

