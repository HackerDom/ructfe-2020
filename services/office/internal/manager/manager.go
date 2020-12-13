package manager

import (
	"fmt"
	"github.com/HackerDom/ructfe2020/internal/hashutil"
	"github.com/HackerDom/ructfe2020/internal/storage"
)

type Manager struct {
	s storage.Users
}

func New(s storage.Users) *Manager {
	return &Manager{s}
}

func (m *Manager) GetUsers() []string {
	users, err := m.s.List()
	if err != nil {
		fmt.Println(err)
		return make([]string, 0)
	}
	return users
}

func (m *Manager) RegisterUser(username string) string {
	d := hashutil.RandDigest(username)
	err := m.s.Register(d)
	if err != nil {
		fmt.Println(err)
	}
	return d
}