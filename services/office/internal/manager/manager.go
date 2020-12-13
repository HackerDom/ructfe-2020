package manager

import (
	"github.com/HackerDom/ructfe2020/internal/hashutil"
	"github.com/HackerDom/ructfe2020/internal/storage"
	pb "github.com/HackerDom/ructfe2020/proto"
)

type Manager struct {
	*users
}

func New(s storage.Users) *Manager {
	return &Manager{&users{s}}
}

type users struct {
	s storage.Users
}

func (m *users) GetUsers() ([]*pb.User, error) {
	users, err := m.s.List()
	if err != nil {
		return nil, err
	}
	return users, nil
}

func (m *users) GetNames() ([]string, error) {
	users, err := m.s.List()
	if err != nil {
		return nil, err
	}
	names := make([]string, len(users))
	for i, user := range users {
		names[i] = user.Name
	}
	return names, nil
}

func (m *users) RegisterUser(username string) (*pb.User, error) {
	d := hashutil.RandDigest(username)
	user := &pb.User{
		Name:  username,
		Token: d,
	}
	err := m.s.Insert(user)
	if err != nil {
		return nil, err
	}
	return &pb.User{
		Name:  username,
		Token: d,
	}, nil
}
