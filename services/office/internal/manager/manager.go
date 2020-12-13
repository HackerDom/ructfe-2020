package manager

import (
	"github.com/HackerDom/ructfe2020/internal/hashutil"
	"github.com/HackerDom/ructfe2020/internal/storage"
	pb "github.com/HackerDom/ructfe2020/proto"
)

type Manager struct {
	s storage.Users
}

func New(s storage.Users) *Manager {
	return &Manager{s}
}

func (m *Manager) GetUsers() ([]string, error) {
	users, err := m.s.List()
	if err != nil {
		return make([]string, 0), err
	}
	return users, nil
}

func (m *Manager) RegisterUser(username string) (*pb.User, error) {
	d := hashutil.RandDigest(username)
	err := m.s.Register(d)
	if err != nil {
		return nil, err
	}
	return &pb.User{
		Name:  username,
		Token: d,
	}, nil
}
