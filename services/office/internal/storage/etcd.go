package storage

import (
	"context"
	"fmt"
	"go.etcd.io/etcd/clientv3"
)

func NewEtcdUsers() *UsersEtcd {
	return &UsersEtcd{}
}

type UsersEtcd struct {
}

func (u *UsersEtcd) Register(token string) error {
	c, err := openConn()
	if err != nil {
		return err
	}
	resp, err := c.Put(context.Background(), fmt.Sprintf("/%s", token), "val")
	if err != nil {
		return err
	}
	fmt.Println(resp)
	return nil
}

func (u *UsersEtcd) List() ([]string, error) {
	c, err := openConn()
	if err != nil {
		return nil, err
	}
	resp, err := c.Do(context.Background(), clientv3.OpGet("/users"))
	if err != nil {
		return nil, err
	}
	users := make([]string, resp.Get().Count)
	for i, kv := range resp.Get().Kvs {
		users[i] = string(kv.Value)
	}
	return users, nil
}

func openConn() (*clientv3.Client, error) {
	conn, err := clientv3.New(clientv3.Config{
		Endpoints: []string{"localhost:2379", "localhost:22379", "localhost:32379"},
	})
	return conn, err
}
