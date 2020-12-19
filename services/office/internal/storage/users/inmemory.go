package users

import pb "github.com/HackerDom/ructfe2020/proto"

func NewInMemory() *InMemory {
	return &InMemory{users: make([]*pb.User, 0)}
}

type InMemory struct {
	users []*pb.User
}

func (u *InMemory) Insert(user *pb.User) error {
	u.users = append(u.users, user)
	return nil
}

func (u *InMemory) List() ([]*pb.User, error) {
	return u.users, nil
}
