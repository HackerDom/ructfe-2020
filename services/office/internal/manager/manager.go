package manager

import (
	userstorage "github.com/HackerDom/ructfe2020/internal/storage/users"
	"github.com/HackerDom/ructfe2020/internal/storage/docs"
)

type Manager struct {
	*users
	*documents
}

func New(usersStorage userstorage.Users, documentsStorage docs.Documents) *Manager {
	return &Manager{
		&users{usersStorage},
		&documents{documentsStorage, usersStorage},
	}
}
