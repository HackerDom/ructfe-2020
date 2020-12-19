package manager

import (
	"github.com/HackerDom/ructfe2020/internal/storage"
)

type Manager struct {
	*users
	*documents
}

func New(usersStorage storage.Users, documentsStorage storage.Documents) *Manager {
	return &Manager{
		&users{usersStorage},
		&documents{documentsStorage, usersStorage},
	}
}
