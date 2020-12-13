package storage

import pb "github.com/HackerDom/ructfe2020/proto"

func NewInMemoryUsers() *UsersInMemory {
	return &UsersInMemory{users: make([]string, 0)}
}

type UsersInMemory struct {
	users []string
}

func (u *UsersInMemory) Upsert(user *pb.User) error {
	u.users = append(u.users, user.Name)
	return nil
}

func (u *UsersInMemory) List() ([]string, error) {
	return u.users, nil
}
