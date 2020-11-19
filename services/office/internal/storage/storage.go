package storage

import (
	"context"
	"fmt"
	"github.com/coreos/etcd/clientv3"
	"time"
)

const (
	Addr = "[::]"
	Port = "2379"
)

var (
	dialTimeout    = 2 * time.Second
	requestTimeout = 10 * time.Second
)

func Open() clientv3.KV {
	_, cancel := context.WithTimeout(context.Background(), requestTimeout)
	defer cancel()
	cli, _ := clientv3.New(clientv3.Config{
		DialTimeout: dialTimeout,
		Endpoints:   []string{fmt.Sprintf("%s:%s", Addr, Port)},
	})
	defer func() { _ = cli.Close() }()
	return clientv3.NewKV(cli)
}
